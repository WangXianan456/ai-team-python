# HANDOFF Update Rules

## Purpose

Keep session continuity across new conversations without relying on long chat history.

## Required Update Moments

1. Before ending any work session.
2. After completing or re-prioritizing tasks.
3. After generating weekly reports/scorecards or major architecture decisions.

## Command

```bash
python scripts/update_handoff.py
```

## Enforcement

- Any session is incomplete if `memory/HANDOFF.md` is stale.
- New sessions must read `memory/HANDOFF.md` before planning.

## Required Fields In HANDOFF

- Repository identity (branch/head/origin)
- Current task snapshot
- Open priorities
- Next-session execution prompt
- North-star and operating principles
