#!/usr/bin/env python3
"""
Bumps the patch version in a SKILL.md frontmatter metadata.version field.
Usage: python bump_version.py <path/to/SKILL.md>
"""

import sys
import re


def bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Unexpected version format: {version!r}")
    major, minor, patch = parts
    return f"{major}.{minor}.{int(patch) + 1}"


def main():
    if len(sys.argv) < 2:
        print("Usage: bump_version.py <SKILL.md>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match:  version: "1.2.3"  or  version: '1.2.3'  or  version: 1.2.3
    pattern = re.compile(
        r'(?P<key>version:\s*)(?P<q>["\']?)(?P<ver>\d+\.\d+\.\d+)(?P=q)'
    )

    match = pattern.search(content)
    if not match:
        print(f"No version field found in {path}", file=sys.stderr)
        sys.exit(1)

    old_ver = match.group("ver")
    new_ver = bump_patch(old_ver)
    q = match.group("q")

    new_content = pattern.sub(
        lambda m: f'{m.group("key")}{q}{new_ver}{q}',
        content,
        count=1,
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  {old_ver} -> {new_ver}")


if __name__ == "__main__":
    main()
