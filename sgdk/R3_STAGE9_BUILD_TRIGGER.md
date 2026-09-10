# R3 Stage 9 final reproducible build trigger

This file is a CI trigger/status marker only. It is not referenced by SGDK resources or source compilation and does not alter the ROM payload.

Stage 8 verified gameplay source/payload commit: `65893b6f9a760748147c8f59eba335593c69fc1a`.
Stage 8 checkpoint commit: `83919c2776ccb80811c3dcf01a270b3769431649`.

Stage 9 requirement: run the existing pinned SGDK 2.11 Build A / Build B workflow, byte-compare both ROMs, audit the ROM, then compare the result against the Stage 8 emulator-tested ROM SHA-256 `94285501cd6cb72e909c31676a52c14da01f8e72b960e34636689768e13ed293`.
