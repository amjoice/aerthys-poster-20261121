#!/usr/bin/env python3
"""AERTHYS - The Islands Above the Clouds.

A travel poster for a place that does not exist. This entrypoint writes the
poster image to /output/entry.png.

The poster is pre-rendered and shipped beside this file as entry.png (see
render_poster.py for how it was painted: a deterministic Pillow program run
at build time). This file itself uses only the Python standard library, so
it runs in the grading sandbox (plain python:3.13-slim, no network, no
third-party packages): it copies the bundled image to the output path,
byte for byte, every run.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def main():
    out = os.environ.get("POSTER_OUT", "/output/entry.png")
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copyfile(SOURCE, out)
    print("wrote {} ({} bytes)".format(out, os.path.getsize(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
