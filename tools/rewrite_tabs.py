from __future__ import annotations

import re
import sys
from pathlib import Path


TAB_RE = re.compile(r'^(?P<indent>\s*)===(?P<selected>\+)?\s+"(?P<title>[^"]+)"\s*$')
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def escape_attr(value: str) -> str:
    return value.replace('"', '\\"')


def strip_block_indent(line: str, base_indent: int) -> str:
    if not line.strip():
        return ""
    current = len(line) - len(line.lstrip(" "))
    target = min(len(line), base_indent + 4)
    if current >= target:
        return line[target:]
    if current > base_indent:
        return line[current:]
    return line


def collect_tab(lines: list[str], start: int) -> tuple[int, dict[str, object]]:
    match = TAB_RE.match(lines[start])
    if not match:
        raise ValueError("collect_tab called on a non-tab line")

    base_indent = len(match.group("indent"))
    tab: dict[str, object] = {
        "title": match.group("title"),
        "selected": bool(match.group("selected")),
        "body": [],
    }

    body: list[str] = []
    i = start + 1
    while i < len(lines):
        line = lines[i]
        sibling = TAB_RE.match(line)
        if sibling and len(sibling.group("indent")) == base_indent:
            break
        if not line.strip():
            body.append("")
            i += 1
            continue
        current_indent = len(line) - len(line.lstrip(" "))
        if current_indent <= base_indent:
            break
        body.append(strip_block_indent(line, base_indent))
        i += 1

    tab["body"] = transform_lines(body)
    return i, tab


def render_tabs(tabs: list[dict[str, object]]) -> list[str]:
    output = ["{{< tabs >}}", ""]
    for index, tab in enumerate(tabs):
        opening = f'  {{{{< tab name="{escape_attr(str(tab["title"]))}"'
        if tab["selected"] or (index == 0 and not any(item["selected"] for item in tabs)):
            opening += " selected=true"
        opening += " >}}"

        output.append(opening)
        output.extend(str(line) for line in tab["body"])
        output.append("  {{< /tab >}}")
        output.append("")
    output.append("{{< /tabs >}}")
    return output


def transform_lines(lines: list[str]) -> list[str]:
    output: list[str] = []
    i = 0
    in_fence = False

    while i < len(lines):
        if FENCE_RE.match(lines[i]):
            in_fence = not in_fence
            output.append(lines[i])
            i += 1
            continue

        if in_fence:
            output.append(lines[i])
            i += 1
            continue

        match = TAB_RE.match(lines[i])
        if not match:
            output.append(lines[i])
            i += 1
            continue

        base_indent = len(match.group("indent"))
        tabs: list[dict[str, object]] = []
        while i < len(lines):
            sibling = TAB_RE.match(lines[i])
            if not sibling or len(sibling.group("indent")) != base_indent:
                break
            i, tab = collect_tab(lines, i)
            tabs.append(tab)
            while i < len(lines) and not lines[i].strip():
                i += 1

        output.extend(render_tabs(tabs))

    return output


def rewrite_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    transformed = "\n".join(transform_lines(original.splitlines()))
    if original.endswith("\n"):
        transformed += "\n"
    if transformed == original:
        return False
    path.write_text(transformed, encoding="utf-8")
    return True


def main() -> None:
    if len(sys.argv) > 1:
        content_root = Path(sys.argv[1]).resolve()
    else:
        content_root = Path(__file__).resolve().parents[1] / "content" / "docs"
    changed = 0
    for path in content_root.rglob("*.md"):
        if rewrite_file(path):
            changed += 1
            print(path.relative_to(content_root.parent))
    print(f"updated {changed} files")


if __name__ == "__main__":
    main()
