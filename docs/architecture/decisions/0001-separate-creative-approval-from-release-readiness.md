# ADR 0001: Separate creative approval from release readiness

- Status: Accepted
- Date: 2026-08-11

## Context

Agent Music Studio is optimized for fast, mutable creative work: album concepts,
track Markdown, lyrics, Suno prompt iteration, generation logs, mastering, and
promotion. Its track status includes `Final`, which is useful for marking a
creative decision but cannot establish rights clearance or publication
readiness.

Conflating those meanings would let a normal creative status transition imply
facts that require separate human judgment or release policy. Requiring a
particular external governance product would create the opposite problem: a
general music workflow would become coupled to one optional integration.

## Decision

`Final` means creatively approved within the mutable workspace. Rights clearance
and publication readiness remain separate decisions made by whichever release
governance workflow a project chooses.

Portable Agent Skills preserve this semantic boundary, but they do not include
or imply a specific evidence-ledger adapter. Host compatibility and release
governance evolve independently.

## Consequences

- Creative workflows stay lightweight and usable without external governance
  infrastructure.
- Upstream Claude functionality can remain stable while portable Agent Skills
  mature incrementally.
- A resume or generation workflow must not describe `Final` as rights-cleared
  or release-ready.
- Optional governance integrations belong with the system they integrate and
  can define their own installation, schema, and lifecycle.
