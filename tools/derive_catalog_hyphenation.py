"""Derive the conservative catalog lookup from the pinned German Wortliste."""
import argparse
import hashlib
from pathlib import Path
import re
import zlib

SOURCE_SHA256 = "55b457fac8e322146853f45bbda59046a55496a3e3deb32d3a88feb908eca243"


def word_breaks(word, fields):
    # Prefer the reform spelling and its explicitly listed orthographic variants.
    marked = next((fields[i] for i in (6, 4, 3, 1)
                   if i < len(fields) and fields[i] != f"-{i + 1}-"), "")
    parts = re.split(r"([-<>=·.]+)", marked)
    if "".join(parts[::2]) != word:
        # Alternate spellings, ambiguous parses, and spelling-changing breaks.
        return {}
    positions = {}
    offset = 0
    for part, marker in zip(parts[::2], parts[1::2]):
        offset += len(part)
        if "." not in marker and 1 < offset < len(word) - 1:
            positions[offset] = (len(marker), "=" in marker, "<" in marker or ">" in marker)
    return positions


def derive(source):
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError("Wortliste source hash differs from the pinned version")
    entries = {}
    for row in source.decode("utf-8").splitlines():
        fields = row.partition("#")[0].rstrip().split(";")
        word = fields[0]
        if not word.isalpha():
            continue
        points = word_breaks(word, fields)
        if word in entries:
            previous = entries[word]
            points = {i: min(rank, previous[i]) for i, rank in points.items() if i in previous}
        entries[word] = points
    rows = []
    for word, points in sorted(entries.items()):
        if points:
            offsets = sorted(points, key=lambda i: (points[i], i), reverse=True)
            rows.append(word + "\t" + ",".join(map(str, offsets)) + "\n")
    return zlib.compress("".join(rows).encode(), level=9)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_bytes(derive(args.source.read_bytes()))
