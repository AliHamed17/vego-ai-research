# Agent Memory

Shared project state, history, and decisions for Codex and Claude.

## Core status (start here)

- `current-state.md` — latest project state and quick orientation
- `compiled-memory.md` — generated combined memory (read this at session start)
- `shared-state-report.md` — high-level research and governance state
- `progress.md` — milestones, active tasks, and completion status

## History & decisions

- `session-log.md` — chronological prompt history
- `issues.md` — open, blocked, and resolved issues
- `decisions.md` — durable project decisions and rationale
- `revert-log.md` — changed files and rollback notes
- `revert-log-archive.md` — older rollback entries (preserve with active log)

## Handoff & setup

- `claude-bootstrap-prompt.md` — paste-ready startup for a fresh Claude session
- `codex-nextstep-handoff-prompt.md` — verified handoff for Codex next-step cycles
- `claude-m4b-handoff-prompt.md` — historical: completed M4B-1 implementation
- `automation.md` — scripts and workflow for automatic memory handling

## Resources

- `resource-memory.md` — compact shared index of reusable research/tool resources
- `../dashboards/` — progress, KPI, and results dashboards for Confluence
- `../confluence/wiki-sync.md` — Confluence wiki sync workflow

## Maintenance workflow

**At session start:**
1. Run `.\scripts\refresh-tracking.ps1 -Pull` (recompile memory from source files)
2. Read `compiled-memory.md` for full context
3. Check `current-state.md` for latest status

**During work:** Update `current-state.md`, `progress.md`, or `issues.md` if state changes.

**At session end:**
1. Run `.\scripts\agent-memory-finish.ps1` with a concise summary
2. Run `.\scripts\refresh-tracking.ps1 -Viz` (update trackers and visualizations)
3. Optional: Update `docs/dashboards/` if progress, KPI, or validated results changed

**For Confluence sync:**
- Run `.\scripts\build-confluence-wiki.ps1` to build wiki outbox
- Run `.\scripts\dashboard-health.ps1 -RequireOutbox` to verify
- Update live Confluence if local target IDs are configured in `docs/confluence/wiki-sync-config.local.json`
