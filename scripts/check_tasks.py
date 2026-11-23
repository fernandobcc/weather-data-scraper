"""Task harness: validate tasks/*.md against git history and feature_list.json, then run Verify commands.

python scripts/check_tasks.py              # validate all, verify every `done` task
python scripts/check_tasks.py T05 T11      # verify specific tasks (any status)
python scripts/check_tasks.py --list       # status board, no commands run
"""
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
FEATURES = ROOT / "feature_list.json"
STATUSES = ("todo", "in_progress", "done")
SECTIONS = ("## Goal", "## Definition of done", "## Verify")


@dataclass
class Task:
    id: str
    title: str
    status: str
    path: Path
    requirements: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    unchecked: int = 0
    commands: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)


def _split(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def parse(path: Path) -> Task:
    text = path.read_text(encoding="utf-8")
    header = re.match(r"---\n(.*?)\n---\n", text, re.S)
    pairs = [line.split(":", 1) for line in header.group(1).splitlines()] if header else []
    meta = {k.strip(): v.strip() for k, v in pairs}
    verify = re.search(r"## Verify\s*```(?:bash|sh)?\n(.*?)```", text, re.S)
    dod = text.split("## Definition of done", 1)[-1].split("\n## ", 1)[0]
    return Task(
        id=meta.get("id", ""),
        title=meta.get("title", ""),
        status=meta.get("status", ""),
        path=path,
        requirements=_split(meta.get("requirements", "")),
        depends_on=_split(meta.get("depends_on", "")),
        unchecked=dod.count("- [ ]"),
        commands=[c for c in (verify.group(1).splitlines() if verify else []) if c.strip() and not c.startswith("#")],
        missing_sections=[s for s in SECTIONS if s not in text],
    )


def load_tasks() -> list[Task]:
    return [parse(p) for p in sorted(TASKS_DIR.glob("T*.md"))]


def committed_task_ids() -> set[str]:
    """Task ids that appear as a `Tnn:` commit-subject prefix in the current history."""
    log = subprocess.run(["git", "log", "--format=%s"], cwd=ROOT, capture_output=True, text=True).stdout
    return set(re.findall(r"^(T\d{2}):", log, re.M))


def problems(task: Task, by_id: dict[str, Task], committed: set[str]) -> list[str]:
    found = [f"missing section {s!r}" for s in task.missing_sections]
    if not re.fullmatch(r"T\d{2}", task.id) or not task.path.name.startswith(task.id):
        found.append("id must be Tnn and match the file name prefix")
    if task.status not in STATUSES:
        found.append(f"status must be one of {STATUSES}")
    if not task.commands:
        found.append("Verify block has no commands")
    for dep in task.depends_on:
        if dep not in by_id:
            found.append(f"unknown dependency {dep}")
        elif task.status != "todo" and by_id[dep].status != "done":
            found.append(f"{task.status} but dependency {dep} is {by_id[dep].status}")
    if task.status == "done":
        if task.unchecked:
            found.append(f"done but {task.unchecked} Definition-of-done item(s) unchecked")
        if task.id not in committed:
            found.append(f"done but no commit starting with '{task.id}:' in git history")
    return found


def feature_problems(by_id: dict[str, Task]) -> list[str]:
    """A feature is done exactly when all of its tasks are done."""
    if not FEATURES.exists():
        return []
    found = []
    for feature in json.loads(FEATURES.read_text(encoding="utf-8"))["features"]:
        tasks = feature.get("tasks", [])
        missing = [t for t in tasks if t not in by_id]
        if missing or not tasks:
            found.append(f"{feature['id']}: unknown or missing tasks {missing}")
            continue
        all_done = all(by_id[t].status == "done" for t in tasks)
        if (feature["status"] == "done") != all_done:
            found.append(f"{feature['id']}: status {feature['status']!r} but tasks {tasks} all done = {all_done}")
    return found


def verify(task: Task) -> bool:
    print(f"\n{task.id} {task.title}")
    ok = True
    for cmd in task.commands:
        result = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
        passed = result.returncode == 0
        ok &= passed
        print(f"  {'✓' if passed else '✗'} {cmd}")
        if not passed:
            print("    " + (result.stdout + result.stderr).strip().replace("\n", "\n    ")[-1500:])
    return ok


def main(argv: list[str]) -> int:
    tasks = load_tasks()
    by_id = {t.id: t for t in tasks}
    committed = committed_task_ids()
    issues = [f"{t.id}: " + "; ".join(p) for t in tasks if (p := problems(t, by_id, committed))]
    issues += feature_problems(by_id)
    for issue in issues:
        print(f"✗ {issue}")

    if "--list" in argv:
        for t in tasks:
            print(f"{t.id}  {t.status:<11} {t.title}")
        return 1 if issues else 0

    unknown = [i for i in argv if i not in by_id]
    if unknown:
        print(f"Unknown task id(s): {', '.join(unknown)}")
        return 1
    selected = [by_id[i] for i in argv] if argv else [t for t in tasks if t.status == "done"]
    failed = [t.id for t in selected if not verify(t)]
    summary = f"\n{len(selected) - len(failed)}/{len(selected)} task(s) verified"
    print(summary + (f"; failed: {', '.join(failed)}" if failed else ""))
    return 1 if failed or issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
