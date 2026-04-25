from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
import re


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)


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
        import yaml

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

    import yaml

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


def main() -> None:
    site_root = Path(__file__).resolve().parents[1]
    source_root = site_root / "content"
    generated_root = site_root / "generated-content"

    if generated_root.exists():
        shutil.rmtree(generated_root)
    shutil.copytree(source_root, generated_root)
    convert_section_indexes(generated_root)
    ensure_docs_section_frontmatter(generated_root)

    subprocess.run(
        [sys.executable, str(site_root / "tools" / "rewrite_admonitions.py"), str(generated_root / "docs")],
        check=True,
        cwd=site_root,
    )
    subprocess.run(
        [sys.executable, str(site_root / "tools" / "generate_section_indexes.py")],
        check=True,
        cwd=site_root,
    )

    print(f"prepared generated content at {generated_root}")


if __name__ == "__main__":
    main()
