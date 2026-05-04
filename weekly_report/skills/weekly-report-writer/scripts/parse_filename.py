"""Heuristic filename parser for PhD code repos.

Extracts (family_key, version_token, status_suffix) from file stems
to enable version-chain identification across weekly snapshots.
See spec §7 for the full algorithm.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional

# Words that indicate bugfix/iteration status rather than semantic variant.
# These go into `status`, not into `family_key`.
STATUS_SUFFIXES = frozenset({
    "final", "fixed", "correct", "new", "legacy", "old", "bak",
})

# Matches the FIRST _vN[letter] token in a stem (left to right).
# Case-insensitive: handles `_V17` on Windows-native filenames as well as `_v17`.
# Groups: (digits, optional_letter)  — remainder after the match is sliced manually.
VERSION_TOKEN_RE = re.compile(r"_v(\d+)([a-z]?)", re.IGNORECASE)

# Detects "Final_inference_final" style double-status markers (case-insensitive).
# Matches when the same status word appears more than once in the stem (start, middle, or end).
# Pattern 1: status at start, same status at end (Final_inference_final)
# Pattern 2: status in middle repeated (_final_..._final_)
_STATUS_WORDS = r"(?:final|fixed|correct)"
DOUBLE_STATUS_RE = re.compile(
    rf"(?i)(?:^{_STATUS_WORDS}_.+_{_STATUS_WORDS}$"   # status at both ends
    rf"|_{_STATUS_WORDS}_.+_{_STATUS_WORDS}(?:_|$)"    # status in middle twice
    rf"|^{_STATUS_WORDS}_.+_{_STATUS_WORDS}(?:_|$))"   # status at start twice
)

# Detects concatenated version typo like "_v20v2" (no underscore between versions).
SUSPECTED_TYPO_RE = re.compile(r"_v\d+v\d+$")

# Detects a suffix that is itself a bare version token (e.g. "v2", "v19").
# Used to drop "sub-version" semantics from family_key. Case-insensitive.
VERSION_LIKE_RE = re.compile(r"^v\d+[a-z]?$", re.IGNORECASE)


@dataclass
class ParsedName:
    raw_stem: str
    family_key: str
    version: Optional[str] = None
    status: Optional[str] = None
    is_anomaly: bool = False
    anomaly_reasons: list[str] = field(default_factory=list)


def parse_filename(stem: str) -> ParsedName:
    """Parse a file stem (no extension) into family/version/status.

    Algorithm:
    1. Check for anomaly patterns (typo, double-status).
    2. Find the first _vN version token using VERSION_TOKEN_RE (greedy from left).
    3. Extract base (everything before _vN), version string, and optional suffix.
    4. If suffix is a STATUS word → goes into `status`.
       If suffix looks like another version token (v2, v19) → drop it (sub-version, not family).
       Otherwise → append to base to form family_key.
    5. If no version token, check for standalone STATUS suffix at end of base.
    """
    anomalies: list[str] = []

    # --- Anomaly detection ---
    if SUSPECTED_TYPO_RE.search(stem):
        anomalies.append("suspected_version_typo")

    if DOUBLE_STATUS_RE.search(stem):
        anomalies.append("double_status_marker")

    # --- Version token extraction ---
    # Use search to find the FIRST _vN from the left (regex is unanchored).
    # For "compare_v17_v19" we pick v17, and v19 is later classified as a
    # sub-version and dropped via VERSION_LIKE_RE.
    version: Optional[str] = None
    semantic_suffix: Optional[str] = None
    status: Optional[str] = None

    # Find the first _vN[letter] token (left to right).
    first_v_match = VERSION_TOKEN_RE.search(stem)

    if first_v_match:
        version_digits = first_v_match.group(1)
        version_letter = first_v_match.group(2) or ""
        version = f"v{version_digits}{version_letter}"

        base = stem[: first_v_match.start()]          # everything before _vN
        remainder = stem[first_v_match.end():]        # everything after _vN[letter]

        # remainder starts with optional _suffix
        if remainder.startswith("_"):
            suffix = remainder[1:]  # strip leading underscore
        else:
            suffix = remainder  # e.g. empty string

        if not suffix:
            semantic_suffix = None
        elif suffix.lower() in STATUS_SUFFIXES:
            # e.g. "fixed", "final"  → status field
            status = suffix.lower()
            semantic_suffix = None
        elif VERSION_LIKE_RE.match(suffix):
            # e.g. "v2", "v19" → sub-version indicator, drop from family_key
            semantic_suffix = None
        else:
            # Genuine semantic variant: "contrastive", "mstcn_contrastive", etc.
            semantic_suffix = suffix

    else:
        # No version token at all.
        base = stem
        # Check for standalone status suffix (e.g. "data_loader_new")
        for s in sorted(STATUS_SUFFIXES, key=len, reverse=True):  # longest first
            if base.lower().endswith(f"_{s}"):
                status = s
                base = base[: -(len(s) + 1)]
                break

    # Build family_key
    family_key = f"{base}_{semantic_suffix}" if semantic_suffix else base

    return ParsedName(
        raw_stem=stem,
        family_key=family_key,
        version=version,
        status=status,
        is_anomaly=bool(anomalies),
        anomaly_reasons=anomalies,
    )
