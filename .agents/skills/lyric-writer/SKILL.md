---
name: lyric-writer
description: Draft, revise, or review lyrics for a vocal music track using prosody, rhyme, pronunciation, structure, and Suno-readiness checks. Use when the user asks to write or improve lyrics or work on a vocal track; do not use for instrumental tracks or to claim a provider generation occurred.
---

# Lyric Writer

Produce singable lyrics while preserving the upstream craft workflow and keeping claims proportional to work that actually occurred.

## Workflow

1. Read [the host translation rules](references/portability.md).
2. Starting at this skill directory, walk upward until either `canonical-skills/lyric-writer/` or a `skills/lyric-writer/` different from this adapter exists, then read these canonical resources as needed:
   - `SKILL.md`
   - `craft-reference.md`
   - `examples.md`
   - `documentary-standards.md` for factual or documentary material
3. If a track file is provided, check `instrumental: true` or the Track Details instrumental field first. Stop and route instrumental work to the `suno-engineer` skill.
4. Establish the intended point of view, emotional turn, genre, approximate duration, and source constraints from available project context. Ask only for a missing choice that materially changes the song.
5. Draft or revise the lyrics, then run the canonical quality checks and the requested refinement passes. Report unresolved violations rather than hiding them.
6. Update the creative track only when the user asked for a change. A draft or revision remains mutable creative material.
7. Hand off to the `suno-engineer` skill only after the lyrics and required source checks are ready.

Do not assume a Claude model tier, a provider login, or live browser access. Use the current host's strongest appropriate reasoning and file tools within the user's authorization.
