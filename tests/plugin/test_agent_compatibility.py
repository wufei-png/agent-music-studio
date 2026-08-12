"""Static contracts for Agent Skills and Codex plugin compatibility."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import tools.build_codex_plugin as codex_builder
from tools.build_codex_plugin import build_plugin
from tools.plugin_metadata import PORTABLE_SKILLS_FILE, RUNTIME_VERSION_FILE
from tools.state.indexer import _read_plugin_version, get_pending_migrations

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PORTABLE_SKILLS = {"resume", "lyric-writer", "suno-engineer"}


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    _, block, _ = text.split("---", 2)
    value = yaml.safe_load(block)
    assert isinstance(value, dict)
    return value


def _resolve_portable_plugin_root(skill: Path) -> Path:
    """Apply the portable skills' documented source/package root rules."""
    name = skill.parent.name
    for ancestor in (skill.parent, *skill.parents):
        if (ancestor / "canonical-skills" / name / "SKILL.md").is_file():
            return ancestor
        candidate = ancestor / "skills" / name / "SKILL.md"
        if candidate.is_file() and candidate.resolve() != skill.resolve():
            return ancestor
    raise AssertionError(f"cannot resolve plugin root for {skill}")


@pytest.fixture()
def built_plugin(tmp_path: Path) -> Path:
    return build_plugin(PROJECT_ROOT, tmp_path / "agent-music-studio")


