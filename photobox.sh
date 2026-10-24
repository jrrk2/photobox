#!/bin/sh
# photobox.sh BASE_URL [seconds] -- slideshow on the Sonata LCD.
#   photobox.sh http://192.168.1.169:8000/photobox 8
# BASE_URL holds frames/NAME.raw.gz and frames.txt (one NAME per line); http:// or https:// (BusyBox wget has TLS 1.2, no certificate check). Ctrl-C stops.
# /dev/fb0 is held open for the whole run, so the panel stays in frame buffer mode (no flash of the text console
# between pictures); the next frame is downloaded while the current one is shown.
base=${1:?usage: photobox.sh BASE_URL [seconds]}
secs=${2:-8}
t=/tmp/photobox
get() {   # get NAME -> $t.NAME.raw, or nothing on failure
    wget -q -O "$t.dl" "$base/frames/$1.raw.gz" && zcat "$t.dl" > "$t.$1.raw"
    [ "$(wc -c < "$t.$1.raw" 2>/dev/null)" -eq 40960 ] 2>/dev/null || { rm -f "$t.$1.raw"; echo "photobox: bad frame $1" >&2; }
}
wget -q -O $t.list "$base/frames.txt" || { echo "photobox: no $base/frames.txt" >&2; exit 1; }
exec 3>/dev/fb0
trap 'rm -f $t.*; exec 3>&-; exit' INT TERM EXIT
set -- $(cat $t.list)
get "$1"
while :; do
    n=$1; shift; set -- "$@" "$n"   # rotate: $1 is now the frame after $n
    [ -f "$t.$n.raw" ] && cat "$t.$n.raw" > /dev/fb0
    rm -f "$t.$n.raw"
    get "$1" &
    sleep "$secs"
    wait
done
