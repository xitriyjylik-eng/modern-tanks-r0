#!/usr/bin/env bash
set -euo pipefail

OUT_ROOT="${1:-$PWD/sgdk/out/stage10_soak}"
ROM="${2:-$PWD/sgdk/out/rom.bin}"
mkdir -p "$OUT_ROOT"
export DISPLAY=:99
export SDL_AUDIODRIVER=dummy
export LIBGL_ALWAYS_SOFTWARE=1
export SDL_VIDEODRIVER=x11

XVFB_PID=''
EMU_PID=''
cleanup_all() {
  if [ -n "${EMU_PID:-}" ] && [ "$EMU_PID" -gt 1 ] 2>/dev/null; then kill "$EMU_PID" 2>/dev/null || true; fi
  if [ -n "${XVFB_PID:-}" ] && [ "$XVFB_PID" -gt 1 ] 2>/dev/null; then kill "$XVFB_PID" 2>/dev/null || true; fi
}
trap cleanup_all EXIT

Xvfb :99 -screen 0 800x600x24 -nolisten tcp >"$OUT_ROOT/xvfb.log" 2>&1 &
XVFB_PID=$!
for _ in $(seq 1 100); do
  kill -0 "$XVFB_PID" 2>/dev/null || { cat "$OUT_ROOT/xvfb.log" >&2 || true; exit 1; }
  xdotool getmouselocation >/dev/null 2>&1 && break
  sleep 0.1
done
xdotool getmouselocation >/dev/null 2>&1 || { echo 'Xvfb not ready' >&2; exit 1; }

run_case() {
  local name="$1" region="$2" min_seconds="$3" min_cycles="$4"
  local out="$OUT_ROOT/$name" raw="$RUNNER_TEMP/r3-soak-$name-raw" home="$RUNNER_TEMP/r3-soak-$name-home"
  rm -rf "$raw" "$home"
  mkdir -p "$out" "$raw" "$home/.config/blastem"

  local cfg_src
  cfg_src="$(dpkg -L blastem | grep -E '/default\.cfg$' | head -n1 || true)"
  if [ -n "$cfg_src" ]; then cp "$cfg_src" "$home/.config/blastem/blastem.cfg"; else printf 'ui {\n screenshot_path %s\n screenshot_template soak_%%Y%%m%%d_%%H%%M%%S.png\n}\n' "$raw" > "$home/.config/blastem/blastem.cfg"; fi
  python3 - "$home/.config/blastem/blastem.cfg" "$raw" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]); raw=sys.argv[2]
