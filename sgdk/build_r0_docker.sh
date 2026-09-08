#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
IMAGE="registry.gitlab.com/doragasu/docker-sgdk:v2.11"

# Pull once so the build provenance can be recorded explicitly.
docker pull "$IMAGE" >/dev/null
IMAGE_ID="$(docker image inspect "$IMAGE" --format '{{.Id}}')"
IMAGE_DIGEST="$(docker image inspect "$IMAGE" --format '{{index .RepoDigests 0}}')"

mkdir -p out
printf '%s\n' "$IMAGE_ID" > out/R0_TOOLCHAIN_IMAGE_ID.txt
printf '%s\n' "$IMAGE_DIGEST" > out/R0_TOOLCHAIN_IMAGE_DIGEST.txt

docker run --rm \
  -v "$PWD:/m68k" \
  "$IMAGE_ID"

test -f out/rom.bin
python3 tools/verify_rom.py out/rom.bin
sha256sum out/rom.bin | tee out/R0_SHA256.txt
