#!/usr/bin/env python3
"""Standard-library statusline. Parse once, gather lazily, never infer missing metrics."""
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import unicodedata

# Cache keys use the same SHA-256 algorithm without loading OpenSSL on CPython.
try:
    from _sha2 import sha256
except ImportError:
    try:
        from _sha256 import sha256
    except ImportError:
        from hashlib import sha256

VERSION = "2.1.0"
NAMES = ("time", "model", "project", "git", "context", "cost", "agent", "task", "progress", "ralph", "tokens", "performance")
PRIORITY = {name: 1 if name in {"model", "project", "git", "context"} else
            3 if name in {"ralph", "tokens", "performance"} else 2 for name in NAMES}
THEMES = {"default": ("|", "#", ".", "✓", "*"), "minimal": ("|", "=", "-", "✓", "●"),
          "unicode": ("│", "█", "░", "✓", "●"), "nerd": ("┃", "█", "▒", "✓", "●")}
COLORS = {"dim": "2", "red": "31", "green": "32", "yellow": "33", "blue": "34", "magenta": "35", "cyan": "36", "white": "37"}
COLORS.update({"bright_red": "91", "bright_green": "92", "bright_yellow": "93", "bright_blue": "94",
               "bright_magenta": "95", "bright_cyan": "96", "bright_white": "97"})
ANSI = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")


def warning(message):
    print(f"WARNING: HUD {message}", file=sys.stderr)


def safe(text):
    text = ANSI.sub("", str(text))
    return "".join(" " if c in "\n\r\t" else c for c in text
                   if c in "\n\r\t" or unicodedata.category(c) not in {"Cc", "Cf"})


def cells(text):
    return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in {"W", "F"} else 1 for c in text)


def trim(text, maximum):
    if cells(text) <= maximum:
        return text
    if maximum <= 0:
        return ""
    used, result = 0, ""
    for character in text:
        size = cells(character)
        if used + size > maximum - 1:
            break
        result += character
        used += size
    return result + "…"


def number(value):
    return value if type(value) in {int, float} and math.isfinite(value) and value >= 0 else None


def obj(value):
    return value if isinstance(value, dict) else {}


def read_json(path):
    if not path.exists():
        return None
    if path.stat().st_size > 1024 * 1024:
        raise ValueError("JSON file exceeds 1 MiB")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("JSON object required")
    return data


def normalized(path):
    value = str(path)
    if os.name == "nt":
        value = re.sub(r"^/([a-zA-Z])/", lambda m: m[1].upper() + ":/", value)
    return os.path.normcase(str(Path(value).resolve()))


def native_path(value):
    text = str(value)
    if os.name == "nt":
        text = re.sub(r"^/([a-zA-Z])/", lambda m: m[1].upper() + ":/", text)
    return Path(text)


