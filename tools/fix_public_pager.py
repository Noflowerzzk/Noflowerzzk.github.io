from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote


PAGER_RE = re.compile(
    r'<div(?: data-mkdocs-pager="1")? class="hx:mb-8 hx:flex hx:items-center hx:border-t hx:pt-8 .*?</div>',
    re.DOTALL,
)


def rel_permalink_for_html(path: Path, public_root: Path) -> str:
    rel = path.relative_to(public_root).as_posix()
    rel = "/".join(quote(part, safe="") for part in rel.split("/"))
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def pager_html(prev_entry: dict | None, next_entry: dict | None) -> str:
    if not prev_entry and not next_entry:
        return ""

    parts = [
        '<div data-mkdocs-pager="1" class="hx:mb-8 hx:flex hx:items-center hx:border-t hx:pt-8 hx:border-gray-200 hx:dark:border-neutral-800 hx:contrast-more:border-neutral-400 hx:dark:contrast-more:border-neutral-400 hx:print:hidden">'
    ]
    if prev_entry:
        title = html.escape(prev_entry["title"], quote=True)
        href = html.escape(prev_entry["href"], quote=True)
        parts.append(
            f'<a href="{href}" title="{title}" class="hx:flex hx:max-w-[50%] hx:items-center hx:gap-1 hx:py-4 hx:text-base hx:font-medium hx:text-gray-600 hx:transition-colors [word-break:break-word] hx:hover:text-primary-600 hx:dark:text-gray-300 hx:md:text-lg hx:ltr:pr-4 hx:rtl:pl-4"><svg class="hx:inline hx:h-5 hx:shrink-0 hx:ltr:rotate-180" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>{title}</a>'
        )
    if next_entry:
        title = html.escape(next_entry["title"], quote=True)
        href = html.escape(next_entry["href"], quote=True)
        parts.append(
            f'<a href="{href}" title="{title}" class="hx:flex hx:max-w-[50%] hx:items-center hx:gap-1 hx:py-4 hx:text-base hx:font-medium hx:text-gray-600 hx:transition-colors [word-break:break-word] hx:hover:text-primary-600 hx:dark:text-gray-300 hx:md:text-lg hx:ltr:ml-auto hx:ltr:pl-4 hx:ltr:text-right hx:rtl:mr-auto hx:rtl:pr-4 hx:rtl:text-left">{title}<svg class="hx:inline hx:h-5 hx:shrink-0 hx:rtl:-rotate-180" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg></a>'
        )
    parts.append("</div>")
    return "".join(parts)


def main() -> None:
    site_root = Path(__file__).resolve().parents[1]
    public_root = site_root / "public"
    nav_data = json.loads((site_root / "data" / "mkdocs_nav.json").read_text(encoding="utf-8"))
    entries = nav_data.get("linear_pages", [])
    index_by_href = {entry["href"]: i for i, entry in enumerate(entries)}

    changed = 0
    for html_path in public_root.rglob("*.html"):
        current_href = rel_permalink_for_html(html_path, public_root)
        idx = index_by_href.get(current_href)
        if idx is None:
            continue

        prev_entry = entries[idx - 1] if idx > 0 else None
        next_entry = entries[idx + 1] if idx + 1 < len(entries) else None
        replacement = pager_html(prev_entry, next_entry)

        original = html_path.read_text(encoding="utf-8")
        updated = PAGER_RE.sub("", original, count=1)
        marker = "</main>"
        if replacement:
            updated = updated.replace(marker, replacement + marker, 1)
        if updated != original:
            html_path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"updated {changed} html files")


if __name__ == "__main__":
    main()
