from __future__ import annotations

import re
import sys
from pathlib import Path


MKDOCS_RE = re.compile(r"^(?P<indent>\s*)!!!\s+(?P<type>[A-Za-z0-9_-]+)(?:\s+\"(?P<title>[^\"]*)\")?\s*$")
ALERT_RE = re.compile(r"^(?P<prefix>>\s*)?\[!(?P<type>[A-Za-z]+)\]\s*$")
STRONG_TITLE_RE = re.compile(r"^\*\*(?P<title>.+?)\*\*$")
QUOTED_TITLE_RE = re.compile(r'^"(?P<title>.+)"$')
SHORTCODE_TITLE_RE = re.compile(r'title="([^"]*)"')


def escape_attr(value: str) -> str:
    return value.replace('"', '\\"')


def strip_quote(line: str) -> str:
    if line.startswith("> "):
        return line[2:]
    if line.startswith(">"):
        return line[1:]
    return line


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


def extract_alert_title(lines: list[str]) -> tuple[str | None, list[str]]:
    index = 0
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index >= len(lines):
        return None, lines

    raw = lines[index].strip()
    match = STRONG_TITLE_RE.match(raw) or QUOTED_TITLE_RE.match(raw)
    if not match:
        return None, lines

    title = match.group("title").strip()
    remaining = lines[:index] + lines[index + 1 :]
    while remaining and not remaining[0].strip():
        remaining.pop(0)
    return title, remaining


def collect_alert(lines: list[str], start: int) -> tuple[int, list[str], str]:
    match = ALERT_RE.match(lines[start])
    alert_type = match.group("type").lower()
    quoted = bool(match.group("prefix"))
    block: list[str] = []
    i = start + 1
    while i < len(lines):
        line = lines[i]
        if quoted:
            if line.startswith(">"):
                block.append(strip_quote(line))
                i += 1
                continue
            if not line.strip():
                block.append("")
                i += 1
                continue
            break
        if ALERT_RE.match(line) or MKDOCS_RE.match(line):
            break
        block.append(line)
        i += 1
    return i, block, alert_type


def collect_mkdocs(lines: list[str], start: int) -> tuple[int, list[str], str, str | None]:
    match = MKDOCS_RE.match(lines[start])
    base_indent = len(match.group("indent"))
    admonition_type = match.group("type").lower()
    title = match.group("title")
    block: list[str] = []
    i = start + 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            block.append("")
            i += 1
            continue
        current_indent = len(line) - len(line.lstrip(" "))
        if current_indent <= base_indent:
            break
        block.append(strip_block_indent(line, base_indent))
        i += 1
    return i, block, admonition_type, title


def render_shortcode(admonition_type: str, body: list[str], title: str | None = None) -> list[str]:
    opening = f'{{{{% mkadmonition type="{escape_attr(admonition_type)}"'
    if title:
        opening += f' title="{escape_attr(title)}"'
    opening += " %}}"
    result = [opening]
    result.extend(body)
    result.append("{{% /mkadmonition %}}")
    return result


def transform_lines(lines: list[str]) -> list[str]:
    output: list[str] = []
    i = 0
    while i < len(lines):
        alert_match = ALERT_RE.match(lines[i])
        mkdocs_match = MKDOCS_RE.match(lines[i])

        if alert_match:
            i, block, alert_type = collect_alert(lines, i)
            title, block = extract_alert_title(block)
            transformed = transform_lines(block)
            output.extend(render_shortcode(alert_type, transformed, title))
            continue

        if mkdocs_match:
            i, block, admonition_type, title = collect_mkdocs(lines, i)
            transformed = transform_lines(block)
            output.extend(render_shortcode(admonition_type, transformed, title))
            continue

        output.append(lines[i])
        i += 1

    return output


def rewrite_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    transformed = "\n".join(transform_lines(original.splitlines()))
    transformed = SHORTCODE_TITLE_RE.sub(lambda m: f'title="{m.group(1).replace("\\\\", "\\")}"', transformed)
    if transformed == original:
        return False
    if original.endswith("\n"):
        transformed += "\n"
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
