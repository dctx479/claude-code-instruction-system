"""Shared isolated CLI evaluation mechanics; no personal config is copied."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def environment(config):
    env = dict(os.environ, CLAUDE_CONFIG_DIR=str(config), PYTHONIOENCODING="utf-8")
    personal = Path.home() / ".claude/settings.json"
    if personal.is_file():
        values = json.loads(personal.read_text(encoding="utf-8-sig")).get("env", {})
        env.update({k: str(v) for k, v in values.items() if k.startswith("ANTHROPIC_")})
    return env


def install(config, profile="core", components="core,skills,commands,knowledge"):
    result = subprocess.run([sys.executable, str(ROOT / "scripts/install-global.py"), "--target", str(config),
                             "--profile", profile, "--components", components], capture_output=True,
                            text=True, encoding="utf-8", timeout=90)
    if result.returncode:
        raise RuntimeError("isolated install failed: " + result.stderr[-1200:])


def parse_events(stdout):
    events, calls, final, results = [], [], {}, {}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        events.append(event)
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    calls.append(dict(id=block.get("id"), tool=block.get("name"), input=block.get("input", {})))
        if event.get("type") == "user":
            for block in event.get("message", {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    results[block.get("tool_use_id")] = dict(error=bool(block.get("is_error")), content=block.get("content"))
        if event.get("type") == "result":
            final = event
    for call in calls:
        call["result"] = results.get(call["id"])
    return events, calls, final


def invoke(project, config, prompt, tools="Read,Edit,Write,Bash,Glob,Grep,Skill", turns=20, budget="0.50", timeout=180, mode=None):
    cli = shutil.which("claude")
    if not cli:
        raise RuntimeError("Claude CLI unavailable")
    command = [cli, "-p", prompt, "--settings", str(config / "settings.json"), "--tools", tools,
               "--no-session-persistence", "--output-format", "stream-json", "--verbose",
               "--max-turns", str(turns), "--max-budget-usd", str(budget)]
    if mode:
        command.extend(["--permission-mode", mode])
    timed_out = False
    try:
        process = subprocess.run(command, cwd=project, env=environment(config), capture_output=True,
                                 text=True, encoding="utf-8", timeout=timeout)
        output, error, code = process.stdout, process.stderr, process.returncode
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        error, code, timed_out = "evaluation timeout", 124, True
    events, calls, final = parse_events(output)
    return dict(exit=code, timeout=timed_out, calls=calls, final=final, events=events,
                diagnostic=error[-1200:], completed=bool(final) and not final.get("is_error") and code == 0)


def persist(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)
