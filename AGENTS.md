# Agent Music Studio contributor guide

This repository has two compatibility layers that must remain independently usable:

- `skills/` and `.claude-plugin/` are the upstream Claude Code implementation.
- `.agents/skills/` is the repository-local Agent Skills adapter. `packaging/codex/` and `tools/build_codex_plugin.py` produce the isolated Codex plugin package.

Do not remove Claude-specific frontmatter from the upstream skills merely to satisfy another host. Keep portable host translation in `.agents/skills/` until a workflow is genuinely agent-neutral at its canonical source.

The mutable album and track Markdown tree is the creative workspace. `Final` in the creative workspace means creatively approved; it never means rights-cleared or release-ready.

Before committing adapter changes, run:

```bash
python3 -m pytest tests/plugin/test_agent_compatibility.py
python3 tools/build_codex_plugin.py /tmp/plugin-build/agent-music-studio
python3 /tmp/plugin-build/agent-music-studio/tools/bootstrap_codex_runtime.py \
  --venv /tmp/plugin-build/codex-venv
python3 tests/e2e/mcp_boot_check.py --call-tool health_check -- \
  "$PWD/servers/bitwize-music-server/mcp-launch"
```
