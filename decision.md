# Decisions

ADR-style log: context → decision → consequence. Each entry is added in the commit of
the task that made it.

## D01: Spec before code (T00)
- **Context:** The brief mixes required, optional and bonus items, plus stakeholder requests (frontend, notebook, tooling).
- **Decision:** Translate the brief into `specs/spec.md` with numbered requirements and data/API contracts before writing code.
- **Consequence:** Every task, feature and test traces back to an `R` id; changes in scope start as spec edits.

## D02: Task harness with checkable completion (T00)
- **Context:** Agents (and people) tend to call work "done" too early, and a tracker can drift from what actually happened.
- **Decision:** One file per task in `tasks/` with a Definition of done and offline Verify commands. `scripts/check_tasks.py` refuses a `done` task with unchecked boxes, failing commands, unfinished dependencies, or no `Tnn:` commit in git history, and keeps `feature_list.json` in sync. One PR per task.
- **Consequence:** The task board, the feature list and the git history can't disagree without CI failing. Re-running every done task's checks on each PR also catches regressions.
