from __future__ import annotations

import os
import re
import subprocess
import sys
import json
import urllib.error
import urllib.request
from pathlib import Path

import yaml


REMOTE_URL = os.environ.get("NOTE_HISTORY_REMOTE", "https://github.com/Abiesjqq/Abies_Notebook.git")
REMOTE_REF = os.environ.get("NOTE_HISTORY_REF", "main")
CACHE_DIR_NAME = os.environ.get("NOTE_HISTORY_CACHE", ".cache/abies-notebook-history")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
KNOWN_GITHUB_AUTHORS = {
    "1508729918@qq.com": {
        "login": "Abiesjqq",
        "name": "Abiesjqq",
        "avatar": "https://avatars.githubusercontent.com/u/190385647?v=4&size=96",
    },
    "noflowerzzk@outlook.com": {
        "login": "Noflowerzzk",
        "name": "Noflowerzzk",
        "avatar": "https://avatars.githubusercontent.com/u/79004773?v=4&size=96",
    },
}
PROFILE_CACHE: dict[str, dict] = {}


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


def github_login_from_noreply(email: str) -> str | None:
    match = re.search(r"(?:\d+\+)?([^@]+)@users\.noreply\.github\.com\Z", email, re.IGNORECASE)
    if not match:
        return None
    login = match.group(1)
    if login.endswith("[bot]"):
        return None
    return login


def enrich_author(name: str, email: str) -> dict | None:
    if name.endswith("[bot]") or email.endswith("@users.noreply.github.com") and "[bot]" in email:
        return None

    known = KNOWN_GITHUB_AUTHORS.get(email.lower())
    login = github_login_from_noreply(email)
    if known:
        login = known["login"]
        display_name = known["name"]
        avatar = known["avatar"]
    elif login:
        display_name = login
        avatar = f"https://github.com/{login}.png?size=96"
    else:
        display_name = name
        avatar = f"https://github.com/identicons/{email}.png"

    profile = f"https://github.com/{login}" if login else None
    author = {
        "name": display_name,
        "email": email,
        "avatar": avatar,
    }
    if login:
        author["login"] = login
    if profile:
        author["url"] = profile
        author.update(fetch_github_profile(login))
    return author


def fetch_github_profile(login: str) -> dict:
    if login in PROFILE_CACHE:
        return PROFILE_CACHE[login]

    url = f"https://api.github.com/users/{login}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Noflowerzzk-site-build",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"warning: failed to fetch GitHub profile for {login}: {exc}", file=sys.stderr)
        PROFILE_CACHE[login] = {}
        return {}

    profile = {}
    for key in ("name", "bio", "company", "location", "blog", "twitter_username"):
        value = payload.get(key)
        if value:
            profile[key] = value
    if payload.get("html_url"):
        profile["url"] = payload["html_url"]
    if payload.get("avatar_url"):
        profile["avatar"] = f"{payload['avatar_url']}&size=96"
    PROFILE_CACHE[login] = profile
    return profile


def authors_for_path(repo: Path, source_path: str) -> list[dict]:
    ref_path = f"origin/{REMOTE_REF}"
    try:
        result = run_git(
            ["log", "--follow", "--reverse", "--format=%an%x00%ae", ref_path, "--", source_path],
            cwd=repo,
        )
    except subprocess.CalledProcessError as exc:
        print(f"warning: failed to read authors for {source_path}: {exc.stderr.strip()}", file=sys.stderr)
        return []

    authors = []
    seen = set()
    for line in result.stdout.splitlines():
        if "\0" not in line:
            continue
        name, email = line.split("\0", 1)
        key = email.lower()
        if key in seen:
            continue
        seen.add(key)
        author = enrich_author(name.strip(), email.strip())
        if author:
            authors.append(author)
    return authors


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


def apply_metadata_to_file(path: Path, created: str, updated: str, authors: list[dict]) -> bool:
    data, body = load_frontmatter(path)
    changed = False

    if data.get("date") != created:
        data["date"] = created
        changed = True
    if data.get("lastmod") != updated:
        data["lastmod"] = updated
        changed = True
    if authors and data.get("authors") != authors:
        data["authors"] = authors
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
    author_cache: dict[str, list[dict]] = {}
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
        authors = author_cache.get(source_path)
        if authors is None:
            authors = authors_for_path(repo, source_path)
            author_cache[source_path] = authors

        matched += 1
        if apply_metadata_to_file(path, dates[0], dates[1], authors):
            changed += 1

    print(f"applied commit metadata to {matched} generated pages ({changed} changed)")


if __name__ == "__main__":
    main()
