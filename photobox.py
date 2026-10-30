#!/usr/bin/env python3
"""Build the Sonata photobox: fetch the stacked images, crop or downsample each to 160x128 RGB565, write the frames,
previews and index.html.

    python3 photobox.py            (needs Pillow; downloads to .cache/ once)

Frames land in frames/NAME.raw.gz (40960 bytes unpacked, as `fbget` wants) and previews in previews/NAME.png.
Images are the author's own, taken with a Celestron Origin: https://jrrk2.github.io/OriginMonitor/
"""
import gzip, html, os, struct, urllib.request
from PIL import Image

W, H = 160, 128
SITE = "https://jrrk2.github.io/OriginMonitor/gallery/%s.jpg"   # the restacked finals: every good frame of a target from every night
GAMMA = 0.8          # the panel is dim and these frames are dark: lift the mid tones a little

# (gallery image, name, caption, mode)   mode = ("crop", cx, cy, h) centres a window h*image height high on (cx, cy)
#                                       (fractions of the image); "fit" scales the whole field down, black bars.
PHOTOS = [
    ("m31",     "m31",          "M31 Andromeda Galaxy",           ("crop", 0.51, 0.45, 0.95)),
    ("m31",     "m31-core",     "M31 core and M32 (close crop)",  ("crop", 0.51, 0.47, 0.55)),
    ("m33",     "m33",          "M33 Triangulum Galaxy",          ("crop", 0.57, 0.60, 0.65)),
    ("m45",     "m45",          "M45 Pleiades",                   ("fit",)),
    ("m1",      "m1",           "M1 Crab Nebula",                 ("crop", 0.52, 0.49, 0.40)),
    ("m13",     "m13",          "M13 Hercules Cluster",           ("crop", 0.50, 0.51, 0.45)),
    ("m27",     "m27",          "M27 Dumbbell Nebula",            ("crop", 0.47, 0.49, 0.40)),
    ("m57",     "m57",          "M57 Ring Nebula",                ("crop", 0.47, 0.69, 0.16)),
    ("ngc6888", "ngc6888",      "NGC 6888 Crescent Nebula",       ("crop", 0.48, 0.42, 0.85)),
    ("ngc2174", "ngc2174",      "NGC 2174 Monkey Head Nebula",    ("crop", 0.53, 0.51, 0.85)),
    ("ic405",   "ic405",        "IC 405 Flaming Star Nebula",     ("crop", 0.52, 0.42, 0.85)),
    ("ngc6992", "ngc6992",      "NGC 6992 Eastern Veil Nebula",   ("fit",)),
    ("ngc2237", "rosette",      "Rosette Nebula",                 ("fit",)),
    ("ngc7000", "ngc7000",      "NGC 7000 North America Nebula",  ("fit",)),
    ("ngc869",  "double-cluster", "NGC 869 / 884 Double Cluster", ("fit",)),
    ("ngc6946", "ngc6946",      "NGC 6946 Fireworks Galaxy",      ("crop", 0.48, 0.53, 0.45)),
    ("ngc7380", "ngc7380",      "NGC 7380 Wizard Nebula",         ("crop", 0.46, 0.42, 0.85)),
    ("ic5070",  "ic5070",       "IC 5070 Pelican Nebula",         ("fit",)),
]

def frame(im, mode):
    if mode[0] == "crop":
        _, cx, cy, h = mode
        ch = im.height * h
        cw = ch * W / H
        x0 = min(max(im.width * cx - cw / 2, 0), im.width - cw)
        y0 = min(max(im.height * cy - ch / 2, 0), im.height - ch)
        out = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    else:
        k = min(W / im.width, H / im.height)
        s = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        out = Image.new("RGB", (W, H))
        out.paste(s, ((W - s.width) // 2, (H - s.height) // 2))
    lut = [round(255 * (i / 255) ** GAMMA) for i in range(256)]
    return out.point(lut * 3)

def raw565(im):
    p = im.tobytes()
    return b"".join(struct.pack("<H", (p[i] >> 3) << 11 | (p[i + 1] >> 2) << 5 | p[i + 2] >> 3) for i in range(0, len(p), 3))

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    for d in ("frames", "previews", ".cache"):
        os.makedirs(os.path.join(here, d), exist_ok=True)
    rows = []
    for n, name, caption, mode in PHOTOS:
        src = os.path.join(here, ".cache", "%s.jpg" % n)
        if not os.path.exists(src):
            urllib.request.urlretrieve(SITE % n, src)
        out = frame(Image.open(src).convert("RGB"), mode)
        raw = raw565(out)
        assert len(raw) == W * H * 2
        with open(os.path.join(here, "frames", name + ".raw.gz"), "wb") as f:
            f.write(gzip.compress(raw, 9, mtime=0))
        out.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(here, "previews", name + ".png"))
        rows.append((name, caption))
        print("%-15s %s" % (name, caption))
    with open(os.path.join(here, "frames.txt"), "w") as f:
        f.write("".join(n + "\n" for n, _ in rows))
    cards = "\n".join(
        '<figure><img src="previews/%s.png" alt="%s" width="320" height="256"><figcaption>%s<br>'
        '<a href="frames/%s.raw.gz">%s.raw.gz</a></figcaption></figure>' % (n, html.escape(c), html.escape(c), n, n)
        for n, c in rows)
    with open(os.path.join(here, "index.html"), "w") as f:
        f.write("""<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sonata photobox</title>
<style>body{background:#111;color:#ddd;font:16px system-ui;margin:0 16px 32px}h1{font-weight:500}
main{display:flex;flex-wrap:wrap;gap:16px}figure{margin:0;width:320px}img{max-width:100%%;height:auto;display:block;background:#000}
figcaption{padding-top:4px;font-size:14px}a{color:#8cf}code{background:#222;padding:1px 4px}</style>
<h1>Sonata photobox</h1>
<p>Deep-sky photographs taken with a Celestron Origin, ready for the 160&times;128 LCD on the lowRISC Sonata board.
On the board: <code>fbget https://jrrk2.github.io/photobox/frames/m31.raw.gz 10</code> (raw RGB565, gzip). Slideshow: <code>sh photobox.sh https://jrrk2.github.io/photobox 8</code>.
Full-size originals: <a href="https://jrrk2.github.io/OriginMonitor/">the OriginMonitor gallery</a>.</p>
<main>
%s
</main>
""" % cards)

main()
