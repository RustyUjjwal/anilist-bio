#!/usr/bin/env python3
"""Poster maker: shrinks a big poster into a small web-sized file for your bio.

Needs Pillow once:   pip install pillow

  python tools/poster_maker.py my-poster.png posters-web/mytheme.jpg

Options:
  --width 700      width in pixels (the bio shows it at about 260, 700 keeps it sharp on phones)
  --quality 86     JPG quality, 1 to 95 (lower = smaller file)

A poster that was 8 MB usually becomes about 200 KB. Use a .jpg output name.
Transparent areas are filled with dark grey.
"""
import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Please run:  pip install pillow")


def make_poster(src, dst, width=700, quality=86):
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):                  # flatten transparency
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (24, 24, 24, 255))
        bg.alpha_composite(im)
        im = bg
    im = im.convert("RGB")
    if im.width > width:                                 # never enlarge
        im = im.resize((width, int(width * im.height / im.width)), Image.LANCZOS)
    im.save(dst, quality=quality, optimize=True, progressive=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("output", help="use a .jpg name")
    ap.add_argument("--width", type=int, default=700)
    ap.add_argument("--quality", type=int, default=86)
    a = ap.parse_args()
    make_poster(a.source, a.output, a.width, a.quality)
    print("Wrote", a.output, f"({os.path.getsize(a.output) // 1024} KB)")
