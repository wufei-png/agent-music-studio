#!/usr/bin/env python3
"""Codex discovery check for the local plugin marketplace.

This temporarily registers the checkout as a local marketplace, runs
``plugin list``, and removes that marketplace again. It never installs or
enables the plugin. The Codex CLI confirms that it can discover the plugin
manifest, while this checker also verifies that the discovered plugin points
at the 53 canonical skill directories in this checkout.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

EXPECTED_NAME = "bitwize-music"
EXPECTED_SKILL_COUNT = 53


def _entries(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("plugins", "available", "entries"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def _marketplaces_by_root(codex: str, root: Path):
    """Return configured local marketplace roots and names, or ``None`` on error."""
    try:
        result = subprocess.run(
            [codex, "plugin", "marketplace", "list", "--json"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    marketplaces = payload.get("marketplaces", []) if isinstance(payload, dict) else []
    if not isinstance(marketplaces, list):
        return None

    by_root = {}
    for marketplace in marketplaces:
        if not isinstance(marketplace, dict):
            continue
        name = marketplace.get("name")
        installed_root = marketplace.get("root")
        if not isinstance(name, str) or not isinstance(installed_root, str):
            continue
        by_root[Path(installed_root).resolve()] = name
    return by_root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository checkout containing .codex-plugin/plugin.json",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    codex = shutil.which("codex")
    if codex is None:
        print("codex CLI not found", file=sys.stderr)
        return 2

    before = _marketplaces_by_root(codex, root)
    if before is None:
        print("Could not read the configured Codex marketplaces", file=sys.stderr)
        return 1

    marketplace_name = before.get(root)
    added_this_run = False

    def discover() -> int:
        nonlocal marketplace_name, added_this_run

        add = subprocess.run(
            [codex, "plugin", "marketplace", "add", str(root), "--json"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=30,
        )
        if add.returncode != 0:
            print(add.stderr.strip() or add.stdout.strip(), file=sys.stderr)
            return add.returncode

        try:
            add_payload = json.loads(add.stdout)
            marketplace_name = add_payload["marketplaceName"]
            added_this_run = not add_payload.get("alreadyAdded", False)
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            # The successful add may already have persisted the marketplace.
            # Compare roots so a malformed response cannot leave our temporary
            # entry behind, while preserving an entry that existed beforehand.
            after = _marketplaces_by_root(codex, root)
            if root not in before and after is not None and root in after:
                marketplace_name = after[root]
                added_this_run = True
            print(f"Codex marketplace add returned invalid JSON: {exc}", file=sys.stderr)
            return 1

        result = subprocess.run(
            [
                codex,
                "plugin",
                "list",
                "--marketplace",
                marketplace_name,
                "--available",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=30,
        )
        if result.returncode != 0:
            print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
            return result.returncode

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            print(f"Codex discovery returned invalid JSON: {exc}", file=sys.stderr)
            return 1

        entries = _entries(payload)
        discovered = [
            entry
            for entry in entries
            if isinstance(entry, dict) and entry.get("name") == EXPECTED_NAME
        ]
        if not discovered:
            print(f"Codex did not discover {EXPECTED_NAME!r}: {result.stdout}", file=sys.stderr)
            return 1

        skill_dirs = sorted(
            path for path in (root / "skills").iterdir()
            if path.is_dir() and not path.name.startswith(".")
        )
        missing = [path.name for path in skill_dirs if not (path / "SKILL.md").is_file()]
        if len(skill_dirs) != EXPECTED_SKILL_COUNT or missing:
            print(
                f"Canonical skill check failed: {len(skill_dirs)} directories, missing {missing}",
                file=sys.stderr,
            )
            return 1

        version = discovered[0].get("version", "unknown")
        print(
            f"Codex discovered {EXPECTED_NAME} version {version}; "
            f"canonical skills: {len(skill_dirs)}"
        )
        return 0

    cleanup_failed = False
    try:
        result_code = discover()
    finally:
        if added_this_run and marketplace_name:
            try:
                remove = subprocess.run(
                    [codex, "plugin", "marketplace", "remove", marketplace_name, "--json"],
                    capture_output=True,
                    text=True,
                    cwd=root,
                    timeout=30,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                print(
                    "Failed to remove temporary Codex marketplace "
                    f"{marketplace_name!r}: {exc}",
                    file=sys.stderr,
                )
                cleanup_failed = True
            else:
                if remove.returncode != 0:
                    print(
                        "Failed to remove temporary Codex marketplace "
                        f"{marketplace_name!r}: {remove.stderr.strip() or remove.stdout.strip()}",
                        file=sys.stderr,
                    )
                    cleanup_failed = True

    if cleanup_failed:
        return 1
    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
