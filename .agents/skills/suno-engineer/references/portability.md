# Host translation

- Starting at the current skill directory, walk upward and use the first
  ancestor containing either `canonical-skills/suno-engineer/SKILL.md` or
  a `skills/suno-engineer/SKILL.md` different from this adapter as the workflow
  root.
- Paths in the canonical workflow are relative to that workflow root unless the
  workflow explicitly says otherwise.
- Resolve every literal `${CLAUDE_PLUGIN_ROOT}` in the canonical workflow to
  the discovered workflow root. Do not require that Claude-specific environment
  variable to exist.
- Host-specific commands map to advertised portable skills by semantic name.
- Use current-host file, shell, browser, and MCP equivalents. An unavailable provider tool is a real boundary, not permission to simulate success.
- The canonical skill's Claude model and tool metadata does not constrain other Agent Skills hosts.
- A copy-ready Suno package is local preparation. A provider generation exists only after a real provider response or user-supplied stable result.
- Creative `Final`, human listening approval, rights clearance, and publication
  readiness are distinct facts.
