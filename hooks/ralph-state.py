#!/usr/bin/env python3
"""Ralph Stop state transitions. Exit 2 only after a successful state write."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time


def normalized(path):
    text = str(path)
    if os.name == "nt":
        text = re.sub(r"^/([A-Za-z])/", lambda m: m[1].upper() + ":/", text)
    return os.path.normcase(os.path.abspath(text))


def save_state(path, data):
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
            name = stream.name
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(name, path)
    finally:
        if name and Path(name).exists():
            Path(name).unlink()


def transition(state, event, project, is_global, default_max=10):
    """Return decision and new state, without mutating input or doing I/O."""
    if not isinstance(state, dict) or type(state.get("active")) is not bool:
        raise ValueError("state.active must be a boolean")
    if not state["active"]:
        return "inactive", None
    owner = state.get("project_dir")
    if is_global and not owner:
        raise ValueError("global Ralph state has no project_dir; refusing to intercept other projects")
    if owner:
        if not isinstance(owner, str):
            raise ValueError("project_dir must be a string")
        if normalized(owner) != normalized(project):
            return "other-project", None
    session = state.get("session_id")
    if session and (not isinstance(session, str) or session != event.get("session_id")):
        return "other-session", None
    for name in ("completed", "fatal_error", "round_complete", "needs_confirmation"):
        if name in state and type(state[name]) is not bool:
            raise ValueError(f"{name} must be a boolean")
    current, maximum = state.get("iteration", 0), state.get("max_iterations", default_max)
    if type(current) is not int or current < 0 or type(maximum) is not int or maximum < 1:
        raise ValueError("iteration/max_iterations must be nonnegative/positive integers")
    # Copy nested values too, so failed validation/writes never mutate the caller.
    data = json.loads(json.dumps(state))
    data.setdefault("iteration", current)
    data.setdefault("max_iterations", maximum)
    metrics = data.setdefault("metrics", {})
    if not isinstance(metrics, dict):
        raise ValueError("metrics must be an object")

    def increment(key):
        value = metrics.get(key, 0)
        if type(value) is not int or value < 0:
            raise ValueError(f"metrics.{key} must be a nonnegative integer")
        metrics[key] = value + 1

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    data["last_updated"] = now
    if data.get("completed"):
        data.update(active=False, status="COMPLETED")
        increment("successful_runs")
        decision = "completed"
    elif data.get("fatal_error"):
        data.update(active=False, status="FAILED")
        increment("failed_runs")
        decision = "fatal"
    elif current >= maximum or (data.get("round_complete") and current + 1 >= maximum):
        # iteration is zero-based: finishing round max-1 exhausts the budget.
        # Do not emit exit 2 and let the model start an extra round first.
        if current < maximum:
            data["iteration"] = current + 1
        data.update(active=False, status="FAILED", max_iterations_reached=True)
        increment("failed_runs")
        decision = "max"
    elif data.get("needs_confirmation"):
        data.update(status="PAUSED", paused_at=now)
        decision = "paused"
    elif data.get("round_complete"):
        data.update(iteration=current + 1, round_complete=False, status="RUNNING")
        increment("total_iterations")
        decision = "next"
    else:
        data["status"] = "RUNNING"
        decision = "resume"
    return decision, data


def run(home, project, event, state_file=None, default_max=10, log_file=None):
    home, project = Path(home), Path(project)
    global_file = home / ".claude/ralph-state.json"
    project_file = project / "memory/ralph-state.json"
    path = Path(state_file) if state_file else (project_file if project_file.is_file() else global_file)
    if not path.exists():
        return 0
    try:
        if not isinstance(event, dict):
            raise ValueError("Stop input must be a JSON object")
        with path.open(encoding="utf-8-sig") as stream:
            state = json.load(stream)
        decision, data = transition(state, event, project,
                                    normalized(path) == normalized(global_file), default_max)
        if data is None:
            return 0
        save_state(path, data)
    except (OSError, ValueError, TypeError) as exc:
        print(f"WARNING: Ralph state unavailable; allowing stop without claiming completion: {exc}", file=sys.stderr)
        return 0
    log_path = Path(log_file) if log_file else home / ".claude/ralph.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write(f"{data['last_updated']} decision={decision} iteration={data['iteration']} status={data['status']}\n")
    except OSError as exc:
        print(f"WARNING: Ralph log unavailable: {exc}", file=sys.stderr)
    if decision in ("next", "resume"):
        print(f"RALPH LOOP: {'next round' if decision == 'next' else 'resume current round'}; "
              f"iteration={data['iteration']}/{data.get('max_iterations', default_max)}. "
              f"Continue the authorized task, verify results, then update {path}: "
              "round_complete=true, completed=true, fatal_error=true, or needs_confirmation=true.", file=sys.stderr)
        return 2
    print(f"RALPH LOOP: {data['status']} (decision={decision}); allowing stop.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--state-file")
    parser.add_argument("--log-file")
    parser.add_argument("--max-iterations", default="10")
    try:
        args = parser.parse_args()
    except SystemExit as exc:
        if exc.code:
            print("WARNING: invalid Ralph helper arguments; allowing stop", file=sys.stderr)
        return 0  # argparse's error code 2 is not the Stop continuation protocol
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
        maximum = int(args.max_iterations)
        if maximum < 1:
            raise ValueError("max iterations must be positive")
    except (ValueError, OSError) as exc:
        print(f"WARNING: invalid Ralph Stop input: {exc}", file=sys.stderr)
        return 0
    return run(args.home, args.project_root, event, args.state_file, maximum, args.log_file)


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
