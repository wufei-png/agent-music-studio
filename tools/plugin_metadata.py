"""Read host-neutral runtime metadata from a plugin checkout or package."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

RUNTIME_VERSION_FILE = "runtime-version.json"
PORTABLE_SKILLS_FILE = "portable-skills.json"
_VERSION_RE = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def _read_version_file(manifest: Path) -> str | None:
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Cannot read runtime version from %s: %s", manifest, exc)
        return None
    if not isinstance(data, dict):
        logger.warning("Runtime metadata in %s is not a JSON object", manifest)
        return None
    version = data.get("version")
    if not isinstance(version, str) or not _VERSION_RE.fullmatch(version):
        logger.warning("Runtime version in %s is not valid semver", manifest)
        return None
    return version


def read_runtime_version(plugin_root: Path) -> str | None:
    """Return the canonical runtime version, independent of host packaging.

    Codex package versions describe the adapter distribution and do not track
    the upstream migration line. Built packages therefore carry an explicit
    runtime-version file. Source checkouts use the canonical Claude manifest;
    the Codex manifest remains a compatibility fallback for older packages.
    """
    explicit = plugin_root / RUNTIME_VERSION_FILE
    codex_manifest = plugin_root / ".codex-plugin" / "plugin.json"
    if codex_manifest.exists():
        # New Codex packages always carry the canonical runtime marker. Its
        # absence is package corruption, not permission to reinterpret the
        # adapter distribution version as a migration version.
        if not explicit.exists():
            logger.warning("Codex package is missing %s", explicit)
            return None
        return _read_version_file(explicit)
    if explicit.exists():
        return _read_version_file(explicit)

    # Compatibility path for source checkouts and packages produced before
    # runtime-version.json was introduced. Once a higher-authority manifest
    # exists, corruption must fail closed rather than fall through to a host's
    # unrelated distribution version.
    for manifest in (plugin_root / ".claude-plugin" / "plugin.json",):
        if manifest.exists():
            return _read_version_file(manifest)
    return None
