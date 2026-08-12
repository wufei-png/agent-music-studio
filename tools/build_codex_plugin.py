#!/usr/bin/env python3
"""Build a validator-ready Codex plugin without changing Claude source paths."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

# Keep the same canonical import for module and direct-script execution.
_REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from tools.plugin_metadata import (
    PORTABLE_SKILLS_FILE,
    RUNTIME_VERSION_FILE,
)

PLUGIN_NAME = "agent-music-studio"
RUNTIME_DIRECTORIES = (
    "config",
    "genres",
    "migrations",
    "reference",
    "servers",
    "templates",
    "tools",
)
RUNTIME_FILES = ("requirements.txt",)


def _copytree(source: Path, target: Path) -> None:
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )


def build_plugin(source_root: Path, destination: Path) -> Path:
    source_root = source_root.resolve()
    destination = destination.resolve()
    if destination.name != PLUGIN_NAME:
        raise ValueError(f"destination directory must be named {PLUGIN_NAME!r}")
    if destination.is_relative_to(source_root):
        raise ValueError("destination must be outside the source repository")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"destination already exists: {destination}")

    upstream_manifest = json.loads(
        (source_root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    runtime_version = upstream_manifest.get("version")
    if not isinstance(runtime_version, str) or not runtime_version:
        raise ValueError("canonical plugin manifest must contain a runtime version")
    portable_skills = sorted(
        path.parent.name
        for path in (source_root / ".agents" / "skills").glob("*/SKILL.md")
    )
    if not portable_skills:
        raise ValueError("Codex package must contain at least one portable skill")

    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{PLUGIN_NAME}-build-", dir=destination.parent)
    )
    try:
        (staging / ".codex-plugin").mkdir()
        shutil.copy2(
            source_root / "packaging" / "codex" / "plugin.json",
            staging / ".codex-plugin" / "plugin.json",
        )
        shutil.copy2(
            source_root / "packaging" / "codex" / "mcp.json",
            staging / ".mcp.json",
        )
        (staging / RUNTIME_VERSION_FILE).write_text(
            json.dumps({"version": runtime_version}, indent=2) + "\n",
            encoding="utf-8",
        )
        (staging / PORTABLE_SKILLS_FILE).write_text(
            json.dumps({"skills": portable_skills}, indent=2) + "\n",
            encoding="utf-8",
        )
        (staging / "skills").mkdir()
        for skill_name in portable_skills:
            _copytree(
                source_root / ".agents" / "skills" / skill_name,
                staging / "skills" / skill_name,
            )
        _copytree(source_root / "skills", staging / "canonical-skills")
        for directory in RUNTIME_DIRECTORIES:
            _copytree(source_root / directory, staging / directory)
        for filename in RUNTIME_FILES:
            shutil.copy2(source_root / filename, staging / filename)
        staging.replace(destination)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(prog="build_codex_plugin.py")
    parser.add_argument("destination", help=f"new output directory named {PLUGIN_NAME}")
    args = parser.parse_args()
    source_root = Path(__file__).resolve().parent.parent
    print(build_plugin(source_root, Path(args.destination)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
