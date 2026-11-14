#!/bin/bash
# Warm-Up video - auto play full screen, on repeat (Mac). Double-click. To close: Cmd + Q.
VIDEO="BackToSchool_WarmUp_15min.mp4"
# VIDEO="Hana_Japan_WarmUp_15min.mp4"
HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ -x "$CHROME" ]; then
  "$CHROME" --kiosk --autoplay-policy=no-user-gesture-required --no-first-run \
    --user-data-dir="/tmp/warmup_player" "file://$HERE/player.html?v=../output/$VIDEO" >/dev/null 2>&1 &
else
  open "$HERE/../output/$VIDEO"
fi
