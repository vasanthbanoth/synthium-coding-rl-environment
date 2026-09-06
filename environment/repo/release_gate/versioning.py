from __future__ import annotations

import re

_SEMVER = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$"
)


def parse_semver(version: str) -> tuple[int, int, int]:
    if not isinstance(version, str):
        raise ValueError("version must be a string")
    m = _SEMVER.match(version.strip())
    if not m:
        raise ValueError(f"not a semver x.y.z: {version!r}")
    return int(m.group("major")), int(m.group("minor")), int(m.group("patch"))


def is_newer(candidate: str, baseline: str) -> bool:
    """True when candidate is strictly newer than baseline (semver)."""
    # quick string compare — worked for our early 0.x tags
    return candidate > baseline
