from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import yaml


REMOTE_URL = os.environ.get("NOTE_HISTORY_REMOTE", "https://github.com/Abiesjqq/Abies_Notebook.git")
REMOTE_REF = os.environ.get("NOTE_HISTORY_REF", "main")
CACHE_DIR_NAME = os.environ.get("NOTE_HISTORY_CACHE", ".cache/abies-notebook-history")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)


def run_git(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=cwd,
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def ensure_history_repo(site_root: Path) -> Path | None:
    cache_dir = site_root / CACHE_DIR_NAME
    if not cache_dir.exists():
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            run_git(["clone", "--filter=blob:none", "--no-checkout", REMOTE_URL, str(cache_dir)], cwd=site_root)
        except subprocess.CalledProcessError as exc:
            print(f"warning: failed to clone commit-date source: {exc.stderr.strip()}", file=sys.stderr)
            return None

    try:
        run_git(["fetch", "origin", f"{REMOTE_REF}:refs/remotes/origin/{REMOTE_REF}"], cwd=cache_dir)
    except subprocess.CalledProcessError as exc:
        print(f"warning: failed to fetch commit-date source: {exc.stderr.strip()}", file=sys.stderr)
        return None

    return cache_dir


def load_old_paths(repo: Path) -> set[str]:
    result = run_git(["ls-tree", "-r", "--name-only", f"origin/{REMOTE_REF}"], cwd=repo)
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def generated_rel_to_source_candidates(rel_path: str) -> list[str]:
    normalized = rel_path.replace("\\", "/")
    if normalized.endswith("/_index.md"):
        normalized = normalized[: -len("/_index.md")] + "/index.md"
    elif normalized == "_index.md":
        normalized = "index.md"

    return [
        f"docs/{normalized}",
        normalized,
    ]


def commit_dates_for_path(repo: Path, source_path: str) -> tuple[str, str] | None:
    ref_path = f"origin/{REMOTE_REF}"
    try:
        created = run_git(
            ["log", "--follow", "--format=%aI", "--reverse", ref_path, "--", source_path],
            cwd=repo,
        ).stdout.splitlines()
        updated = run_git(
            ["log", "--follow", "-1", "--format=%aI", ref_path, "--", source_path],
            cwd=repo,
        ).stdout.splitlines()
    except subprocess.CalledProcessError as exc:
        print(f"warning: failed to read commit dates for {source_path}: {exc.stderr.strip()}", file=sys.stderr)
        return None

    if not created or not updated:
        return None
    return created[0].strip(), updated[0].strip()


def load_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    return yaml.safe_load(match.group(1)) or {}, text[match.end() :]


def dump_frontmatter(data: dict, body: str) -> str:
    frontmatter = yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip()
    body = body.lstrip("\n")
    if body:
        return f"---\n{frontmatter}\n---\n\n{body}"
    return f"---\n{frontmatter}\n---\n"


def apply_dates_to_file(path: Path, created: str, updated: str) -> bool:
    data, body = load_frontmatter(path)
    changed = False

    if data.get("date") != created:
        data["date"] = created
        changed = True
    if data.get("lastmod") != updated:
        data["lastmod"] = updated
        changed = True

    if changed:
        path.write_text(dump_frontmatter(data, body), encoding="utf-8")
    return changed


def main() -> None:
    site_root = Path(__file__).resolve().parents[1]
    docs_root = site_root / "generated-content" / "docs"
    if os.environ.get("NOTE_HISTORY_DISABLE") == "1":
        print("commit-date sync skipped because NOTE_HISTORY_DISABLE=1")
        return
    if not docs_root.exists():
        raise FileNotFoundError(f"generated docs root not found: {docs_root}")

    repo = ensure_history_repo(site_root)
    if repo is None:
        print("commit-date sync skipped")
        return

    old_paths = load_old_paths(repo)
    date_cache: dict[str, tuple[str, str]] = {}
    matched = 0
    changed = 0

    for path in docs_root.rglob("*.md"):
        rel_path = path.relative_to(docs_root).as_posix()
        source_path = next((candidate for candidate in generated_rel_to_source_candidates(rel_path) if candidate in old_paths), None)
        if source_path is None:
            continue

        dates = date_cache.get(source_path)
        if dates is None:
            dates = commit_dates_for_path(repo, source_path)
            if dates is None:
                continue
            date_cache[source_path] = dates

        matched += 1
        if apply_dates_to_file(path, dates[0], dates[1]):
            changed += 1

    print(f"applied commit dates to {matched} generated pages ({changed} changed)")


if __name__ == "__main__":
    main()
