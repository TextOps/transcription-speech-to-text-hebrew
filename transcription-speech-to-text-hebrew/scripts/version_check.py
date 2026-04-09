#!/usr/bin/env python3
"""
Checks whether the locally installed skill version is compatible with the
latest version published on GitHub.

Outputs one of:
  [OK] current=1.0.13 latest=1.0.13
  [UPDATE_AVAILABLE] current=1.0.10 latest=1.0.13
  [UPDATE_REQUIRED] current=1.0.9 min_compatible=1.0.13  <- breaking change
  [SKIP] <reason>   <- network error or parse failure, non-fatal
"""

import os
import re
import sys
import json
import urllib.request

GITHUB_VERSION_URL = (
    "https://raw.githubusercontent.com/textops/"
    "transcription-speech-to-text-hebrew/main/version.json"
)
TIMEOUT = 5


def _skill_dir() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _local_version() -> str:
    skill_md = os.path.join(_skill_dir(), "SKILL.md")
    with open(skill_md, encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'version:\s*["\']?(\d+\.\d+\.\d+)', content)
    if not m:
        raise ValueError("version not found in SKILL.md")
    return m.group(1)


def _fetch_remote() -> dict:
    req = urllib.request.Request(GITHUB_VERSION_URL, headers={"User-Agent": "skill-version-check"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode())


def _parse(v: str):
    return tuple(int(x) for x in v.split("."))


def main():
    try:
        local = _local_version()
    except Exception as e:
        print(f"[SKIP] could not read local version: {e}")
        sys.exit(0)

    try:
        remote = _fetch_remote()
        latest = remote["version"]
        min_compatible = remote.get("min_compatible", "0.0.0")
    except Exception as e:
        print(f"[SKIP] could not fetch remote version: {e}")
        sys.exit(0)

    if _parse(local) < _parse(min_compatible):
        print(f"[UPDATE_REQUIRED] current={local} min_compatible={min_compatible} latest={latest}")
        sys.exit(0)

    if _parse(local) < _parse(latest):
        print(f"[UPDATE_AVAILABLE] current={local} latest={latest}")
        sys.exit(0)

    print(f"[OK] current={local} latest={latest}")


if __name__ == "__main__":
    main()
