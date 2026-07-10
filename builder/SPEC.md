# Profile SVG v2 — Terminal Window Redesign

Two builders work in parallel against this contract. Scratchpad (work dir):
`C:\Users\Oleg\AppData\Local\Temp\claude\C--Users-Oleg-Desktop-code-github\1452e980-7131-4d62-a66e-c06b701076e1\scratchpad`

Existing assets in scratchpad: `avatar.png` (452x452 anime portrait), `ascii_gen.py`
(v1 grayscale converter, reference only), `build_svg.py` (v1 builder — REUSE its
info-row logic and current stat values verbatim).
Production repo: `C:\Users\Oleg\Desktop\code\github\lightsmite` (today.py lives here).

## Design
One SVG per theme (`light_mode.svg`, `dark_mode.svg`), 985px wide, rendered as a
macOS-style terminal window:

- Canvas: rounded rect rx=12, full-canvas. Title bar 36px tall (slightly different
  shade than body), three traffic-light circles r=6 (fills #ff5f56 #ffbd2e #27c93f,
  cx = 22/44/66, cy = 18), centered muted title text `lightsmite@github: ~` (13px).
- Prompt line at baseline y=64, x=15, default text color:
  `<green>lightsmite@github</green>:<blue>~</blue>$ neofetch` followed by a blinking
  block cursor: `<rect width="9" height="16">` with
  `<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.2s" repeatCount="indefinite"/>`.
- Body content (art + info panel) starts at baseline y=94, line height 20px.
- Font: same as v1 — `font-family="ConsolasFallback,Consolas,monospace"`,
  font-size 16px, the same @font-face size-adjust 109% block as v1. Char cell is
  ~9.6px wide. `text, tspan {white-space: pre;}`.
- ASCII art: x=15, 21 rows (y = 94, 114, ... 494), max 38 chars/row.
- Info panel: x=390, 22 rows y = 94..514 (some intentionally blank/skipped — copy the
  exact row list from v1 build_svg.py ROWS, shifted +64px).
- Total height: 514 + 26 padding = 540.

## Theme palettes
                      dark        light
canvas/body bg        #161b22     #f6f8fa
title bar bg          #21262d     #e7ebf0
default text (ink)    #c9d1d9     #24292f
.key                  #ffa657     #953800
.value                #a5d6ff     #0a3069
.addColor             #3fb950     #1a7f37
.delColor             #f85149     #cf222e
.cc (dot leaders)     #616e7f     #c2cfde
prompt green          #3fb950     #1a7f37
prompt blue           #58a6ff     #0969da
art .a-hair           #f2cc60     #bf8700
art .a-jacket         #f0883e     #bc4c00
art .a-skin           #e6b892    -> use #e0b48f dark / #a97d55 light
art .a-blue           #58a6ff     #0969da
art .a-gray           #8b949e     #6e7781
(art outline/dark pixels use default ink color, no class)

## Interface contract between the two builders
`art_color.py` (in scratchpad) exposes:

    PALETTE_KEYS = ('ink', 'hair', 'jacket', 'skin', 'blue', 'gray')
    def art_runs() -> list[list[tuple[str, str]]]
        # exactly <=21 rows; each row: list of (text, key) runs, key in PALETTE_KEYS;
        # consecutive same-key cells merged into one run; rows right-stripped;
        # each row <= 38 chars total. Pure function, no I/O at import time
        # beyond reading avatar.png relative to this file's directory.

The SVG builder maps keys -> CSS classes (`ink` -> no class/default fill,
others -> .a-<key>) and must join runs into one `<tspan x=15 y=...>` per row
containing nested tspans WITHOUT any whitespace between them (white-space: pre).

## Hard compatibility requirements (breaking these breaks production)
today.py `svg_overwrite()` rewrites these element IDs in both SVGs; ALL 16 must
exist with identical semantics to v1: age_data, age_data_dots, commit_data,
commit_data_dots, contrib_data, follower_data, follower_data_dots, loc_add,
loc_data, loc_data_dots, loc_del, loc_del_dots, repo_data, repo_data_dots,
star_data, star_data_dots.
Justify widths (value+dots column widths handled by today.py): age 49, commit 23,
star 14, repo 6, follower 10, loc 9, loc_del 7, contrib none. The v1 build_svg.py
implements all of this — copy its `info_row`/`dots`/`stats_row_*`/`header_row`
functions and ROWS content unchanged (only shift y by +64). Current stat values in
v1 are correct; keep them.

## Verification each builder must run before finishing
- Windows console is cp1251: always `PYTHONIOENCODING=utf-8` when running python
  from bash; write files with encoding='utf-8'.
- Render check: start `python -m http.server <PORT>` in the directory (art builder
  uses PORT 8811, svg builder 8812) and screenshot with:
  "/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new
  --disable-gpu --hide-scrollbars --force-device-scale-factor=1
  --window-size=1005,660 --screenshot=<ABS_WIN_PATH>.png <URL>
  Then Read the PNG and judge it yourself. Iterate until good.
- SVG builder additionally: run the today.py compatibility stub — copy the SVGs,
  chdir to the repo, `ACCESS_TOKEN=dummy USER_NAME=lightsmite python -c "import today;
  today.svg_overwrite(<copy>, '8 years, 1 month, 1 day', 2345, 12, 58, 61, 7,
  ['1,234,567','234,567','1,000,000'])"` and verify with lxml that all ids updated
  and the file still parses. Do NOT modify today.py or push anything to git.
