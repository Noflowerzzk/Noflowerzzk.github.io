from __future__ import annotations

import re
from pathlib import Path


OPEN_RE = re.compile(
    r'^(?P<indent>\s*)\{\{% admonition type="(?P<type>[^"]+)"(?: title="(?P<title>[^"]*)")? %\}\}\s*$'
)
CLOSE_RE = re.compile(r"^\s*\{\{% /admonition %\}\}\s*$")


def parse_block(lines: list[str], start: int = 0) -> tuple[list[str], int]:
    output: list[str] = []
    i = start

    while i < len(lines):
        if CLOSE_RE.match(lines[i]):
            return output, i + 1

        match = OPEN_RE.match(lines[i])
        if not match:
            output.append(lines[i])
            i += 1
            continue

        indent = match.group("indent")
        admonition_type = match.group("type")
        title = match.group("title")
        inner, i = parse_block(lines, i + 1)

        header = f"{indent}!!! {admonition_type}"
        if title:
            header += f' "{title}"'
        output.append(header)

        if inner:
            for line in inner:
                if line.strip():
                    output.append(f"{indent}    {line}")
                else:
                    output.append("")
        else:
            output.append("")

    return output, i


def rewrite_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    transformed_lines, _ = parse_block(original.splitlines())
    transformed = "\n".join(transformed_lines)
    if original.endswith("\n"):
        transformed += "\n"
    if transformed == original:
        return False
    path.write_text(transformed, encoding="utf-8")
    return True


def main() -> None:
    content_root = Path(__file__).resolve().parents[1] / "content"
    changed = 0
    for path in content_root.rglob("*.md"):
        if rewrite_file(path):
            changed += 1
            print(path.relative_to(content_root))
    print(f"updated {changed} files")


if __name__ == "__main__":
    main()
