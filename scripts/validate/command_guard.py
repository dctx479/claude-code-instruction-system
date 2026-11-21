#!/usr/bin/env python3
"""Supplementary shell checks, not a shell sandbox or authorization engine."""
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys


def blocked(command):
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
        lexer.whitespace = " \t\r"
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return "unparseable shell command"
    segments, current = [], []
    for token in tokens:
        if token and all(char in "();<>|&\n" for char in token):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    for tokens in segments:
        index = 0
        while index < len(tokens) and re.match(r"^[A-Za-z_][A-Za-z_0-9]*=", tokens[index]):
            index += 1
        while index < len(tokens) and tokens[index] in {"sudo", "env", "command", "exec", "nohup"}:
            index += 1
            while index < len(tokens) and (tokens[index].startswith("-") or re.match(r"^[A-Za-z_][A-Za-z_0-9]*=", tokens[index])):
                index += 2 if tokens[index] in {"-u", "-g", "--user", "--group", "--unset"} else 1
        if index >= len(tokens):
            continue
        word = tokens[index].rsplit("/", 1)[-1]
        if word == "git":
            following = tokens[index + 1:]
            cursor = 0
            while cursor < len(following) and following[cursor].startswith("-"):
                cursor += 2 if following[cursor] in {"-C", "-c", "--git-dir", "--work-tree", "--namespace"} else 1
            if cursor < len(following) and following[cursor] == "push":
                options = following[cursor + 1:]
                if any(a in {"-f", "--force"} or a.startswith("--force=") or
                       (a.startswith("-") and not a.startswith("--") and "f" in a[1:]) for a in options):
                    return "forced git push"
        if re.fullmatch(r"(?:mkfs(?:\.[\w]+)?|fdisk|parted)", word, re.I):
            return "disk formatting"
        if word != "rm":
            continue
        args = tokens[index + 1:]
        flags = "".join(a[1:] for a in args if a.startswith("-") and not a.startswith("--"))
        recursive = "r" in flags.lower() or "--recursive" in args
        force = "f" in flags or "--force" in args
        targets = [a for a in args if not a.startswith("-")]
        if recursive and force and any(
                a.startswith(("/", "~", "$HOME", "${HOME}", "../")) for a in targets):
            return "recursive forced deletion of an absolute/home/parent path"
    return ""


def main():
    try:
        raw = sys.stdin.read()
        event = json.loads(raw)
        command = event["tool_input"]["command"]
        if not isinstance(command, str):
            raise ValueError("command must be a string")
    except (ValueError, KeyError, TypeError) as exc:
        print(f"WARNING: command guard input invalid: {exc}", file=sys.stderr)
        return 2
    reason = blocked(command)
    if reason:
        # Never echo the original command: arguments can contain secrets.
        print(f"WARNING: BLOCKED: {reason}", file=sys.stderr)
        return 2
    if re.search(r"\b(?:docker|compose|podman)\b", command):
        helper = Path(__file__).resolve().parents[1] / "port-management/port-check-hook.py"
        if helper.is_file():
            try:
                result = subprocess.run([sys.executable, str(helper)], input=raw, text=True,
                                        encoding="utf-8", timeout=4)
                if result.returncode:
                    print("WARNING: port check returned a failure", file=sys.stderr)
                return result.returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                print(f"WARNING: port check unavailable: {exc}", file=sys.stderr)
        else:
            print("WARNING: port check helper missing", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
