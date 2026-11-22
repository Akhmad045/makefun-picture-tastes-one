#!/usr/bin/env python3
"""The picture that tastes of one ingredient -- make.fun entry.

Writes one image to /output/entry.png: a single ripe strawberry, drawn at
build time (see draw_entry.py) and committed as entry.png next to this file.
This program only copies that committed PNG into /output -- stdlib only,
no network, no third-party imports -- because the grading sandbox is offline.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST = "/output/entry.png"


def main():
    if not os.path.isfile(SRC):
        print("entry.png missing next to main.py", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    shutil.copyfile(SRC, DST)
    size = os.path.getsize(DST)
    print("wrote %s (%d bytes)" % (DST, size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
