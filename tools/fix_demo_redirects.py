from __future__ import annotations

from pathlib import Path


REDIRECTS = {
    "docs/NoflowersNotes/ComputerVision/CNN/activation_functions.html": "/docs/NoflowersNotes/ComputerVision/CNN/activation_functions/",
    "docs/NoflowersNotes/人工智能基础/启发式搜索算法/a_star.html": "/docs/NoflowersNotes/人工智能基础/启发式搜索算法/a_star/",
}


def redirect_html(target: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={target}">
  <link rel="canonical" href="{target}">
  <script>location.replace({target!r});</script>
  <title>Redirecting…</title>
</head>
<body>
  <p>Redirecting to <a href="{target}">{target}</a> …</p>
</body>
</html>
"""


def main() -> None:
    site_root = Path(__file__).resolve().parents[1]
    public_root = site_root / "public"
    updated = 0
    for rel_path, target in REDIRECTS.items():
        path = public_root / rel_path
        if not path.exists():
            continue
        path.write_text(redirect_html(target), encoding="utf-8")
        updated += 1
    print(f"updated {updated} demo redirect files")


if __name__ == "__main__":
    main()
