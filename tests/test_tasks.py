import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_tasks.py"
spec = importlib.util.spec_from_file_location("check_tasks", SCRIPT)
assert spec and spec.loader
check_tasks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_tasks)


def test_every_task_file_is_valid():
    tasks = check_tasks.load_tasks()
    by_id = {t.id: t for t in tasks}
    committed = check_tasks.committed_task_ids()
    assert tasks, "no task files found"
    assert {t.id: check_tasks.problems(t, by_id, committed) for t in tasks if check_tasks.problems(t, by_id, committed)} == {}


def test_feature_list_matches_task_status():
    tasks = {t.id: t for t in check_tasks.load_tasks()}
    assert check_tasks.feature_problems(tasks) == []


def test_done_task_without_commit_is_rejected(tmp_path):
    task = check_tasks.Task(id="T99", title="x", status="done", path=tmp_path / "T99-x.md", commands=["true"])
    assert any("no commit" in p for p in check_tasks.problems(task, {"T99": task}, committed=set()))


def test_unchecked_done_task_is_rejected(tmp_path):
    task = check_tasks.Task(id="T99", title="x", status="done", path=tmp_path / "T99-x.md", commands=["true"], unchecked=1)
    assert any("unchecked" in p for p in check_tasks.problems(task, {"T99": task}, committed={"T99"}))


def test_front_matter_is_valid_yaml():
    """GitHub renders the header as YAML; an unquoted ':' in a value breaks it."""
    import re

    import yaml

    for path in sorted(check_tasks.TASKS_DIR.glob("*.md")):
        header = re.match(r"---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
        if path.name == "README.md":
            continue
        assert header, f"{path.name}: missing front matter"
        meta = yaml.safe_load(header.group(1))
        assert isinstance(meta, dict), path.name
        parsed = check_tasks.parse(path)
        assert str(meta["title"]) == parsed.title, f"{path.name}: checker and YAML disagree on the title"