def test_codex_plugin_manifest_points_to_real_portable_components(
    built_plugin: Path,
) -> None:
    manifest = json.loads(
        (built_plugin / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert manifest["name"] == "agent-music-studio"
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert (built_plugin / manifest["skills"]).is_dir()
    assert (built_plugin / manifest["mcpServers"]).is_file()


def test_codex_package_keeps_distribution_and_runtime_versions_separate(
    built_plugin: Path,
) -> None:
    distribution = json.loads(
        (built_plugin / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )["version"]
    runtime = json.loads(
        (built_plugin / RUNTIME_VERSION_FILE).read_text(encoding="utf-8")
    )["version"]
    canonical = json.loads(
        (PROJECT_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )["version"]

    assert distribution != runtime
    assert runtime == canonical
    assert _read_plugin_version(built_plugin) == canonical

    pending = get_pending_migrations(
        {"last_migrated_version": "0.43.0"}, built_plugin
    )
    assert [item["version"] for item in pending["pending"]] == [
        "0.44.0",
        "0.59.0",
        "0.90.0",
        "0.91.0",
    ]


def test_codex_package_records_expected_portable_skill_inventory(
    built_plugin: Path,
) -> None:
    inventory = json.loads(
        (built_plugin / PORTABLE_SKILLS_FILE).read_text(encoding="utf-8")
    )
    installed = {
        path.parent.name for path in (built_plugin / "skills").glob("*/SKILL.md")
    }
    assert set(inventory["skills"]) == PORTABLE_SKILLS
    assert installed == PORTABLE_SKILLS


def test_codex_mcp_manifest_uses_agent_neutral_root(built_plugin: Path) -> None:
    manifest = json.loads((built_plugin / ".mcp.json").read_text(encoding="utf-8"))
    assert set(manifest["mcpServers"]) == {"bitwize-music-mcp"}
    server = manifest["mcpServers"]["bitwize-music-mcp"]
    assert server["cwd"] == "."
    command = server["command"]
    assert command.startswith("./")
    assert (built_plugin / command.removeprefix("./")).is_file()


def test_portable_skills_have_standard_frontmatter_and_valid_resources() -> None:
    skill_root = PROJECT_ROOT / ".agents" / "skills"
    discovered = {path.parent.name for path in skill_root.glob("*/SKILL.md")}
    assert discovered == PORTABLE_SKILLS
    for name in PORTABLE_SKILLS:
        skill = skill_root / name / "SKILL.md"
        metadata = _frontmatter(skill)
        assert set(metadata) == {"name", "description"}
        assert metadata["name"] == name
        assert len(metadata["description"]) > 40
        assert "TODO" not in skill.read_text(encoding="utf-8")
        assert (skill.parent / "agents" / "openai.yaml").is_file()
        assert (skill.parent / "references").is_dir()


def test_openai_metadata_mentions_each_skill_in_default_prompt() -> None:
    skill_root = PROJECT_ROOT / ".agents" / "skills"
    for name in PORTABLE_SKILLS:
        metadata = yaml.safe_load(
            (skill_root / name / "agents" / "openai.yaml").read_text(encoding="utf-8")
        )
        assert f"${name}" in metadata["interface"]["default_prompt"]


def test_built_portable_skill_links_resolve_inside_package(
    built_plugin: Path,
) -> None:
    link_pattern = re.compile(r"\[[^]]+\]\(([^)]+)\)")
    for markdown in (built_plugin / "skills").glob("**/*.md"):
        for target in link_pattern.findall(markdown.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#")):
                continue
            resource = markdown.parent / target.split("#", 1)[0]
            assert resource.is_file(), f"missing skill resource: {resource}"


def test_canonical_claude_skills_remain_available() -> None:
    for name in {"resume", "lyric-writer", "suno-engineer"}:
        assert (PROJECT_ROOT / "skills" / name / "SKILL.md").is_file()
    assert (PROJECT_ROOT / ".claude-plugin" / "plugin.json").is_file()


def test_built_plugin_separates_portable_and_canonical_skills(
    built_plugin: Path,
) -> None:
    assert {
        path.parent.name for path in (built_plugin / "skills").glob("*/SKILL.md")
    } == PORTABLE_SKILLS
    assert len(list((built_plugin / "canonical-skills").glob("*/SKILL.md"))) >= 50
    for name in {"resume", "lyric-writer", "suno-engineer"}:
        assert (built_plugin / "canonical-skills" / name / "SKILL.md").is_file()
    assert (built_plugin / "tools" / "bootstrap_codex_runtime.py").is_file()
    assert (built_plugin / "servers" / "bitwize-music-server" / "mcp-launch").is_file()


@pytest.mark.parametrize("name", ["lyric-writer", "resume", "suno-engineer"])
def test_portable_skills_resolve_canonical_resources_in_both_layouts(
    built_plugin: Path,
    name: str,
) -> None:
    source_skill = PROJECT_ROOT / ".agents" / "skills" / name / "SKILL.md"
    installed_skill = built_plugin / "skills" / name / "SKILL.md"

    source_root = _resolve_portable_plugin_root(source_skill)
    installed_root = _resolve_portable_plugin_root(installed_skill)

    assert source_root == PROJECT_ROOT
    assert installed_root == built_plugin
    assert (source_root / "skills" / name / "SKILL.md").is_file()
    assert (installed_root / "canonical-skills" / name / "SKILL.md").is_file()


@pytest.mark.parametrize("name", ["lyric-writer", "suno-engineer"])
def test_portable_translation_resolves_claude_root_references(
    built_plugin: Path,
    name: str,
) -> None:
    token = "${CLAUDE_PLUGIN_ROOT}"
    canonical = (PROJECT_ROOT / "skills" / name / "SKILL.md").read_text(
        encoding="utf-8"
    )
    portability = (
        PROJECT_ROOT / ".agents" / "skills" / name / "references" / "portability.md"
    ).read_text(encoding="utf-8")
    references = set(
        re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+\.md)", canonical)
    )

    assert token in canonical
    assert token in portability
    assert "discovered workflow root" in portability
    assert references
    for reference in references:
        assert (PROJECT_ROOT / reference).is_file(), reference
        assert (built_plugin / reference).is_file(), reference


def test_builder_refuses_to_write_inside_source_repository() -> None:
    with pytest.raises(ValueError, match="outside the source repository"):
        build_plugin(PROJECT_ROOT, PROJECT_ROOT / "build" / "agent-music-studio")


def test_builder_does_not_publish_partial_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "agent-music-studio"

    def fail_copytree(source: Path, target: Path) -> None:
        raise OSError("synthetic copy failure")

    monkeypatch.setattr(codex_builder, "_copytree", fail_copytree)
    with pytest.raises(OSError, match="synthetic copy failure"):
        build_plugin(PROJECT_ROOT, destination)

    assert not destination.exists()
    assert not list(tmp_path.glob(".agent-music-studio-build-*"))


@pytest.mark.parametrize(
    "version",
    ["1.2.3", "1.2.3-rc.1", "1.2.3+build.5", "1.2.3-rc.1+build.5"],
)
def test_runtime_version_accepts_semver_prerelease_and_build_metadata(
    tmp_path: Path, version: str
) -> None:
    (tmp_path / RUNTIME_VERSION_FILE).write_text(
        json.dumps({"version": version}), encoding="utf-8"
    )
    assert _read_plugin_version(tmp_path) == version


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX launcher contract")
def test_codex_launcher_requires_explicit_runtime_bootstrap(
    built_plugin: Path, tmp_path: Path
) -> None:
    missing_venv = tmp_path / "missing-runtime"
    env = os.environ.copy()
    env["AGENT_MUSIC_STUDIO_CODEX_VENV"] = str(missing_venv)
    result = subprocess.run(
        [str(built_plugin / "servers" / "bitwize-music-server" / "mcp-launch")],
        cwd=built_plugin,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "runtime is missing or stale" in result.stderr
    assert "bootstrap_codex_runtime.py" in result.stderr


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX launcher contract")
def test_codex_launcher_checks_with_the_isolated_interpreter(
    built_plugin: Path, tmp_path: Path
) -> None:
    runtime = tmp_path / "runtime"
    isolated_python = runtime / "bin" / "python3"
    isolated_python.parent.mkdir(parents=True)
    invocation_log = tmp_path / "isolated-python.log"
    isolated_python.write_text(
        "\n".join(
            [
                "#!/bin/sh",
                "printf '%s\\n' \"$*\" >> \"$INVOCATION_LOG\"",
                "exit 0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    isolated_python.chmod(0o755)

    hostile_path = tmp_path / "hostile-path"
    hostile_path.mkdir()
    (hostile_path / "dirname").symlink_to("/usr/bin/dirname")
    global_python = hostile_path / "python3"
    global_python.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
    global_python.chmod(0o755)

    env = os.environ.copy()
    env["AGENT_MUSIC_STUDIO_CODEX_VENV"] = str(runtime)
    env["INVOCATION_LOG"] = str(invocation_log)
    env["PATH"] = str(hostile_path)
    result = subprocess.run(
        [str(built_plugin / "servers" / "bitwize-music-server" / "mcp-launch")],
        cwd=built_plugin,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    invocations = invocation_log.read_text(encoding="utf-8").splitlines()
    assert "bootstrap_codex_runtime.py" in invocations[0]
    assert "--check --quiet" in invocations[0]
    assert invocations[1].endswith("run.py")


def test_windows_launcher_checks_with_the_isolated_interpreter() -> None:
    launcher = (
        PROJECT_ROOT / "servers" / "bitwize-music-server" / "mcp-launch.cmd"
    ).read_text(encoding="utf-8")
    assert (
        '"!CODEX_PYTHON!" "!BOOTSTRAP!" --venv "!CODEX_VENV!" --check --quiet'
        in launcher
    )
