#!/usr/bin/env python3
"""Prepares a release commit for the maintainer to review and push by hand
-- run this locally BEFORE tagging, never from CI. Release.yml's
verify-release job then only checks that the tag it was pushed for already
carries a consistent version/changelog everywhere; it refuses to publish
otherwise instead of trying to auto-fix things during the release run (that
auto-fix used to run in bump-versions as a commit pushed to main *after*
the tag already existed, which is exactly what made publish-py compute a
"1 commit past the tag" dev version that PyPI then rejected).

What this script does, all as uncommitted working-tree edits for you to
review with `git diff` and commit yourself:
  1. Renames CHANGELOG.md's "## [Unreleased]" heading to
     "## [VERSION] - DATE" and adds a fresh empty "## [Unreleased]" above it.
  2. Updates the reference-style links at the bottom of CHANGELOG.md
     (adds "[VERSION]: .../compare/PREV...VERSION", repoints "[Unreleased]").
  3. Bumps dart/pubspec.yaml and js/package.json to VERSION (py and go have
     no version field to bump -- see release.yml's comments on that).
  4. Runs sync_changelogs.py to regenerate py/js/dart/go/CHANGELOG.md.

It does NOT commit, tag, or push anything -- that's on you, after reviewing
the diff:
    git add -A && git commit -m "chore: prepare release VERSION"
    git push origin main
    git tag vVERSION && git push origin vVERSION

Usage: scripts/ci/prepare_release.py VERSION   (e.g. 1.2.3, no "v" prefix)
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPO_URL = "https://github.com/o-murphy/a7p"

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-.](?:alpha|beta|rc)\.?\d*)?$")
HEADING_RE = re.compile(r"^## \[(?P<version>[^\]]+)\]")
LINK_RE = re.compile(r"^\[(?P<label>[^\]]+)\]:\s")


def fail(msg: str) -> None:
    sys.exit(f"error: {msg}")


def check_clean_tree() -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    if status.strip():
        fail(
            "working tree isn't clean -- commit or stash your changes first "
            "so this script's edits are easy to review on their own."
        )


def update_changelog(version: str) -> str | None:
    """Returns the previous version label (for the compare link), or None
    if this is the first release."""
    path = REPO_ROOT / "CHANGELOG.md"
    lines = path.read_text().splitlines()

    unreleased_idx = next(
        (i for i, line in enumerate(lines) if line.strip() == "## [Unreleased]"),
        None,
    )
    if unreleased_idx is None:
        fail("CHANGELOG.md has no '## [Unreleased]' heading to rename.")

    body = lines[unreleased_idx + 1 :]
    next_heading_idx = next(
        (i for i, line in enumerate(body) if HEADING_RE.match(line)), len(body)
    )
    unreleased_body = [line for line in body[:next_heading_idx] if line.strip()]
    if not unreleased_body:
        fail(
            "CHANGELOG.md's '## [Unreleased]' section is empty -- add the "
            "release's changes there first."
        )

    prev_version = None
    m = HEADING_RE.match(body[next_heading_idx]) if next_heading_idx < len(body) else None
    if m:
        prev_version = m.group("version")

    new_heading = f"## [{version}] - {date.today().isoformat()}"

    lines[unreleased_idx : unreleased_idx + 1] = ["## [Unreleased]", "", new_heading]

    # Repoint/insert the reference-style links at the bottom of the file.
    link_idx = next((i for i, line in enumerate(lines) if LINK_RE.match(line)), None)
    if link_idx is None:
        fail("CHANGELOG.md has no reference-style links ('[X]: url') to update.")

    new_compare = (
        f"[{version}]: {REPO_URL}/compare/v{prev_version}...v{version}"
        if prev_version
        else f"[{version}]: {REPO_URL}/releases/tag/v{version}"
    )
    new_links = [f"[Unreleased]: {REPO_URL}/compare/v{version}...HEAD", new_compare]

    if LINK_RE.match(lines[link_idx]).group("label") == "Unreleased":
        lines[link_idx : link_idx + 1] = new_links
    else:
        lines[link_idx:link_idx] = new_links

    path.write_text("\n".join(lines) + "\n")
    print(f"Updated {path.relative_to(REPO_ROOT)}")
    return prev_version


def bump_field(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text()
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count == 0:
        fail(f"couldn't find a version field to bump in {path.relative_to(REPO_ROOT)}.")
    path.write_text(new_text)
    print(f"Bumped {path.relative_to(REPO_ROOT)}")


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: scripts/ci/prepare_release.py VERSION  (e.g. 1.2.3)")
    version = sys.argv[1].lstrip("v")
    if not VERSION_RE.match(version):
        fail(f"'{version}' doesn't look like a version (expected e.g. 1.2.3 or 1.2.3-rc.1).")

    check_clean_tree()
    update_changelog(version)
    bump_field(
        REPO_ROOT / "dart" / "pubspec.yaml",
        r"^version: .*$",
        f"version: {version}",
    )
    bump_field(
        REPO_ROOT / "js" / "package.json",
        r'^(  "version": ")[^"]*(")',
        rf"\g<1>{version}\g<2>",
    )

    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "ci" / "sync_changelogs.py")],
        cwd=REPO_ROOT,
        check=True,
    )

    print(
        f"\nReview with `git diff`, then:\n"
        f"  git add -A && git commit -m 'chore: prepare release {version}'\n"
        f"  git push origin main\n"
        f"  git tag v{version} && git push origin v{version}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