s=p.read_text(errors='replace')
if re.search(r'(?m)^\s*screenshot_path\s+',s): s=re.sub(r'(?m)^\s*screenshot_path\s+.*$',f'\tscreenshot_path {raw}',s)
else: s=s.replace('ui {',f'ui {{\n\tscreenshot_path {raw}',1)
if re.search(r'(?m)^\s*screenshot_template\s+',s): s=re.sub(r'(?m)^\s*screenshot_template\s+.*$',r'\tscreenshot_template soak_%Y%m%d_%H%M%S.png',s)
else: s=s.replace('ui {','ui {\n\tscreenshot_template soak_%Y%m%d_%H%M%S.png',1)
p.write_text(s)
PY

  export HOME="$home"
  blastem -g -r "$region" "$ROM" 320 224 >"$out/blastem.log" 2>&1 &
  EMU_PID=$!

  local win=''
  for _ in $(seq 1 120); do
    if ! kill -0 "$EMU_PID" 2>/dev/null; then cat "$out/blastem.log" >&2 || true; return 1; fi
    win="$(xdotool search --onlyvisible --pid "$EMU_PID" 2>/dev/null | head -n1 || true)"
    [ -n "$win" ] || win="$(xdotool search --onlyvisible --name 'BlastEm' 2>/dev/null | head -n1 || true)"
    [ -n "$win" ] && break
    sleep 0.1
  done
  [ -n "$win" ] || { echo "$name: no BlastEm window" >&2; return 1; }
  xdotool windowfocus "$win" || true

  pad_tap() { local key="$1"; xdotool keydown --window "$win" "$key"; sleep 0.20; xdotool keyup --window "$win" "$key"; }
  shot_key() { xdotool keydown --window "$win" p; sleep 0.03; xdotool keyup --window "$win" p; }
  capture() {
    local label="$1" before newest_line newest trailer
    before="$(find "$raw" -maxdepth 1 -type f -name '*.png' -printf '%T@ %p\n' | sort -nr | head -n1 || true)"
    shot_key
    for _ in $(seq 1 80); do
      newest_line="$(find "$raw" -maxdepth 1 -type f -name '*.png' -printf '%T@ %p\n' | sort -nr | head -n1 || true)"
      if [ -n "$newest_line" ] && [ "$newest_line" != "$before" ]; then
        newest="${newest_line#* }"
        if [ -s "$newest" ]; then
          trailer="$(tail -c 12 "$newest" 2>/dev/null | od -An -tx1 | tr -d ' \n' || true)"
          if [ "$trailer" = '0000000049454e44ae426082' ]; then cp "$newest" "$out/${label}.png"; return 0; fi
        fi
      fi
      sleep 0.05
    done
    echo "$name: screenshot timeout $label" >&2
    return 1
  }
  alive() { kill -0 "$EMU_PID" 2>/dev/null || { echo "$name: BlastEm died" >&2; cat "$out/blastem.log" >&2 || true; return 1; }; }
  rss_kb() { awk '/VmRSS:/ {print $2}' "/proc/$EMU_PID/status" 2>/dev/null || echo 0; }

  : > "$out/cycles.csv"
  echo 'cycle,elapsed_s,rss_kb' >> "$out/cycles.csv"
  sleep 2.5
  capture 000_boot
  # Robust boot -> menu. Three START taps are harmless once battle starts, so first get a known battle,
  # then return to menu to establish the cycle baseline.
  for _ in 1 2 3; do pad_tap Return; sleep 0.60; done
  capture 001_initial_battle
  pad_tap s; sleep 0.80
  capture 002_initial_menu

  local start=$SECONDS cycle=0 elapsed=0 direction key1 key2
  while :; do
    elapsed=$((SECONDS-start))
    if [ "$cycle" -ge "$min_cycles" ] && [ "$elapsed" -ge "$min_seconds" ]; then break; fi
    cycle=$((cycle+1))
    local tag
    printf -v tag '%03d' "$cycle"

    alive
    # MENU -> BATTLE. Two START taps tolerate a missed polling frame; extra START in battle is inert.
    pad_tap Return; sleep 0.35; pad_tap Return; sleep 0.80
    alive
    capture "${tag}_battle"

    # Exercise different scroll directions from the fixed battle start point.
    key1=''; key2=''
    case $((cycle % 6)) in
      0) key1=Right ;;
      1) key1=Down ;;
      2) key1=Left ;;
      3) key1=Up ;;
      4) key1=Right; key2=Down ;;
      5) key1=Left; key2=Up ;;
    esac
    xdotool keydown --window "$win" "$key1"
    [ -z "$key2" ] || xdotool keydown --window "$win" "$key2"
    sleep 9.0
    alive
    capture "${tag}_moved"
    xdotool keyup --window "$win" "$key1"
    [ -z "$key2" ] || xdotool keyup --window "$win" "$key2"
    sleep 0.60

    # BATTLE -> MENU, again double-tap B for input robustness; B in menu is harmless.
    pad_tap s; sleep 0.35; pad_tap s; sleep 0.80
    alive
    capture "${tag}_menu"
    elapsed=$((SECONDS-start))
    echo "$cycle,$elapsed,$(rss_kb)" >> "$out/cycles.csv"
  done

  local total=$((SECONDS-start))
  printf 'region=%s\ncycles=%d\nelapsed_seconds=%d\nfinal_rss_kb=%s\n' "$region" "$cycle" "$total" "$(rss_kb)" > "$out/summary.txt"
  alive
  kill "$EMU_PID" 2>/dev/null || true
  wait "$EMU_PID" 2>/dev/null || true
  EMU_PID=''
}

# Main soak: >10 minutes continuous NTSC runtime with repeated map allocation/release cycles.
run_case ntsc U 630 40
# Short PAL repeated-transition regression on the exact same ROM.
run_case pal E 120 8
