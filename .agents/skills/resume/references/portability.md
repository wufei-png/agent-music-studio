# Host translation

- Starting at the current skill directory, walk upward and use the first
  ancestor containing either `canonical-skills/resume/SKILL.md` or
  a `skills/resume/SKILL.md` different from this adapter as the workflow root.
- Paths in the canonical workflow are relative to that workflow root unless the
  workflow explicitly says otherwise.
- A host-specific command maps to the advertised portable skill with the same
  semantic name when that skill is available.
- `Read`, `Write`, `Edit`, `Glob`, `Grep`, and `Bash` mean the current host's equivalent file and shell tools; they are not literal tool requirements.
- MCP tool names may be host-namespaced. Match the advertised tool by its final semantic name.
- Never claim a Suno operation, listening decision, rights decision, or release action happened unless there is direct evidence that it did.
- Creative `Final` means creatively approved. It does not prove rights
  clearance or publication readiness.
