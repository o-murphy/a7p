#!/usr/bin/env python3
"""Copies new entries from the repo root's CHANGELOG.md into each package's
own CHANGELOG.md (py/js/dart/go) -- the only source of truth for changelog
*content* is the root file; this just distributes it, since each package's
registry (pub.dev, generally npm/PyPI too, and -- for consistency with the
other three, even though pkg.go.dev doesn't require it -- go/) expects to
find one in the published package.

Unlike a from-scratch monorepo, py/js/dart/go each carry real pre-merge
history in their own CHANGELOG.md (from back when they were independent
repos) that this script must never touch. So instead of regenerating each
file wholesale, this only replaces the content between two HTML-comment
markers already present in each package's CHANGELOG.md:

    <!-- BEGIN AUTO-GENERATED FROM ROOT CHANGELOG.md -->
    ...
    <!-- END AUTO-GENERATED FROM ROOT CHANGELOG.md -->

Everything outside those markers (the frozen pre-merge history) is left
exactly as-is.

Root file format: version headings ("## [X]" or "## [X] - DATE"), each
containing zero or more "### <pkg>/" subsections (pkg in py/js/dart/go) with
"#### Added"/"#### Changed"/etc. sub-headings one level deeper than each
package's own file uses (its file has no "### <pkg>/" wrapper of its own).

The root file also ends with Keep-a-Changelog-style reference link
definitions ("[1.2.0]: https://.../releases/tag/v1.2.0") that make each
"## [X]" heading clickable. Each package's own CHANGELOG.md gets its own
copy of the ones its included headings actually use, not just a mention of
them -- pub.dev/npm/PyPI/pkg.go.dev all render a package's CHANGELOG.md in
isolation, with no access to the root file's definitions, so a heading
without its own matching "[X]: url" line renders as dead text there.

Usage: scripts/ci/sync_changelogs.py [pkg ...]
  No args: syncs py/CHANGELOG.md, js/CHANGELOG.md, dart/CHANGELOG.md,
  go/CHANGELOG.md. With args, only the named package(s), e.g.:
    scripts/ci/sync_changelogs.py dart
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGES = ("py", "js", "dart", "go")

VERSION_HEADING_RE = re.compile(r"^## \[(?P<version>[^\]]+)\](?P<rest>.*)$")
PKG_HEADING_RE = re.compile(r"^### (?P<pkg>\w+)/\s*$")
LINK_REF_RE = re.compile(r"^\[.+\]:\s")
LINK_LABEL_RE = re.compile(r"^\[(?P<label>[^\]]+)\]:\s")

BEGIN_MARKER = "<!-- BEGIN AUTO-GENERATED FROM ROOT CHANGELOG.md -->"
END_MARKER = "<!-- END AUTO-GENERATED FROM ROOT CHANGELOG.md -->"


def parse_root(text: str):
    """Returns (versions, link_refs).

    versions is a list of (heading_line, {pkg: [content_lines]}) in source
    order. link_refs is an ordered {label: full_line} dict of the
    reference-style link definitions at the end of the file (e.g. label
    "1.2.0" -> "[1.2.0]: https://.../releases/tag/v1.2.0"), so
    render_package_block can pull out just the ones a package's included
    headings actually reference.
    """
    lines = text.splitlines()
    versions = []
    link_refs: dict[str, str] = {}
    heading = None
    sections: dict[str, list[str]] | None = None
    i = 0
    while i < len(lines):
        line = lines[i]
        m_link = LINK_LABEL_RE.match(line)
        if m_link:
            link_refs[m_link.group("label")] = line
            i += 1
            continue
        if VERSION_HEADING_RE.match(line):
            if heading is not None:
                versions.append((heading, sections))
            heading = line
            sections = {}
            i += 1
            continue
        if heading is not None:
            m = PKG_HEADING_RE.match(line)
            if m:
                pkg = m.group("pkg")
                i += 1
                content = []
                while (
                    i < len(lines)
                    and not VERSION_HEADING_RE.match(lines[i])
                    and not PKG_HEADING_RE.match(lines[i])
                    and not LINK_REF_RE.match(lines[i])
                ):
                    content.append(lines[i])
                    i += 1
                while content and not content[-1].strip():
                    content.pop()
                while content and not content[0].strip():
                    content.pop(0)
                sections[pkg] = content
                continue
        i += 1
    if heading is not None:
        versions.append((heading, sections))
    return versions, link_refs


def demote_headings(lines: list[str]) -> list[str]:
    """One "### <pkg>/" wrapper level is dropped per package, so its
    "#### Foo" sub-headings become "### Foo" in the per-package file."""
    return [line[1:] if line.startswith("#### ") else line for line in lines]


def render_package_block(
    pkg: str, versions: list[tuple[str, dict]], link_refs: dict[str, str]
) -> str:
    # "## [Unreleased]" always heads the block, Keep-a-Changelog-style, even
    # with no content of its own yet for this package -- otherwise a package
    # with nothing currently unreleased would have no place for the next
    # entry to go, and would misleadingly look like development stopped.
    unreleased_content: list[str] = []
    others: list[tuple[str, list[str]]] = []
    for heading, sections in versions:
        m = VERSION_HEADING_RE.match(heading)
        if m and m.group("version") == "Unreleased":
            unreleased_content = sections.get(pkg, [])
            continue
        if sections.get(pkg):
            others.append((heading, sections[pkg]))

    parts = ["## [Unreleased]"]
    if unreleased_content:
        parts.append("")
        parts.extend(demote_headings(unreleased_content))
    parts.append("")

    for heading, content in others:
        parts.append(heading)
        parts.append("")
        parts.extend(demote_headings(content))
        parts.append("")

    while parts and parts[-1] == "":
        parts.pop()

    # Only the labels this package's block actually references (not every
    # link in the root file -- a package that was never part of an older
    # version shouldn't get a dangling, unused reference definition for it),
    # in the root file's order.
    referenced_labels = ["Unreleased"] + [
        m.group("version") for h, _ in others if (m := VERSION_HEADING_RE.match(h))
    ]
    refs = [link_refs[label] for label in referenced_labels if label in link_refs]
    if refs:
        parts.append("")
        parts.extend(refs)

    return "\n".join(parts)


def sync_package(
    pkg: str, versions: list[tuple[str, dict]], link_refs: dict[str, str]
) -> None:
    dest = REPO_ROOT / pkg / "CHANGELOG.md"
    text = dest.read_text()

    if BEGIN_MARKER not in text or END_MARKER not in text:
        sys.exit(
            f"{dest.relative_to(REPO_ROOT)} is missing the "
            f"'{BEGIN_MARKER}' / '{END_MARKER}' markers -- add them once by "
            "hand (see py/CHANGELOG.md for the expected shape) before this "
            "script can sync into it."
        )

    before, rest = text.split(BEGIN_MARKER, 1)
    _old_block, after = rest.split(END_MARKER, 1)

    block = render_package_block(pkg, versions, link_refs)
    new_text = f"{before}{BEGIN_MARKER}\n{block}\n{END_MARKER}{after}"

    dest.write_text(new_text)
    print(f"Synced {dest.relative_to(REPO_ROOT)}")


def main() -> int:
    requested = sys.argv[1:] or list(PACKAGES)
    unknown = set(requested) - set(PACKAGES)
    if unknown:
        print(
            f"Unknown package(s): {', '.join(sorted(unknown))} (expected: {', '.join(PACKAGES)})",
            file=sys.stderr,
        )
        return 1

    versions, link_refs = parse_root((REPO_ROOT / "CHANGELOG.md").read_text())
    for pkg in requested:
        sync_package(pkg, versions, link_refs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
