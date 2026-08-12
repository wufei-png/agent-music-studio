---
name: suno-engineer
description: Prepare, review, and iterate Suno lyrics-box, style, exclusion, duration, and generation-log inputs for vocal or instrumental tracks. Use when a track is ready for Suno prompting or a real Suno result needs diagnosis; do not use to fabricate a provider operation or treat a creative approval as release clearance.
---

# Suno Engineer

Translate project intent into focused Suno inputs, then keep preparation, live provider operation, and human evaluation as distinct steps.

## Workflow

1. Read [the host translation rules](references/portability.md).
2. Starting at this skill directory, walk upward until either `canonical-skills/suno-engineer/SKILL.md` or a `skills/suno-engineer/SKILL.md` different from this adapter exists. Read it as the canonical workflow and load only the referenced Suno and genre guides needed for the current track.
3. Inspect the track, duration target, lyrics or instrumental flag, artist profile, genre guide, pronunciation notes, and any user override file.
4. Produce or review the Lyrics Box, Style of Music, Exclude Styles, and generation settings. Keep section directions out of sung text and distinguish documented platform behavior from heuristics.
5. Before any live provider action, state whether Suno is actually accessible through an authorized browser or tool. If it is not, stop at a copy-ready generation package.
6. After a real generation attempt, capture the provider object ID or stable URL, model, operation, timestamp, prompt and lyrics references, and any selected output. Do not invent missing values.
7. Record the real result in the mutable creative generation log. Human listening and rights decisions remain separate from the provider operation.
8. Keep rejected attempts in the creative generation log so later iterations have useful context.

Creative status `Final` means the user approved the creative result. It does not establish rights clearance or publication readiness.
