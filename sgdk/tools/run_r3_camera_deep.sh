#!/usr/bin/env bash
set -euo pipefail

OUT_ROOT="${1:-$PWD/sgdk/out/camera_deep}"
ROM="${2:-$PWD/sgdk/out/rom.bin}"
mkdir -p "$OUT_ROOT"
export DISPLAY=:99
export SDL_AUDIODRIVER=dummy
export LIBGL_ALWAYS_SOFTWARE=1

XVFB_PID=''
EMU_PID=''
cleanup_all() {
  if [ -n "${EMU_PID:-}" ] && [ "$EMU_PID" -gt 1 ] 2>/dev/null; then kill "$EMU_PID" 2>/dev/null || true; fi
  if [ -n "${XVFB_PID:-}" ] && [ "$XVFB_PID" -gt 1 ] 2>/dev/null; then kill "$XVFB_PID" 2>/dev/null || true; fi
}
trap cleanup_all EXIT

Xvfb :99 -screen 0 800x600x24 -nolisten tcp >"$OUT_ROOT/xvfb.log" 2>&1 &
XVFB_PID=$!
sleep 1

run_case() {
  local name="$1" region="$2"
  local out="$OUT_ROOT/$name" raw="$RUNNER_TEMP/r3-camera-$name-raw" home="$RUNNER_TEMP/r3-camera-$name-home"
  rm -rf "$raw" "$home"
  mkdir -p "$out" "$raw" "$home/.config/blastem"

  local cfg_src
  cfg_src="$(dpkg -L blastem | grep -E '/default\.cfg$' | head -n1 || true)"
  if [ -n "$cfg_src" ]; then cp "$cfg_src" "$home/.config/blastem/blastem.cfg"; else printf 'ui {\n screenshot_path %s\n screenshot_template camera_%%Y%%m%%d_%%H%%M%%S.png\n}\n' "$raw" > "$home/.config/blastem/blastem.cfg"; fi
  python3 - "$home/.config/blastem/blastem.cfg" "$raw" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]); raw=sys.argv[2]
s=p.read_text(errors='replace')
if re.search(r'(?m)^\s*screenshot_path\s+',s): s=re.sub(r'(?m)^\s*screenshot_path\s+.*$',f'\tscreenshot_path {raw}',s)
else: s=s.replace('ui {',f'ui {{\n\tscreenshot_path {raw}',1)
if re.search(r'(?m)^\s*screenshot_template\s+',s): s=re.sub(r'(?m)^\s*screenshot_template\s+.*$',r'\tscreenshot_template camera_%Y%m%d_%H%M%S.png',s)
else: s=s.replace('ui {','ui {\n\tscreenshot_template camera_%Y%m%d_%H%M%S.png',1)
p.write_text(s)
PY

  export HOME="$home"
  blastem -g -r "$region" "$ROM" 320 224 >"$out/blastem.log" 2>&1 &
  EMU_PID=$!

  local win=''
  for _ in $(seq 1 80); do
    if ! kill -0 "$EMU_PID" 2>/dev/null; then cat "$out/blastem.log" >&2 || true; return 1; fi
    win="$(xdotool search --onlyvisible --name 'BlastEm' 2>/dev/null | head -n1 || true)"
    [ -n "$win" ] && break
    sleep 0.1
  done
  test -n "$win"
  xdotool windowfocus "$win" || true
  : > "$out/trace.csv"
  echo 'label,epoch_ms' >> "$out/trace.csv"

  pad_tap() { local key="$1"; xdotool keydown --window "$win" "$key"; sleep 0.20; xdotool keyup --window "$win" "$key"; }
  shot_key() { xdotool keydown --window "$win" p; sleep 0.03; xdotool keyup --window "$win" p; }
  down() { xdotool keydown --window "$win" "$1"; }
  up() { xdotool keyup --window "$win" "$1"; }
  capture() {
    local label="$1" ts newest
    ts="$(date +%s%3N)"
    shot_key
    sleep 0.09
    newest="$(find "$raw" -maxdepth 1 -type f -name '*.png' -printf '%T@ %p\n' | sort -nr | head -n1 | cut -d' ' -f2-)"
    test -n "$newest"
    cp "$newest" "$out/${label}.png"
    echo "$label,$ts" >> "$out/trace.csv"
  }

  sleep 1.5
  pad_tap Return
  sleep 1.1
  capture 00_menu
  pad_tap Return
  sleep 1.2
  capture 01_start

  down Right
  for i in 01 02 03 04 05 06 07 08; do sleep 0.11; capture "10_right_$i"; done
  up Right
  capture 11_release_00
  sleep 0.08; capture 11_release_01
  sleep 0.10; capture 11_release_02
  sleep 0.18; capture 11_release_03
  sleep 0.45; capture 11_settle_a
  sleep 0.45; capture 11_settle_b

  down Right
  sleep 6.5; capture 20_right_mid
  sleep 1.0; capture 21_right_edge_a
  sleep 1.0; capture 21_right_edge_b
  up Right
  sleep 0.5

  down Left
  sleep 1.0; capture 30_left_mid
  sleep 9.0; capture 31_left_edge_a
  sleep 1.0; capture 31_left_edge_b
  up Left
  sleep 0.5

  down Down
  sleep 1.0; capture 40_down_mid
  sleep 6.5; capture 41_bottom_edge_a
  sleep 1.0; capture 41_bottom_edge_b
  up Down
  sleep 0.5

  down Up
  sleep 1.0; capture 50_up_mid
  sleep 6.5; capture 51_top_edge_a
  sleep 1.0; capture 51_top_edge_b
  up Up
  sleep 0.5

  down Right; down Down
  for i in 01 02 03 04 05; do sleep 0.12; capture "60_diag_dr_$i"; done
  up Right; up Down
  capture 61_diag_release_00
  sleep 0.10; capture 61_diag_release_01
  sleep 0.18; capture 61_diag_release_02
  sleep 0.45; capture 61_diag_settle_a
  sleep 0.45; capture 61_diag_settle_b

  down Left; down Up
  sleep 3.0; capture 70_diag_ul_edge_a
  sleep 1.0; capture 70_diag_ul_edge_b
  up Left; up Up
  sleep 0.5
  capture 71_final_settle

  kill "$EMU_PID" 2>/dev/null || true
  wait "$EMU_PID" 2>/dev/null || true
  EMU_PID=''
}

run_case ntsc U
run_case pal E
