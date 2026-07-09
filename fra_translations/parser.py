"""Parser for Tatoeba-style tab-separated English<TAB>French<TAB>meta lines.

We build a mapping French -> set(English)
"""
from typing import Dict, List, Iterable, TextIO


def parse_stream(stream: TextIO) -> Dict[str, List[str]]:
    """Parse lines from a text stream and return french -> [english] mapping.

    Expected file format: English<TAB>French<TAB>...
    Multiple lines can have same English and French; we deduplicate.
    """
    mapping = {}
    for raw in stream:
        line = raw.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            # skip malformed
            continue
        eng = parts[0].strip()
        fra = parts[1].strip()
        if not eng or not fra:
            continue
        # Use fra as key, collect eng
        mapping.setdefault(fra, []).append(eng)
    # Deduplicate while preserving order
    for k, v in mapping.items():
        seen = set()
        dedup = []
        for item in v:
            if item not in seen:
                dedup.append(item)
                seen.add(item)
        mapping[k] = dedup
    return mapping


def parse_file(path: str) -> Dict[str, List[str]]:
    with open(path, 'r', encoding='utf-8') as fh:
        return parse_stream(fh)
