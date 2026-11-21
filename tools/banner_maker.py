#!/usr/bin/env python3
"""Banner maker: turns your own artwork into files that are the right size for the bio.

Needs Pillow once:   pip install pillow

  python tools/banner_maker.py banner  my-art.jpg  banners/mytheme-banner.png
  python tools/banner_maker.py poster  my-poster.png  posters-web/mytheme.jpg

banner : crops to 2:1 (1200 x 600), makes it translucent with soft faded edges. PNG output.
         --opacity 0.75   how solid it is (0.3 = very faint, 1 = fully solid)
         --fit            keep the whole picture (pads with the picture's own edge colour)
                          instead of cropping, good for logos
poster : shrinks to 700 px wide and saves a small JPG (a few hundred KB).
"""
import argparse
import sys

try:
    from PIL import Image
    import numpy as np
except ImportError:
    sys.exit("Please run:  pip install pillow numpy")


def banner(src, dst, opacity, fit):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if fit:   # whole picture on a background taken from its own edge
        edge = np.array(im.resize((50, 50)))[:5].reshape(-1, 3).mean(0).astype(int)
        nw = int(w * 600 / h)
        small = im.resize((nw, 600), Image.LANCZOS)
        im = Image.new("RGB", (1200, 600), tuple(edge))
        im.paste(small, ((1200 - nw) // 2, 0))
    else:     # crop to 2:1 around the centre
        if w >= 2 * h:
            left = (w - 2 * h) // 2
            im = im.crop((left, 0, left + 2 * h, h))
        else:
            top = (h - w // 2) // 2
            im = im.crop((0, top, w, top + w // 2))
        im = im.resize((1200, 600), Image.LANCZOS)
    alpha = np.full((600, 1200), opacity, dtype=np.float32)
    fade = 60   # pixels of soft edge
    x = np.minimum(np.arange(1200), np.arange(1200)[::-1])
    y = np.minimum(np.arange(600), np.arange(600)[::-1])
    alpha *= np.minimum(np.clip(x / fade, 0, 1)[None, :], np.clip(y / fade, 0, 1)[:, None])
    out = im.convert("RGBA")
    out.putalpha(Image.fromarray((alpha * 255).astype("uint8")))
    out.save(dst, optimize=True)


def poster(src, dst):
    im = Image.open(src).convert("RGB")
    im = im.resize((700, int(700 * im.height / im.width)), Image.LANCZOS)
    im.save(dst, quality=86, optimize=True, progressive=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["banner", "poster"])
    ap.add_argument("source")
    ap.add_argument("output")
    ap.add_argument("--opacity", type=float, default=0.75)
    ap.add_argument("--fit", action="store_true")
    a = ap.parse_args()
    banner(a.source, a.output, a.opacity, a.fit) if a.kind == "banner" else poster(a.source, a.output)
    print("Wrote", a.output)
