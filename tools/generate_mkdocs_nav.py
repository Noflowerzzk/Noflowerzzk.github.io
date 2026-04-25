from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

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


def to_page_ref(value: str) -> str:
    normalized = value.replace("\\", "/").strip("/")
    def encode_path(path: str) -> str:
        return "/".join(quote(part, safe="") for part in path.split("/") if part)
    if normalized == "index.md":
        return "/docs/"
    if normalized.endswith("/index.md"):
        normalized = normalized[: -len("/index.md")]
        return f"/docs/{encode_path(normalized)}/"
    if normalized.endswith(".md") or normalized.endswith(".ipynb"):
        normalized = normalized.rsplit(".", 1)[0]
        return f"/docs/{encode_path(normalized)}/"
    return f"/docs/{encode_path(normalized)}/"


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def convert_entry(entry) -> dict:
    if isinstance(entry, dict):
        title, value = next(iter(entry.items()))
        if isinstance(value, str):
            href = to_page_ref(value)
            return {
                "title": title,
                "href": href,
                "children": [],
                "page_refs": [href],
            }
        if isinstance(value, list):
            children = [convert_entry(child) for child in value]
            page_refs: list[str] = []
            for child in children:
                page_refs.extend(child["page_refs"])
            return {
                "title": title,
                "href": "",
                "children": children,
                "page_refs": dedupe(page_refs),
            }
    raise ValueError(f"Unsupported nav entry: {entry!r}")


def flatten_entry(entry) -> list[dict]:
    if isinstance(entry, dict):
        title, value = next(iter(entry.items()))
        if isinstance(value, str):
            href = to_page_ref(value)
            return [{"title": title, "href": href}]
        if isinstance(value, list):
            result: list[dict] = []
            for child in value:
                result.extend(flatten_entry(child))
            return result
    raise ValueError(f"Unsupported nav entry: {entry!r}")


def main() -> None:
    site_root = Path(__file__).resolve().parents[1]
    mkdocs_path = site_root / "mkdocs.yml"
    if not mkdocs_path.exists():
        fallback = site_root.parent / "mkdocs.yml"
        if fallback.exists():
            mkdocs_path = fallback
        else:
            raise FileNotFoundError(f"mkdocs.yml not found in {site_root} or parent directory")
    output_path = site_root / "data" / "mkdocs_nav.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = yaml.load(mkdocs_path.read_text(encoding="utf-8"), Loader=LenientLoader)
    nav_entries = data.get("nav", [])
    branches = [convert_entry(entry) for entry in nav_entries]
    linear_pages: list[dict] = []
    for entry in nav_entries:
        linear_pages.extend(flatten_entry(entry))
    output_path.write_text(
        json.dumps({"branches": branches, "linear_pages": linear_pages}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