class Renderer:
    def __init__(self, data, config=None, env=None, cwd=None, theme=None):
        self.data = data
        self.env = os.environ if env is None else env
        self.home = native_path(self.env.get("HOME") or Path.home())
        self.config_file = native_path(self.env.get("HUD_CONFIG_FILE") or self.home / ".claude/hud-config.json")
        if config is None:
            try:
                config = read_json(self.config_file) or {}
            except (OSError, ValueError, RecursionError):
                warning("configuration unavailable; using defaults")
                config = {}
        self.config = config
        workspace = obj(data.get("workspace"))
        self.cwd = native_path(workspace.get("current_dir") or data.get("cwd") or cwd or os.getcwd()).resolve()
        self.project = native_path(workspace.get("project_dir") or self.env.get("CLAUDE_PROJECT_DIR") or self.cwd).resolve()
        selected = theme or self.env.get("HUD_THEME") or config.get("theme", "default")
        if selected not in THEMES:
            warning("unknown theme; using default")
            selected = "default"
        self.theme = THEMES[selected]
        self.separator = self.theme[0] if theme or self.env.get("HUD_THEME") else safe(self.get("display.separator", self.theme[0]))[:8]
        width = self.env.get("HUD_WIDTH") or self.get("width", "auto")
        terminal = self.env.get("COLUMNS", "80")
        terminal = int(terminal) if str(terminal).isdigit() and int(terminal) > 0 else 80
        if width == "auto":
            self.width = max(1, terminal - 4)
        elif str(width).isdigit() and int(width) > 0:
            self.width = min(int(width), max(1, terminal - 4)) if "COLUMNS" in self.env else min(int(width), 1000)
        else:
            warning("invalid width; using terminal width")
            self.width = max(1, terminal - 4)
        self.cache_dir = native_path(self.env.get("HUD_CACHE_DIR") or self.home / ".claude/cache")
        budget = number(self.get("performance.max_execution_time", 100))
        self.deadline = time.monotonic() + (budget if budget is not None else 100) / 1000
        self.color_enabled = self.get("colors.enabled", True) is True and "NO_COLOR" not in self.env

    def get(self, key, default=None):
        value = self.config
        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        return value

    def state(self, path):
        try:
            return read_json(path)
        except (OSError, ValueError, RecursionError):
            warning("state unavailable; segment omitted")
            return None

    def scoped(self, state, require_session=False, require_owner=False):
        if not state:
            return False
        session = self.data.get("session_id")
        if require_session and (not session or state.get("session_id") != session):
            return False
        if state.get("session_id") and state["session_id"] != session:
            return False
        owner = state.get("project_dir") or state.get("cwd")
        if require_owner and not isinstance(owner, str):
            return False
        return not owner or (isinstance(owner, str) and normalized(owner) == normalized(self.project))

    def agent(self):
        explicit = self.env.get("CLAUDE_AGENT")
        prefix = safe(self.get("modules.agent.prefix", "@"))
        if explicit:
            return prefix + safe(explicit)
        local = self.state(self.project / ".claude/agent-state.json")
        if self.scoped(local, require_session=True, require_owner=True) and local.get("current_agent"):
            return prefix + safe(local["current_agent"])
        session = self.data.get("session_id")
        raw_cwd = obj(self.data.get("workspace")).get("current_dir") or self.data.get("cwd")
        if session and isinstance(raw_cwd, str):
            key = sha256((raw_cwd + "\0" + session).encode()).hexdigest()
            state = self.state(self.home / ".claude/intent-sessions" / (key + ".json"))
            # Intent records carry the working directory, not the launch root.
            if state and state.get("session_id") == session and isinstance(state.get("cwd"), str) and normalized(state["cwd"]) == normalized(self.cwd):
                if state.get("agent"):
                    return prefix + safe(state["agent"])
                if state.get("skill"):
                    return "/" + safe(state["skill"])
        return ""

    def ralph(self):
        local = self.state(self.project / "memory/ralph-state.json")
        state = local if local is not None else self.state(self.home / ".claude/ralph-state.json")
        if not self.scoped(state, require_owner=local is None) or state.get("active") is not True:
            return ""
        current, maximum = state.get("iteration"), state.get("max_iterations")
        if type(current) is not int or type(maximum) is not int or current < 0 or maximum < 1:
            warning("Ralph counters invalid; segment omitted")
            return ""
        return safe(self.get("modules.ralph.prefix", "R:")) + f"{current}/{maximum}"

    def git(self):
        key = sha256(normalized(self.cwd).encode()).hexdigest()
        path = self.cache_dir / ("taiyi-hud-git-" + key + ".json")
        cached = None
        use_cache = self.get("cache.enabled", True) is True
        ttl = number(self.get("cache.git_ttl", 5))
        if ttl is None:
            warning("invalid Git TTL; using 5 seconds")
            ttl = 5
        if use_cache:
            try:
                cached = read_json(path)
                if cached is not None and (cached.get("version") != 1 or cached.get("cwd") != normalized(self.cwd) or
                                           number(cached.get("ts")) is None or not isinstance(cached.get("git"), dict)):
                    raise ValueError("invalid cache schema")
                if cached is not None:
                    information = cached["git"]
                    if (not isinstance(information.get("branch"), str) or not isinstance(information.get("oid"), str) or
                            type(information.get("dirty")) is not bool or type(information.get("ahead")) is not int or
                            type(information.get("behind")) is not int or information["ahead"] < 0 or information["behind"] < 0):
                        raise ValueError("invalid Git cache fields")
                if cached and 0 <= time.time() - cached["ts"] < ttl:
                    return self.git_text(cached["git"])
            except (OSError, ValueError, RecursionError):
                warning("Git cache invalid; refreshing")
                cached = None
        budget = self.deadline - time.monotonic()
        if budget <= 0:
            warning("Git collection budget exhausted; segment unknown")
            return "GIT:?"
        import subprocess
        try:
            process = subprocess.run(["git", "-C", str(self.cwd), "status", "--porcelain=v2", "--branch", "--untracked-files=normal"],
                                     env=dict(self.env, GIT_OPTIONAL_LOCKS="0"), capture_output=True, text=True,
                                     encoding="utf-8", errors="replace", timeout=budget)
            if process.returncode:
                if "not a git repository" in process.stderr.lower():
                    return ""
                raise ValueError("git status failed")
            information = dict(branch="", oid="", dirty=False, ahead=0, behind=0)
            for line in process.stdout.splitlines():
                if line.startswith("# branch.head "):
                    information["branch"] = line[14:]
                elif line.startswith("# branch.oid "):
                    information["oid"] = line[13:]
                elif line.startswith("# branch.ab "):
                    match = re.fullmatch(r"# branch.ab \+(\d+) -(\d+)", line)
                    if match:
                        information.update(ahead=int(match[1]), behind=int(match[2]))
                elif line.startswith(("1 ", "2 ", "u ", "? ")):
                    information["dirty"] = True
            if use_cache:
                try:
                    self.cache_dir.mkdir(parents=True, exist_ok=True)
                    import tempfile
                    temporary = None
                    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.cache_dir, suffix=".tmp", delete=False) as stream:
                        temporary = Path(stream.name)
                        json.dump(dict(owner="taiyi-hud", version=1, cwd=normalized(self.cwd), ts=time.time(), git=information), stream)
                    try:
                        if path.is_symlink():
                            warning("linked cache entry preserved; refreshed data not cached")
                        else:
                            os.replace(temporary, path)
                    finally:
                        if temporary.exists():
                            temporary.unlink()
                except OSError:
                    warning("Git cache could not be written")
            return self.git_text(information)
        except (OSError, ValueError, subprocess.SubprocessError):
            warning("Git unavailable or timed out; segment unknown")
            return "GIT:?"

    def git_text(self, information):
        self.git_dirty = information.get("dirty") is True
        branch = information.get("branch", "")
        if branch == "(detached)":
            branch = information.get("oid", "")[:7] + "(detached)"
        parts = [safe(branch)] if self.get("modules.git.show_branch", True) is True else []
        if self.get("modules.git.show_status", True) is True:
            parts.append(self.theme[4] if information.get("dirty") else self.theme[3])
        if self.get("modules.git.show_ahead_behind", True) is True:
            for field, marker in (("ahead", "↑"), ("behind", "↓")):
                value = information.get(field)
                if number(value) and value > 0:
                    parts.append(marker + str(value))
        return " ".join(parts)

    def metric(self, name):
        context, cost = obj(self.data.get("context_window")), obj(self.data.get("cost"))
        if name == "context":
            percentage = number(context.get("used_percentage"))
            if percentage is None:
                usage = obj(context.get("current_usage"))
                size = number(context.get("context_window_size"))
                counts = [number(usage.get(k)) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")]
                if size and counts[0] is not None:
                    percentage = sum(value or 0 for value in counts) * 100 / size
            return "CTX:?" if percentage is None else f"CTX:{min(100, percentage):.0f}%"
        if name == "cost":
            value = number(cost.get("total_cost_usd"))
            return "$?" if value is None else f"${value:.3f}"
        if name == "tokens":
            usage = obj(context.get("current_usage"))
            incoming, outgoing = number(context.get("total_input_tokens")), number(context.get("total_output_tokens"))
            if incoming is None and number(usage.get("input_tokens")) is not None:
                incoming = sum(number(usage.get(k)) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            if outgoing is None:
                outgoing = number(usage.get("output_tokens"))
            def format_count(value):
                if value is None:
                    return "?"
                if self.get("modules.tokens.format", "compact") == "compact":
                    if value >= 1000000:
                        return f"{value / 1000000:.1f}M"
                    if value >= 1000:
                        return f"{value / 1000:.1f}K"
                return str(int(value))
            return format_count(incoming) + "i/" + format_count(outgoing) + "o"
        return ""

    def segment(self, name):
        if name == "model":
            model = obj(self.data.get("model"))
            candidates = [model.get("id")] if self.get("modules.model.show_full_name", False) is True else []
            candidates += [model.get("display_name"), model.get("id"), self.env.get("CLAUDE_MODEL"), "Claude"]
            value = ""
            for candidate in candidates:
                if candidate is None:
                    continue
                if not isinstance(candidate, str):
                    raise ValueError("model name must be a string")
                value = safe(candidate).strip()
                if value:
                    break
            if self.get("modules.model.show_full_name", False) is not True and (
                    value == safe(model.get("id", "")).strip() or not re.search(r"\d", value)):
                match = re.search(r"claude-(opus|sonnet|haiku)-(\d+)-(\d+)", str(model.get("id", "")))
                if match:
                    value = f"{match[1].capitalize()} {match[2]}.{match[3]}"
            return safe(value)
        if name == "project":
            maximum = number(self.get("modules.project.max_length", 30))
            return trim(safe(self.cwd.name), int(maximum) if maximum else 30)
        if name in {"context", "cost", "tokens"}:
            return self.metric(name)
        if name in {"agent", "ralph", "git"}:
            if name == "git" and not any(self.get("modules.git." + option, True) is True
                                         for option in ("show_branch", "show_status", "show_ahead_behind")):
                return ""
            return getattr(self, name)()
        if name == "time":
            format_time = safe(self.get("modules.time.format", "HH:MM:SS"))
            return datetime.now().strftime(format_time.replace("HH", "%H").replace("MM", "%M").replace("SS", "%S"))
        if name == "task":
            value = safe(self.env.get("CLAUDE_TASK", ""))
            maximum = number(self.get("modules.task.max_length", 20))
            return trim(value, int(maximum) if maximum else 20) if self.get("modules.task.truncate", True) is True else value
        if name == "progress":
            raw = self.env.get("CLAUDE_PROGRESS")
            try:
                value = number(float(raw)) if raw is not None else None
            except ValueError:
                value = None
                warning("invalid progress; segment omitted")
            if value is None:
                return ""
            value = min(100, value)
            size = number(self.get("modules.progress.bar_width", 10))
            size = max(1, min(50, int(size or 10)))
            filled = int(value * size / 100)
            return "[" + self.theme[1] * filled + self.theme[2] * (size - filled) + "]" + (f" {value:.0f}%" if self.get("modules.progress.show_percentage", True) is True else "")
        if name == "performance":
            performance = obj(self.data.get("performance"))
            parts = []
            response = number(performance.get("response_time_ms"))
            success = number(performance.get("success_rate"))
            if response is not None and self.get("modules.performance.show_response_time", True) is True:
                parts.append(f"{response:.0f}ms")
            if success is not None and self.get("modules.performance.show_success_rate", False) is True:
                parts.append(f"{min(1, success):.0%}")
            return " ".join(parts)
        return ""

    def colored(self, name, text):
        color = self.get("colors." + name, {"project": "white", "agent": "green", "task": "yellow", "ralph": "cyan"}.get(name, "dim"))
        if name == "git":
            dirty = getattr(self, "git_dirty", False)
            color = self.get("colors.git_dirty" if dirty else "colors.git_clean", "yellow" if dirty else "green") if text != "GIT:?" else "yellow"
        if name == "model":
            family = next((family for family in ("opus", "sonnet", "haiku") if family in text.lower()), None)
            color = self.get("colors.model_" + family, {"opus": "magenta", "sonnet": "blue", "haiku": "cyan"}[family]) if family else "white"
        if name == "context":
            match = re.fullmatch(r"CTX:(\d+)%", text)
            if match:
                percentage = int(match[1])
                critical = number(self.get("modules.context.critical_threshold", 90))
                warn = number(self.get("modules.context.warn_threshold", 80))
                key = "critical" if percentage >= (critical if critical is not None else 90) else "warn" if percentage >= (warn if warn is not None else 80) else "good"
                color = self.get("colors.context_" + key, {"critical": "red", "warn": "yellow", "good": "green"}[key])
        if not self.color_enabled or color not in COLORS:
            return text
        if name == "model" and self.get("modules.model.high_contrast", True) is True:
            return f"\033[1;{COLORS['bright_white']}m{text}\033[0m"
        return f"\033[{COLORS[color]}m{text}\033[0m"

    def render(self):
        if self.get("display.hide_zero_cost", False) is True and not number(obj(self.data.get("cost")).get("total_cost_usd")):
            return ""
        adaptive = self.get("display.adaptive_width", True) is True
        threshold = number(self.get("display.priority_threshold", 2))
        threshold = min(3, int(threshold if threshold is not None else 2))
        maximum = 3 if self.width >= 120 or not adaptive else threshold
        selected, length = [], 0
        joiner = " " + self.separator + " "
        allowed = []
        for index, name in enumerate(NAMES):
            if self.get(f"modules.{name}.enabled", name != "performance") is not True:
                continue
            priority = number(self.get(f"modules.{name}.priority", PRIORITY[name]))
            priority = int(priority) if priority is not None else PRIORITY[name]
            if priority <= maximum:
                allowed.append((priority, index, name))
        for priority, index, name in sorted(allowed):
            remaining = self.width - length - (cells(joiner) if selected else 0)
            if adaptive and priority > 1 and remaining < 5:
                continue
            text = safe(self.segment(name))
            if not text:
                continue
            if adaptive and priority > 1 and cells(text) > remaining:
                continue
            selected.append((index, name, text))
            length += cells(text) + (cells(joiner) if len(selected) > 1 else 0)
        if adaptive and length > self.width:
            # Shrink descriptive labels before clipping current metrics.
            for shortened in ("project", "git"):
                for position, (index, name, text) in enumerate(selected):
                    if name == shortened:
                        target = max(3, cells(text) - (length - self.width))
                        clipped = trim(text, target)
                        length -= cells(text) - cells(clipped)
                        selected[position] = (index, name, clipped)
                        break
                if length <= self.width:
                    break
            # Keep the model identifiable before sacrificing it to labels.
            for dropped in ("project", "git", "time", "cost", "agent", "task", "progress", "ralph", "tokens", "performance"):
                if length <= self.width:
                    break
                selected = [item for item in selected if item[1] != dropped]
                length = sum(cells(item[2]) for item in selected) + max(0, len(selected) - 1) * cells(joiner)
        ordered = sorted(selected)
        # Clip plain segments before applying ANSI, so escapes are never truncated.
        result, used = [], 0
        for _, name, text in ordered:
            room = self.width - used - (cells(joiner) if result else 0)
            if adaptive:
                text = trim(text, room)
            if not text:
                break
            used += cells(text) + (cells(joiner) if result else 0)
            result.append(self.colored(name, text))
        return joiner.join(result)


def main():
    arguments = sys.argv[1:]
    action = arguments[0] if arguments else "render"
    if action in {"-h", "--help"}:
        action = "help"
    if action not in {"render", "full", "theme", "config", "cache-clear", "version", "help"} or len(arguments) > (2 if action == "theme" else 1):
        warning("unknown command or extra arguments")
        return 2
    theme = arguments[1] if len(arguments) == 2 else "default" if action == "theme" else None
    if action == "version":
        print(f"HUD Statusline v{VERSION}")
        return 0
    if action == "help":
        print("Usage: hud.sh [render|full|theme NAME|config|cache-clear|version|help]\n"
              "Environment: HUD_CONFIG_FILE, HUD_CACHE_DIR, HUD_THEME, HUD_WIDTH, HUD_SESSION_JSON")
        return 0
    if action in {"config", "cache-clear"}:
        renderer = Renderer({})
        if action == "config":
            print(json.dumps(renderer.config, ensure_ascii=False, indent=2))
            return 0
        count = 0
        for path in renderer.cache_dir.glob("taiyi-hud-git-*.json"):
            if not re.fullmatch(r"taiyi-hud-git-[a-f0-9]{64}\.json", path.name) or path.is_symlink() or not path.is_file():
                warning("unowned/linked cache entry preserved")
                continue
            try:
                entry = read_json(path)
                if not entry or entry.get("owner") != "taiyi-hud" or entry.get("version") != 1:
                    warning("cache entry without ownership marker preserved")
                    continue
            except (OSError, ValueError, RecursionError):
                warning("unverifiable cache entry preserved")
                continue
            path.unlink()
            count += 1
        print(f"Cache cleared: {count} HUD entries")
        return 0
    raw = "" if sys.stdin.isatty() else sys.stdin.read(1024 * 1024 + 1)
    raw = raw or os.environ.get("HUD_SESSION_JSON", "")
    try:
        data = json.loads(raw) if raw.strip() else {}
        if len(raw) > 1024 * 1024 or not isinstance(data, dict):
            raise ValueError("invalid payload")
        renderer = Renderer(data, theme=theme)
        content = renderer.render()
        if action == "full":
            print("-" * renderer.width)
        if content:
            print(content)
        if action == "full":
            print("-" * renderer.width)
        return 0
    except (ValueError, TypeError, OSError, RecursionError, KeyError, AttributeError):
        warning("input/rendering invalid; metrics unavailable")
        print("HUD unavailable")
        return 1


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError, RecursionError):
        warning("operation failed")
        sys.exit(1)
