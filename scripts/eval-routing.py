#!/usr/bin/env python3
"""Opt-in real Skill-tool routing evaluation in a disposable config/project."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="invoke billed CLI calls with a $0.10 per-case budget (last request may exceed it)")
    parser.add_argument("--limit", type=int, default=0, help="0 means all cases")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.run:
        parser.error("--run is required")
    cli = shutil.which("claude")
    if not cli:
        parser.error("Claude CLI unavailable")
    fixture = json.loads((ROOT / "evals/routing/core.json").read_text(encoding="utf-8"))
    cases = fixture["cases"][:args.limit or None]
    with tempfile.TemporaryDirectory(prefix="taiyi-routing-eval-") as directory:
        temporary = Path(directory)
        config = temporary / "config"
        project = temporary / "project"
        project.mkdir()
        install = subprocess.run([sys.executable, str(ROOT / "scripts/install-global.py"), "--target", str(config),
                                  "--components", "skills", "--profile", "core"], capture_output=True, text=True, encoding="utf-8")
        if install.returncode:
            raise RuntimeError("temporary skill installation failed")
        settings = config / "settings.json"
        settings.write_text(json.dumps(dict(disableAllHooks=True, autoMemoryEnabled=False,
                                             permissions={"allow": ["Skill"]})), encoding="utf-8")
        env = dict(os.environ, CLAUDE_CONFIG_DIR=str(config))
        personal = Path.home() / ".claude/settings.json"
        if personal.is_file():
            values = json.loads(personal.read_text(encoding="utf-8-sig")).get("env", {})
            env.update({k: str(v) for k, v in values.items() if k.startswith("ANTHROPIC_")})
        version = subprocess.check_output([cli, "--version"], text=True).strip()
        results = []
        for index, case in enumerate(cases, 1):
            process = subprocess.run([cli, "-p", case["prompt"], "--settings", str(settings),
                                      "--tools", "Skill", "--no-session-persistence", "--output-format", "stream-json",
                                      "--verbose", "--max-turns", "2", "--max-budget-usd", "0.10"],
                                     cwd=project, env=env, capture_output=True, text=True, encoding="utf-8", timeout=90)
            selected, final = [], {}
            for line in process.stdout.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if event.get("type") == "assistant":
                    for block in event.get("message", {}).get("content", []):
                        if block.get("type") == "tool_use" and block.get("name") == "Skill":
                            selected.append(block.get("input", {}).get("skill"))
                if event.get("type") == "result":
                    final = event
            observed = selected[0] if selected else None
            # A no-match is only valid if the CLI actually completed, not on missing evidence/errors.
            valid = bool(final) and not final.get("is_error") and process.returncode == 0
            results.append(dict(case=index, owner=case["owner"], selected=selected, cli_exit=process.returncode,
                                observed=observed, passed=valid and observed == case["owner"],
                                evidence_complete=valid, cost_usd=final.get("total_cost_usd"), subtype=final.get("subtype")))
            print(f"case {index}/{len(cases)}: {'PASS' if results[-1]['passed'] else 'FAIL/INCOMPLETE'}", file=sys.stderr, flush=True)
        report = dict(cli_version=version, profile="core", cases=len(results),
                      passed=sum(r["passed"] for r in results), results=results,
                      scope="First actual Skill tool call with only Skill enabled. This is routing, not workflow behavior.")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({k: v for k, v in report.items() if k != "results"}, ensure_ascii=False))
        return 0 if report["passed"] == report["cases"] else 1


if __name__ == "__main__":
    sys.exit(main())
