from __future__ import annotations

import re
from pathlib import Path

import yaml


class LenientLoader(yaml.SafeLoader):
    pass


def construct_unknown_tag(loader: yaml.SafeLoader, tag_suffix: str, node: yaml.Node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


LenientLoader.add_multi_constructor("", construct_unknown_tag)


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip("/")


def load_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    body = text[match.end() :]
    return data, body


def dump_frontmatter(data: dict, body: str) -> str:
    frontmatter = yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip()
    body = body.lstrip("\n")
    if body:
        return f"---\n{frontmatter}\n---\n\n{body}"
    return f"---\n{frontmatter}\n---\n"


def mkdocs_url_for_rel_path(rel_path: str) -> str:
    normalized = normalize_path(rel_path)
    if normalized == "index.md":
        return "/docs/"
    if normalized.endswith("/index.md"):
        return f"/docs/{normalized[:-len('/index.md')]}/"
    if normalized.endswith(".md") or normalized.endswith(".ipynb"):
        return f"/docs/{normalized.rsplit('.', 1)[0]}/"
    return f"/docs/{normalized}/"


def ensure_frontmatter(
    path: Path,
    title: str | None = None,
    weight: int | None = None,
    link_title: str | None = None,
    url: str | None = None,
    nav_path: list[dict] | None = None,
) -> None:
    if not path.exists():
        return
    data, body = load_frontmatter(path)
    changed = False
    if weight is not None and data.get("weight") != weight:
        data["weight"] = weight
        changed = True
    if title and not data.get("title"):
        data["title"] = title
        changed = True
    if link_title and data.get("linkTitle") != link_title:
        data["linkTitle"] = link_title
        changed = True
    if url and data.get("url") != url:
        data["url"] = url
        changed = True
    if nav_path and data.get("navPath") != nav_path:
        data["navPath"] = nav_path
        changed = True
    if changed:
        path.write_text(dump_frontmatter(data, body), encoding="utf-8")


def apply_entry(entry, docs_root: Path, weight: int, ancestors: list[dict] | None = None) -> None:
    ancestors = ancestors or []
    if not isinstance(entry, dict):
        return

    title, value = next(iter(entry.items()))
    if isinstance(value, str):
        rel_path = normalize_path(value)
        source_path = docs_root / rel_path
        url = mkdocs_url_for_rel_path(rel_path)
        ensure_frontmatter(
            source_path,
            title=title,
            weight=weight,
            link_title=title,
            url=url,
            nav_path=[*ancestors, {"title": title, "href": url}],
        )
        return

    if isinstance(value, list):
        branch_path = [*ancestors, {"title": title, "href": ""}]
        for child_weight, child in enumerate(value, start=1):
            apply_entry(child, docs_root, child_weight, branch_path)
        return


def ensure_default_frontmatter_for_all_pages(docs_root: Path) -> None:
    for path in docs_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name == "_index.md":
            continue
        if path.suffix.lower() not in {".md", ".ipynb"}:
            continue
        rel_path = normalize_path(path.relative_to(docs_root).as_posix())
        ensure_frontmatter(
            path,
            title=path.stem,
            url=mkdocs_url_for_rel_path(rel_path),
        )


def main() -> None:
    site_root = Path(__file__).resolve().parents[1]
    docs_root = site_root / "generated-content" / "docs"
    mkdocs_path = site_root / "mkdocs.yml"
    if not mkdocs_path.exists():
        fallback = site_root.parent / "mkdocs.yml"
        if fallback.exists():
            mkdocs_path = fallback
        else:
            raise FileNotFoundError(f"mkdocs.yml not found in {site_root} or parent directory")

    data = yaml.load(mkdocs_path.read_text(encoding="utf-8"), Loader=LenientLoader)
    nav = data.get("nav", [])
    for weight, entry in enumerate(nav, start=1):
        apply_entry(entry, docs_root, weight)
    ensure_default_frontmatter_for_all_pages(docs_root)


if __name__ == "__main__":
    main()
