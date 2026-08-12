#!/usr/bin/env python3
"""
Cross-platform wrapper for MCP server that uses venv if available.

Priority order:
1. ~/.bitwize-music/venv/bin/python3 (or python.exe on Windows)
2. python3 (system/user install)

Works on Linux, macOS, Windows, and WSL.
"""

import os
import subprocess
import sys
from pathlib import Path

# Get the directory containing this script
SCRIPT_DIR = Path(__file__).parent
SERVER_PY = SCRIPT_DIR / "server.py"

# Resolve the plugin boundary before choosing an interpreter. Codex launchers
# already execute this wrapper with their isolated runtime and must not be
# redirected into the Claude plugin venv.
plugin_root = Path(
    os.environ.get("PLUGIN_ROOT")
    or os.environ.get("CLAUDE_PLUGIN_ROOT")
    or SCRIPT_DIR.parent.parent
).resolve()

# Check for the Claude/source venv (platform-specific paths).
VENV_DIR = Path.home() / ".bitwize-music" / "venv"

if sys.platform == "win32":
    # Windows: Scripts/python.exe
    VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
else:
    # Linux/macOS/WSL: bin/python3
    VENV_PYTHON = VENV_DIR / "bin" / "python3"

# Use the current isolated interpreter for Codex. Otherwise preserve the
# existing Claude/source preference and fallback.
if (plugin_root / ".codex-plugin" / "plugin.json").is_file():
    python_cmd = sys.executable
elif VENV_PYTHON.exists():
    python_cmd = str(VENV_PYTHON)
else:
    python_cmd = sys.executable

# Export both the agent-neutral name and the Claude compatibility name.
# A host-provided PLUGIN_ROOT wins; Claude-only installations continue to work.
os.environ.setdefault("PLUGIN_ROOT", str(plugin_root))
os.environ.setdefault("CLAUDE_PLUGIN_ROOT", str(plugin_root))

# Execute the server with the selected Python
sys.exit(subprocess.call([python_cmd, str(SERVER_PY), *sys.argv[1:]]))
