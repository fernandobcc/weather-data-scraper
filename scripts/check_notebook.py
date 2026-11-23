"""Check an executed notebook: no errors, every non-setup code cell has output, three chart images."""
import json
import sys
from pathlib import Path


def problems(path: Path, expected_images: int = 3) -> list[str]:
    cells = [c for c in json.loads(path.read_text(encoding="utf-8"))["cells"] if c["cell_type"] == "code"]
    outputs = [o for c in cells for o in c["outputs"]]
    found = []
    if any(o.get("output_type") == "error" for o in outputs):
        found.append("a cell raised an error")
    empty = [i for i, c in enumerate(cells) if not c["outputs"] and "import" not in "".join(c["source"])]
    if empty:
        found.append(f"code cells without output: {empty}")
    images = sum("image/png" in o.get("data", {}) for o in outputs)
    if images != expected_images:
        found.append(f"expected {expected_images} chart images, found {images}")
    return found


if __name__ == "__main__":
    issues = problems(Path(sys.argv[1]))
    print("\n".join(issues) or "notebook ok")
    sys.exit(1 if issues else 0)
