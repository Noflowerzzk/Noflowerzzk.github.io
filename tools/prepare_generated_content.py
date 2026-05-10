from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
import re

import yaml


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
CONTENT_PAGE_SUFFIXES = {".md", ".ipynb", ".html"}


class LenientLoader(yaml.SafeLoader):
    pass


def construct_unknown_tag(loader: yaml.Loader, node: yaml.Node) -> object:
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


LenientLoader.add_multi_constructor("!", lambda loader, suffix, node: construct_unknown_tag(loader, node))
LenientLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/name:",
    lambda loader, suffix, node: loader.construct_scalar(node),
)


def collect_nav_content_paths(site_root: Path) -> set[str]:
    mkdocs_path = site_root / "mkdocs.yml"
    if not mkdocs_path.exists():
        return set()

    data = yaml.load(mkdocs_path.read_text(encoding="utf-8"), Loader=LenientLoader) or {}
    keep_paths: set[str] = set()

    def visit(entries: object) -> None:
        if isinstance(entries, list):
            for entry in entries:
                visit(entry)
            return
        if isinstance(entries, dict):
            for value in entries.values():
                if isinstance(value, str):
                    path = value.replace("\\", "/").strip("/")
                    if Path(path).suffix.lower() in CONTENT_PAGE_SUFFIXES:
                        keep_paths.add(path)
                else:
                    visit(value)

    visit(data.get("nav", []))
    return keep_paths


def ensure_docs_section_frontmatter(generated_root: Path) -> None:
    docs_index = generated_root / "docs" / "_index.md"
    if not docs_index.exists():
        return

    text = docs_index.read_text(encoding="utf-8")
    frontmatter = {
        "type": "docs",
        "cascade": {"type": "docs"},
    }

    match = FRONTMATTER_RE.match(text)
    if match:
        data = yaml.safe_load(match.group(1)) or {}
        changed = False
        if data.get("type") != "docs":
            data["type"] = "docs"
            changed = True
        cascade = data.get("cascade")
        if not isinstance(cascade, dict) or cascade.get("type") != "docs":
            data["cascade"] = {"type": "docs"}
            changed = True
        if changed:
            body = text[match.end() :].lstrip("\n")
            docs_index.write_text(
                "---\n"
                + yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip()
                + "\n---\n\n"
                + body,
                encoding="utf-8",
            )
        return

    docs_index.write_text(
        "---\n"
        + yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
        + "\n---\n\n"
        + text.lstrip("\n"),
        encoding="utf-8",
    )


def convert_section_indexes(generated_root: Path) -> None:
    for index_path in generated_root.rglob("index.md"):
        parent = index_path.parent
        has_children = any(child.is_dir() for child in parent.iterdir() if child.name != ".gitkeep")
        has_peer_content = any(
            child.is_file()
            and child.name != "index.md"
            and child.suffix.lower() in {".md", ".ipynb"}
            for child in parent.iterdir()
        )
        if not has_children and not has_peer_content:
            continue
        target = parent / "_index.md"
        target.write_text(index_path.read_text(encoding="utf-8"), encoding="utf-8")
        index_path.unlink()


def prune_disabled_docs(generated_root: Path) -> None:
    for rel_path in [
        Path("docs") / "notices",
    ]:
        target = generated_root / rel_path
        if target.exists():
            shutil.rmtree(target)


def prune_unlisted_content(generated_root: Path, keep_paths: set[str]) -> None:
    if not keep_paths:
        return

    docs_root = generated_root / "docs"
    if not docs_root.exists():
        return

    for path in docs_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CONTENT_PAGE_SUFFIXES:
            continue
        rel_path = path.relative_to(docs_root).as_posix()
        if rel_path not in keep_paths:
            path.unlink()

    for path in sorted((p for p in docs_root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if not any(path.iterdir()):
            path.rmdir()


def main() -> None:
    site_root = Path(__file__).resolve().parents[1]
    source_root = site_root / "content"
    generated_root = site_root / "generated-content"
    nav_content_paths = collect_nav_content_paths(site_root)

    if generated_root.exists():
        shutil.rmtree(generated_root)
    shutil.copytree(source_root, generated_root)
    prune_disabled_docs(generated_root)
    prune_unlisted_content(generated_root, nav_content_paths)
    convert_section_indexes(generated_root)
    ensure_docs_section_frontmatter(generated_root)

    subprocess.run(
        [sys.executable, str(site_root / "tools" / "rewrite_admonitions.py"), str(generated_root / "docs")],
        check=True,
        cwd=site_root,
    )
    subprocess.run(
        [sys.executable, str(site_root / "tools" / "rewrite_tabs.py"), str(generated_root / "docs")],
        check=True,
        cwd=site_root,
    )
    subprocess.run(
        [sys.executable, str(site_root / "tools" / "generate_section_indexes.py")],
        check=True,
        cwd=site_root,
    )
    subprocess.run(
        [sys.executable, str(site_root / "tools" / "apply_commit_dates.py")],
        check=True,
        cwd=site_root,
    )

    print(f"prepared generated content at {generated_root}")


if __name__ == "__main__":
    main()
