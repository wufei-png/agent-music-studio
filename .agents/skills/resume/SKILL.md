---
name: resume
description: Resume an existing music album, report its current creative status, and recommend one concrete next action. Use when the user names an album, asks to continue previous music work, or wants a progress summary; do not use to create a new album.
---

# Resume Music Work

Resume an album from its mutable creative workspace without overstating what that workspace proves.

## Workflow

1. Read [the host translation rules](references/portability.md).
2. Starting at this skill directory, walk upward until either `canonical-skills/resume/SKILL.md` or a `skills/resume/SKILL.md` different from this adapter exists. Read that file as the canonical album-resume workflow and ignore host-specific frontmatter.
3. Use the advertised `bitwize-music-mcp` tools when available: find the album, rebuild stale state if needed, get album progress, list tracks, and update session context.
4. If MCP is unavailable, inspect the configured creative workspace read-only and explain which state query could not be performed. Do not invent progress.
5. Report the album phase, track status, and missing creative work. State separately that this creative status does not establish rights clearance, publication readiness, or any external release-governance decision.
6. Recommend exactly one next action. Invoke an available portable workflow by its advertised name; otherwise name the canonical workflow and explain that its portable adapter is not yet included.

If every track is `Final`, recommend import or mastering work as appropriate. Never label the project rights-cleared or release-ready from creative workspace state alone.
