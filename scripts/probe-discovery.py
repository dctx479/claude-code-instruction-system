#!/usr/bin/env python3
"""Open an isolated, repository-external CLI to inspect /context and /skills interactively."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from eval_support import environment, install


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="core")
    parser.add_argument("--global-install", action="store_true", help="read installed user capabilities, keep hooks disabled during inspection")
    args = parser.parse_args()
    cli = shutil.which("claude")
    with tempfile.TemporaryDirectory(prefix="taiyi-discovery-") as directory:
        base = Path(directory)
        project, config = base / "project", base / "config"
        project.mkdir()
        config.mkdir()
        if args.global_install:
            source = Path.home() / ".claude"
            # Copy only discovery assets. Never copy credentials, personal memory or hooks.
            for kind in ("skills", "agents", "commands"):
                if (source / kind).is_dir():
                    shutil.copytree(source / kind, config / kind)
        else:
            install(config, profile=args.profile, components="skills,agents,commands")
        (config / "settings.json").write_text(json.dumps(dict(disableAllHooks=True, autoMemoryEnabled=False)), encoding="utf-8")
        (config / ".claude.json").write_text(json.dumps(dict(hasCompletedOnboarding=True, theme="dark")), encoding="utf-8")
        env = environment(config)
        env["CLAUDE_CODE_USE_POWERSHELL_TOOL"] = "1"
        return subprocess.call([cli, "--settings", str(config / "settings.json"), "--tools", "Read,Skill",
                                "--permission-mode", "default"], cwd=project, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
