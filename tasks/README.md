# Tasks

One file per unit of work, derived from [`specs/spec.md`](../specs/spec.md). A task is
**done only when its Definition of done is fully checked, every Verify command passes,
and git history contains its commits**:

```bash
python scripts/check_tasks.py --list     # board
python scripts/check_tasks.py T07        # verify one task
python scripts/check_tasks.py            # re-verify every done task (regression)
```

## Lifecycle

`todo` → `in_progress` → `done`

1. Pick a `todo` task whose `depends_on` are all `done`. Branch `tNN-short-name`.
2. **Work commit(s)** `Tnn: <what>`: code, tests, and the task file set to `in_progress`.
3. Run `check_tasks.py Tnn` until every Verify command passes.
4. **Done commit** `Tnn: mark done`: tick the Definition of done, set `status: done`, fill in
   *Evidence*, flip the feature in `feature_list.json`, append to `progress.md`.
5. Open one PR per task; merge when CI is green.

## What the checker enforces

- Required sections, valid status, and known dependencies (a started task needs its dependencies done).
- `done` ⇒ no unchecked boxes, and at least one commit whose subject starts with `Tnn:`.
- `feature_list.json`: a feature is `done` exactly when all of its tasks are.
- Verify commands pass, for every done task, on every CI run (catches regressions).

## Writing a task

- **Verify commands are deterministic and offline** (pytest node ids, pyright, file and content checks). Anything that needs the network, a browser or Docker goes under *Manual checks*.
- Definition-of-done items are observable outcomes ("CSV header matches the spec"), not activities.
- One feature per task; split it if the Verify block grows past ~6 commands.
- The header is YAML (GitHub renders it): quote any value that contains `:`, e.g. `title: "README: run guide"`.
- New work that isn't in the spec: update the spec first (new `R`), then add the task.

Start from [`_template.md`](_template.md).
