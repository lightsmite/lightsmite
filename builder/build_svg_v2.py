"""Build light_mode.svg and dark_mode.svg for the lightsmite profile README (v2).

macOS-style terminal window: title bar with traffic lights, a prompt line with
a blinking cursor, then the same ASCII-art + info-panel body as v1 (build_svg.py),
shifted down by 64px to make room for the new chrome.

Reuses build_svg.py's info_row/dots/value/key/header_row/stats_row_* functions,
ROWS content, and current stat values UNCHANGED (only y coordinates shifted).
See SPEC.md in this directory for the full contract.
"""
import html
import sys

try:
    from art_color import art_runs, PALETTE_KEYS
except ImportError:
    # Fallback so this script works before art_color.py exists: a small
    # centered diamond of '#', all rows tagged 'ink' (inherits default fill).
    PALETTE_KEYS = ('ink', 'hair', 'jacket', 'skin', 'blue', 'gray')

    def art_runs():
        widths = [1, 3, 5, 7, 9, 9, 7, 5, 3, 1]
        maxw = max(widths)
        rows = []
        for w in widths:
            pad = (maxw - w) // 2
            rows.append([(" " * pad + "#" * w, "ink")])
        return rows

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "."

WIDTH = 60  # chars per info row (unchanged from v1)

# --- theme palettes (chrome + reused v1 colors + art colors) ---
PALETTES = {
    "light_mode.svg": {
        "bg": "#f6f8fa", "titlebar": "#e7ebf0", "text": "#24292f",
        "key": "#953800", "value": "#0a3069", "add": "#1a7f37",
        "del": "#cf222e", "cc": "#c2cfde",
        "muted": "#6e7781", "pg": "#1a7f37", "pb": "#0969da",
        "a_hair": "#bf8700", "a_jacket": "#bc4c00", "a_skin": "#a97d55",
        "a_blue": "#0969da", "a_gray": "#6e7781",
    },
    "dark_mode.svg": {
        "bg": "#161b22", "titlebar": "#21262d", "text": "#c9d1d9",
        "key": "#ffa657", "value": "#a5d6ff", "add": "#3fb950",
        "del": "#f85149", "cc": "#616e7f",
        "muted": "#8b949e", "pg": "#3fb950", "pb": "#58a6ff",
        "a_hair": "#f2cc60", "a_jacket": "#f0883e", "a_skin": "#e0b48f",
        "a_blue": "#58a6ff", "a_gray": "#8b949e",
    },
}

E = html.escape

# ---------------------------------------------------------------------------
# Copied verbatim from build_svg.py (v1) — do not change semantics.
# ---------------------------------------------------------------------------

def key(s):
    # 'Languages.Programming' -> key.key with plain dot separators
    parts = s.split(".")
    return ".".join(f'<tspan class="key">{E(p)}</tspan>' for p in parts)

def dots(n, elem_id=None):
    idattr = f' id="{elem_id}"' if elem_id else ""
    if n <= 0:
        s = {0: "", -1: ""}.get(n, "")
    elif n == 1:
        s = " "
    elif n == 2:
        s = ". "
    else:
        s = " " + "." * (n - 2) + " "  # matches today.py justify_format
    return f'<tspan class="cc"{idattr}>{s}</tspan>'

def value(s, elem_id=None):
    idattr = f' id="{elem_id}"' if elem_id else ""
    return f'<tspan class="value"{idattr}>{E(s)}</tspan>'

def info_row(label, val, val_id=None, dots_id=None):
    # ". " + label + ":" + " ...dots... " + value == WIDTH chars
    label_len = 2 + len(label) + 1
    ndots = WIDTH - label_len - len(val)
    return ('<tspan class="cc">. </tspan>' + key(label) + ":"
            + dots(ndots, dots_id) + value(val, val_id))

def header_row(text_, lead=""):
    n = WIDTH - len(lead + text_) - 1
    return f"{E(lead + text_)} " + "—" * n

# --- stats as of last local run; the GitHub Action (today.py) overwrites these ---
AGE = "8 years, 6 months, 12 days"
REPOS, CONTRIB, STARS = "60", "60", "1"
COMMITS, FOLLOWERS = "1,438", "0"
LOC, LOC_ADD, LOC_DEL = "601,130", "752,880", "151,750"

def stats_row_repos():
    ndots = 6 - len(REPOS)
    sdots = 14 - len(STARS)
    return ('<tspan class="cc">. </tspan>' + key("Repos") + ":"
            + dots(ndots + 2, "repo_data_dots") + value(REPOS, "repo_data")
            + " {" + key("Contributed") + ": " + value(CONTRIB, "contrib_data")
            + "} | " + key("Stars") + ":"
            + dots(sdots + 2, "star_data_dots") + value(STARS, "star_data"))

def stats_row_commits():
    cdots = 23 - len(COMMITS)
    fdots = 10 - len(FOLLOWERS)
    return ('<tspan class="cc">. </tspan>' + key("Commits") + ":"
            + dots(cdots + 2, "commit_data_dots") + value(COMMITS, "commit_data")
            + " | " + key("Followers") + ":"
            + dots(fdots + 2, "follower_data_dots") + value(FOLLOWERS, "follower_data"))

def stats_row_loc():
    ldots = 9 - len(LOC)
    ddots = 7 - len(LOC_DEL)
    return ('<tspan class="cc">. </tspan>' + key("Lines of Code on GitHub") + ":"
            + dots(ldots + 2, "loc_data_dots") + value(LOC, "loc_data")
            + f' ( <tspan class="addColor" id="loc_add">{LOC_ADD}</tspan>'
            + '<tspan class="addColor">++</tspan>, '
            + f'<tspan id="loc_del_dots">{" " * max(0, ddots)}</tspan>'
            + f'<tspan class="delColor" id="loc_del">{LOC_DEL}</tspan>'
            + '<tspan class="delColor">--</tspan> )')

