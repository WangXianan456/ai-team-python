#!/usr/bin/env python3
"""
Update memory/HANDOFF.md with current repository snapshot.

Usage:
  python scripts/update_handoff.py
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "memory" / "HANDOFF.md"
TASK_DIR = ROOT / "tasks"

STATUS_RE = re.compile(r"^-\s*Status:\s*`?([a-z]+)`?\s*$", re.IGNORECASE)
PRIORITY_RE = re.compile(r"^-\s*Priority:\s*`?([A-Za-z0-9]+)`?\s*$", re.IGNORECASE)


def run_git(args: list[str]) -> str:
    try:
        p = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True, text=True)
        if p.returncode == 0:
            return (p.stdout or "").strip()
    except Exception:
        pass
    return "N/A"


def collect_tasks() -> tuple[dict[str, int], list[str]]:
    counts = {"todo": 0, "doing": 0, "qa": 0, "release": 0, "done": 0, "unknown": 0}
    open_tasks: list[tuple[str, str, str]] = []
    if not TASK_DIR.exists():
        return counts, []

    for p in sorted(TASK_DIR.glob("TASK-*.md")):
        status = "unknown"
        priority = "P2"
        for line in p.read_text(encoding="utf-8").splitlines():
            m = STATUS_RE.match(line.strip())
            if m:
                status = m.group(1).lower()
                continue
            m = PRIORITY_RE.match(line.strip())
            if m:
                priority = m.group(1).upper()
        if status not in counts:
            status = "unknown"
        counts[status] += 1
        if status != "done":
            open_tasks.append((priority, p.stem, status))

    order = {"P0": 0, "P1": 1, "P2": 2}
    open_tasks.sort(key=lambda x: (order.get(x[0], 99), x[1]))
    lines = [f"- {task} | priority={pri} | status={st}" for pri, task, st in open_tasks[:10]]
    return counts, lines


def main() -> None:
    ROOT.joinpath("memory").mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    branch = run_git(["branch", "--show-current"]) or "N/A"
    head = run_git(["rev-parse", "--short", "HEAD"]) or "N/A"
    remote = run_git(["remote", "get-url", "origin"]) or "N/A"

    counts, open_lines = collect_tasks()

    doc = []
    doc.append("# HANDOFF")
    doc.append("")
    doc.append(f"- Updated (UTC): `{now}`")
    doc.append(f"- Repo: `{ROOT.name}`")
    doc.append(f"- Branch: `{branch}`")
    doc.append(f"- HEAD: `{head}`")
    doc.append(f"- Origin: `{remote}`")
    doc.append("")
    doc.append("## North Star")
    doc.append("- Build expert-level AI team capability with measurable quality, security, and cost control.")
    doc.append("- Use multi-pass workflow: framing -> evidence -> validation -> finalization.")
    doc.append("")
    doc.append("## Task Snapshot")
    doc.append(f"- todo={counts['todo']}, doing={counts['doing']}, qa={counts['qa']}, release={counts['release']}, done={counts['done']}, unknown={counts['unknown']}")
    doc.append("")
    doc.append("## Open Priorities")
    if open_lines:
        doc.extend(open_lines)
    else:
        doc.append("- No open tasks detected.")
    doc.append("")
    doc.append("## Next Session Prompt")
    doc.append("- Read README, policies, workflows, tasks, and this HANDOFF file first.")
    doc.append("- Propose top 3 tasks (P0/P1), execute the first one end-to-end, and record evidence.")
    doc.append("")
    doc.append("## Auto-Update Rule")
    doc.append("- Run `python scripts/update_handoff.py` before ending each work session.")
    doc.append("- Rule doc: `policies/handoff_update_rules.md`.")
    doc.append("")

    HANDOFF.write_text("\n".join(doc), encoding="utf-8")
    print(f"updated: {HANDOFF}")


if __name__ == "__main__":
    main()
