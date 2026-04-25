from __future__ import annotations

import shutil
from pathlib import Path


CONTENT_SUFFIXES = {".md", ".ipynb"}
EXCLUDED_TOP_LEVEL = {
    "AbiesNotes",
    "CourseNotes",
    "javascripts",
    "scripts",
    "stylesheets",
}


def should_skip(path: Path, source_root: Path) -> bool:
    try:
        rel = path.relative_to(source_root)
    except ValueError:
        return True
    if not rel.parts:
        return False
    return rel.parts[0] in EXCLUDED_TOP_LEVEL


def copy_tree(source_root: Path, content_root: Path, static_root: Path) -> None:
    if content_root.exists():
        shutil.rmtree(content_root)
    if static_root.exists():
        shutil.rmtree(static_root)

    content_root.mkdir(parents=True, exist_ok=True)
    static_root.mkdir(parents=True, exist_ok=True)

    for source in source_root.rglob("*"):
        if source.is_dir() or should_skip(source, source_root):
            continue

        rel = source.relative_to(source_root)
        if source.suffix.lower() in CONTENT_SUFFIXES:
            target = content_root / rel
        else:
            target = static_root / rel

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def main() -> None:
    site_root = Path(__file__).resolve().parents[1]
    repo_root = site_root.parent
    source_root = repo_root / "docs"
    content_root = site_root / "content" / "docs"
    static_root = site_root / "static" / "docs"

    if not source_root.exists():
        raise FileNotFoundError(f"source docs directory not found: {source_root}")

    copy_tree(source_root, content_root, static_root)
    print(f"synced docs from {source_root} to {content_root}")
    print(f"synced static assets from {source_root} to {static_root}")


if __name__ == "__main__":
    main()