# (y, content) — None content = row intentionally left empty
# Same as v1 ROWS, y shifted +64 (body content now starts at baseline y=94).
ROWS = [
    (94,  header_row("lightsmite@github")),
    (114, info_row("OS", "Windows, Linux")),
    (134, info_row("Uptime", AGE, "age_data", "age_data_dots")),
    (154, info_row("Host", "Crypto Trading Infrastructure")),
    (174, info_row("Kernel", "Algorithmic Trading Systems")),
    (194, info_row("IDE", "VSCode, Claude Code")),
    (214, '<tspan class="cc">. </tspan>'),
    (234, info_row("Languages.Programming", "JavaScript, Python, Shell")),
    (254, info_row("Languages.Computer", "HTML, CSS, JSON, YAML")),
    (274, info_row("Languages.Real", "English, Ukrainian, Russian, Lithuanian")),
    (294, '<tspan class="cc">. </tspan>'),
    (314, info_row("Hobbies.Software", "Trading Bots, DeFi, Automation")),
    (334, info_row("Hobbies.Markets", "Arbitrage, Orderbooks, Yield")),
    (374, header_row("Contact", "- ")),
    (394, info_row("Email", "lightsmite83360@gmail.com")),
    (414, info_row("GitHub", "github.com/lightsmite")),
    (434, info_row("Telegram", "t.me/fff31div")),
    (474, header_row("GitHub Stats", "- ")),
    (494, stats_row_repos()),
    (514, stats_row_commits()),
    (534, stats_row_loc()),
]

# ---------------------------------------------------------------------------
# New in v2: terminal chrome + ASCII-art color runs.
# ---------------------------------------------------------------------------

TITLE_TEXT = "lightsmite@github: ~"
PROMPT_TEXT = "lightsmite@github:~$ neofetch"
CHAR_W = 9.6
CURSOR_X = 15 + len(PROMPT_TEXT) * CHAR_W

ART_Y0 = 94
ART_LINE_H = 20
ART_MAX_ROWS = 21

CLASS_MAP = {k: f"a-{k}" for k in PALETTE_KEYS if k != "ink"}

def render_art_row(y, runs):
    parts = []
    for text, k in runs:
        if not text:
            continue
        if k == "ink":
            parts.append(E(text))
        else:
            cls = CLASS_MAP.get(k, "")
            parts.append(f'<tspan class="{cls}">{E(text)}</tspan>')
    inner = "".join(parts)
    return f'<tspan x="15" y="{y}">{inner}</tspan>'

def art_block():
    rows = art_runs()[:ART_MAX_ROWS]
    return "\n".join(
        render_art_row(ART_Y0 + i * ART_LINE_H, runs)
        for i, runs in enumerate(rows)
    )

HEIGHT = 534 + 26  # last info row y=534 + bottom padding = 560

TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="{h}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {key};}}
.value {{fill: {value};}}
.addColor {{fill: {add};}}
.delColor {{fill: {del_};}}
.cc {{fill: {cc};}}
.muted {{fill: {muted};}}
.pg {{fill: {pg};}}
.pb {{fill: {pb};}}
.a-hair {{fill: {a_hair};}}
.a-jacket {{fill: {a_jacket};}}
.a-skin {{fill: {a_skin};}}
.a-blue {{fill: {a_blue};}}
.a-gray {{fill: {a_gray};}}
text, tspan {{white-space: pre;}}
</style>
<defs>
<clipPath id="roundclip"><rect width="985" height="{h}" rx="12"/></clipPath>
</defs>
<g clip-path="url(#roundclip)">
<rect width="985" height="{h}" fill="{bg}"/>
<rect width="985" height="36" fill="{titlebar}"/>
<circle cx="22" cy="18" r="6" fill="#ff5f56"/>
<circle cx="44" cy="18" r="6" fill="#ffbd2e"/>
<circle cx="66" cy="18" r="6" fill="#27c93f"/>
<text x="492.5" y="22" text-anchor="middle" font-size="13px" class="muted">{title_text}</text>
<text x="15" y="64" fill="{text}"><tspan class="pg">lightsmite@github</tspan><tspan>:</tspan><tspan class="pb">~</tspan><tspan>$ neofetch</tspan></text>
<rect x="{cursor_x}" y="51" width="9" height="16" fill="{text}">
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.2s" repeatCount="indefinite"/>
</rect>
<text x="15" y="94" fill="{text}">
{art}
</text>
<text x="390" y="94" fill="{text}">
{info}
</text>
</g>
</svg>
"""

def build(filename, pal):
    art = art_block()
    info = "\n".join(f'<tspan x="390" y="{y}">{row}</tspan>' for y, row in ROWS)
    svg = TEMPLATE.format(
        h=HEIGHT, art=art, info=info,
        bg=pal["bg"], titlebar=pal["titlebar"], text=pal["text"],
        key=pal["key"], value=pal["value"], add=pal["add"], del_=pal["del"],
        cc=pal["cc"], muted=pal["muted"], pg=pal["pg"], pb=pal["pb"],
        a_hair=pal["a_hair"], a_jacket=pal["a_jacket"], a_skin=pal["a_skin"],
        a_blue=pal["a_blue"], a_gray=pal["a_gray"],
        title_text=E(TITLE_TEXT), cursor_x=f"{CURSOR_X:.1f}",
    )
    out = f"{OUT_DIR}/{filename}"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("wrote", out)

for fname, pal in PALETTES.items():
    build(fname, pal)
