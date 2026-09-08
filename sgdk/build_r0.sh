#!/usr/bin/env sh
set -eu

if [ -z "${GDK:-}" ]; then
  echo "ERROR: GDK is not set to the SGDK root." >&2
  exit 2
fi

if [ ! -f "$GDK/makefile.gen" ]; then
  echo "ERROR: $GDK/makefile.gen not found." >&2
  exit 2
fi

cd "$(dirname "$0")"
make -f "$GDK/makefile.gen" clean
make -f "$GDK/makefile.gen"

test -f out/rom.bin
sha256sum out/rom.bin
