#!/usr/bin/env python3
"""Create or verify the isolated Python runtime used by the Codex package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

_ENV_VENV = "AGENT_MUSIC_STUDIO_CODEX_VENV"
_MARKER = ".agent-music-studio-runtime.json"


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python3"


def _requirements_digest(requirements: Path) -> str:
    return hashlib.sha256(requirements.read_bytes()).hexdigest()


def _runtime_ready(venv_dir: Path, requirements: Path) -> bool:
    python = _venv_python(venv_dir)
    marker = venv_dir / _MARKER
    if not python.is_file() or not marker.is_file():
        return False
    try:
        metadata = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if metadata != {"requirements_sha256": _requirements_digest(requirements)}:
        return False
    probe = subprocess.run(
        [str(python), "-c", "import mcp, yaml"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return probe.returncode == 0


def _write_marker(venv_dir: Path, requirements: Path) -> None:
    payload = {"requirements_sha256": _requirements_digest(requirements)}
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=venv_dir, delete=False
    ) as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(venv_dir / _MARKER)


def main() -> int:
    parser = argparse.ArgumentParser(prog="bootstrap_codex_runtime.py")
    parser.add_argument(
        "--venv",
        type=Path,
        default=Path(
            os.environ.get(
                _ENV_VENV,
                Path.home() / ".agent-music-studio" / "codex-venv",
            )
        ),
        help=f"runtime directory (default: ${_ENV_VENV} or the user data directory)",
    )
    parser.add_argument("--check", action="store_true", help="only verify readiness")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if sys.version_info < (3, 11):  # noqa: UP036 - bootstrap diagnoses host Python
        print("agent-music-studio requires Python 3.11 or newer", file=sys.stderr)
        return 1

    plugin_root = Path(__file__).resolve().parent.parent
    requirements = plugin_root / "requirements.txt"
    venv_dir = args.venv.expanduser().resolve()
    if _runtime_ready(venv_dir, requirements):
        if not args.quiet:
            print(f"Codex runtime is ready: {venv_dir}")
        return 0
    if args.check:
        if not args.quiet:
            print(f"Codex runtime is missing or stale: {venv_dir}", file=sys.stderr)
        return 1

    try:
        if not _venv_python(venv_dir).is_file():
            venv.EnvBuilder(with_pip=True).create(venv_dir)
        python = _venv_python(venv_dir)
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--requirement",
                str(requirements),
            ],
            check=True,
        )
        probe = subprocess.run(
            [str(python), "-c", "import mcp, yaml"],
            check=False,
        )
        if probe.returncode != 0:
            print("Codex runtime dependency probe failed", file=sys.stderr)
            return 1
        _write_marker(venv_dir, requirements)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Codex runtime bootstrap failed: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Codex runtime is ready: {venv_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
