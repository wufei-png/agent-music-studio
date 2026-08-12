# Agent compatibility

Agent Music Studio keeps the complete upstream Claude Code plugin and adds a deliberately small portable slice before attempting a risky 53-skill rewrite.

| Host | Entry point | First-slice status |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json`, `skills/`, `.mcp.json` | Upstream behavior preserved |
| Codex / ChatGPT plugin | generated `.codex-plugin/plugin.json`, `skills/`, `.mcp.json` | `resume`, `lyric-writer`, and `suno-engineer`; local MCP commands use plugin-relative paths with plugin-root `cwd` |
| Codex repository skills | `.agents/skills/` | Auto-discovered from the repository root |
| Other Agent Skills hosts | `.agents/skills/` | Standard `name` and `description` frontmatter; host tool translation may still be needed |
| Generic MCP clients | `servers/bitwize-music-server/mcp-launch` | STDIO server; accepts `PLUGIN_ROOT` with Claude compatibility fallback |

The portable skills are thin adapters over canonical upstream workflows. Their instructions use semantic skill names and discover canonical resources by content, without assuming a particular host's invocation syntax or package manifest. This avoids breaking Claude model routing and tool metadata while establishing translation rules that can later be upstreamed.

The source tree cannot use root `skills/` for both formats: the current OpenAI plugin validator reserves `skills/` and `.mcp.json` inside a distributable plugin, while upstream Claude Code already owns those paths with different contracts. Build an isolated package instead:

```bash
mkdir -p /tmp/agent-music-build
python3 tools/build_codex_plugin.py /tmp/agent-music-build/agent-music-studio
```

The builder copies portable adapters to package `skills/`, keeps upstream workflows under `canonical-skills/`, emits the required `.codex-plugin/plugin.json` and `.mcp.json`, and includes the local MCP runtime. It builds in a sibling staging directory and publishes the completed package atomically. It refuses to overwrite an existing destination.

## Codex runtime bootstrap

The Codex package does not reuse Claude's `~/.bitwize-music/venv` and does not install dependencies during MCP startup. Bootstrap its isolated runtime explicitly:

```bash
python3 /path/to/agent-music-studio/tools/bootstrap_codex_runtime.py
```

The default runtime directory is `~/.agent-music-studio/codex-venv`. Set `AGENT_MUSIC_STUDIO_CODEX_VENV` or pass `--venv` to choose another location. The command is idempotent: it skips installation when the requirements digest and dependency probe still match. The launcher exits with a repair command when the runtime is absent or stale.

This bootstrap is specific to the generated Codex package. Other Agent Skills hosts can use the repository-local adapters, but this release does not claim host-specific installation packages for them.

## Creative and release semantics

The artist/album/track Markdown tree is mutable creative state. `Final` means creatively approved. It does not prove rights clearance or publication readiness, and the portable adapters do not claim to query an external release-governance system.

## Validation

Validate the portable package:

```bash
python3 -m pytest tests/plugin/test_agent_compatibility.py
python3 tools/build_codex_plugin.py /tmp/agent-music-build/agent-music-studio
python3 /tmp/agent-music-build/agent-music-studio/tools/bootstrap_codex_runtime.py \
  --venv /tmp/agent-music-build/codex-venv
```

Validate the agent-neutral MCP launch:

```bash
PLUGIN_ROOT="$PWD" python3 tests/e2e/mcp_boot_check.py \
  --call-tool health_check -- \
  "$PWD/servers/bitwize-music-server/mcp-launch"
```
