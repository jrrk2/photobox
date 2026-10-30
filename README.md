# photobox

Deep-sky photographs for the 160x128 LCD of the lowRISC Sonata board, as ready-made frames for the `sonata_romlinux`
LiteX/Linux example (the VexRiscv SoC with BusyBox, in the synthgui repository under `projects/sonata_romlinux-src`).
Published at https://jrrk2.github.io/photobox/ (GitHub Pages, branch `main`, root).

The photographs were taken by the author with a Celestron Origin. They come from the OriginMonitor gallery, https://jrrk2.github.io/OriginMonitor/,
where each target is one stack of all its good frames from every night.
Each frame is raw RGB565, little endian, gzip-compressed (`frames/NAME.raw.gz`: 40960 bytes unpacked, about 25 KB packed).

* Small targets (M1, M13, M27, M57, M31 core, NGC 6946, ...) are cropped around the object; large nebulae and star fields (Pleiades,
  Veil, Rosette, North America, Double Cluster) are scaled down whole with black bars. The choice and the crop centres are the
  `PHOTOS` table in `photobox.py`. A gamma of 0.8 lifts the mid tones: the panel is dim and astro frames are dark.
* `frames.txt` lists the frame names, one per line, in slideshow order. `previews/` has 2x PNGs for the web page.

## On the board

The board's BusyBox `wget` speaks https (TLS 1.2, no certificate check), so these work as they are:

    fbget https://jrrk2.github.io/photobox/frames/m31.raw.gz 10                  # one picture for 10 s
    wget -O /tmp/pb.sh https://jrrk2.github.io/photobox/photobox.sh
    sh /tmp/pb.sh https://jrrk2.github.io/photobox 8                             # slideshow, Ctrl-C stops

`photobox.sh` keeps `/dev/fb0` open for the whole run so the text console never reappears between pictures, and downloads the
next frame while the current one is shown. `fbget` is in the sonata_romlinux root filesystem. Over plain http from a PC (`python3 -m http.server`)
the same commands work with `http://HOST:8000/`.

## Rebuild

    pip install pillow
    python3 photobox.py

downloads the originals into `.cache/` (not committed), and writes `frames/`, `previews/`, `frames.txt` and `index.html`.

## Licence

The code (`photobox.py`, `photobox.sh`) is the author's; the photographs are the author's own work. No licence has been chosen yet.
