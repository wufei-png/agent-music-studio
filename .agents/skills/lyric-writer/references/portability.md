# Host translation

- Starting at the current skill directory, walk upward and use the first
  ancestor containing either `canonical-skills/lyric-writer/SKILL.md` or
  a `skills/lyric-writer/SKILL.md` different from this adapter as the workflow
  root.
- Paths in the canonical workflow are relative to that workflow root unless the
  workflow explicitly says otherwise.
- Resolve every literal `${CLAUDE_PLUGIN_ROOT}` in the canonical workflow to
  the discovered workflow root. Do not require that Claude-specific environment
  variable to exist.
- A host-specific command maps to the advertised portable skill with the same
  semantic name when that skill is available.
- Host-specific model and effort frontmatter in the canonical skill is advisory context, not a requirement for other agents.
- Use the current host's equivalent read, edit, search, and shell tools.
- Do not browse or operate Suno unless the user authorized it and a suitable browser or provider tool is actually available.
- Draft lyrics and prompt iterations stay in the mutable creative workspace.
