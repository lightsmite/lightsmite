"""Color-quantized ASCII art of avatar.png for the profile SVG (v3).

Produces a coarse grid (<=38 cols x <=21 rows). Every cell gets:
  - a character: ' ' for background (a border-connected flood fill, not
    a raw white test -- see _background_mask), '.' for a sparse
    silhouette edge, otherwise a 3-step luminance ramp '@' (dark) /
    '#' (mid) / '+' (light) so shading and folds show as texture even
    where the color key is uniform;
  - a palette key, chosen by a majority vote of the hue/value class of
    the non-background pixels in that cell, with two minority boosts:
    'blue' (eyes) and 'ink' (eye outlines, mouth, whisker marks,
    headband edge) can win a cell without a majority, because those
    small dark/blue features are what make the face readable.

Classifying per-pixel and voting per-cell (rather than resizing/blurring
first) keeps each printed color region a single solid mass instead of
noisy per-pixel speckle.

Pure function; the only I/O is reading avatar.png next to this file.
"""
import colorsys
import os
from collections import deque

from PIL import Image

PALETTE_KEYS = ('ink', 'hair', 'jacket', 'skin', 'blue', 'gray')

_HERE = os.path.dirname(os.path.abspath(__file__))
_IMG_PATH = os.path.join(_HERE, 'avatar.png')

COLS = 38
ROWS = 21  # source is square (9.6/20 cell aspect wants ~18.2 rows for 38
# cols); the portrait is full-bleed with no whitespace margin to crop, so
# we spend the spec's full row budget on resolution instead (a mild ~15%
# vertical stretch is a fair trade for legible eyes/headband detail).


def _is_white(r, g, b):
    return r > 238 and g > 238 and b > 238


def _background_mask(img):
    """Flood fill from the four border edges over near-white pixels.

    Only white that is *connected to the canvas border* counts as
    background. This matters because the portrait is full-bleed (no
    clean margin) and has interior near-white pixels of its own (eye
    sclera, jacket trim highlights) that must NOT be punched out as
    blank space.
    """
    w, h = img.size
    px = img.load()
    bg = bytearray(w * h)
    dq = deque()

    def seed(x, y):
        idx = y * w + x
        if not bg[idx] and _is_white(*px[x, y]):
            bg[idx] = 1
            dq.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)

    while dq:
        x, y = dq.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h:
                idx = ny * w + nx
                if not bg[idx] and _is_white(*px[nx, ny]):
                    bg[idx] = 1
                    dq.append((nx, ny))
    return bg, w


def _classify_pixel(r, g, b):
    """Classify a *foreground* pixel into a PALETTE_KEYS entry, or
    'skip' if it's a white/near-white highlight that shouldn't sway the
    per-cell color vote (e.g. eye sclera, jacket trim highlight).

    The jacket/skin split is calibrated empirically from avatar.png:
    face pixels (x 160-290, y 150-280) cluster at s=0.2-0.5, v=0.7-1.0;
    jacket shoulder pixels cluster at s=0.7-1.0 (v down to 0.4 in the
    folds).  There is a natural saturation gap around 0.6, so warm hues
    split cleanly on s >= 0.62 -- NOT on value, and not at 0.48, which
    misfiled shadowed skin (s~0.5) as jacket.  Hair measures hue 30-55
    at s=0.7-1.0 (pale highlights down to s~0.4), hence the 32-75 band.
    """
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue = h * 360.0
    if v < 0.32:
        # Saturated dark navy (headband cloth, undershirt collar, iris
        # ring) is 'blue', not 'ink': 'ink' maps to the default text
        # color, which is LIGHT on the dark theme -- classifying the
        # navy masses as ink rendered them as a bright bib.  True
        # black/warm-dark outline pixels stay ink.
        if 195 <= hue <= 262 and s >= 0.45 and v >= 0.05:
            return 'blue'
        return 'ink'
    if s < 0.16:
        return 'gray' if v <= 0.85 else 'skip'
    if 175 <= hue <= 260:
        # Iris/headband blue is strongly saturated (s 0.45-0.95).
        # Desaturated blue-gray (s < 0.35) is the shading tone used in
        # the hair crevices and laptop shadows -- that's gray, and
        # letting it count as blue painted a blue blob into the hair.
        return 'blue' if s >= 0.35 else 'gray'
    if 32 <= hue <= 75:
        return 'hair'
    if hue <= 32 or hue >= 340:
        return 'jacket' if s >= 0.62 else 'skin'
    return 'ink'  # stray/edge-blend hue; treat as outline


def art_runs():
    """Return <=ROWS rows; each row is a list of (text, key) runs.

    Consecutive same-key cells are merged into one run, rows are
    right-stripped, and each row is <=38 characters total.
    """
    img = Image.open(_IMG_PATH).convert('RGB')
    w, h = img.size
    px = img.load()
    bg_mask, mw = _background_mask(img)

    cols, rows = COLS, ROWS
    cell_w = w / cols
    cell_h = h / rows

    grid_char = []
    grid_key = []
    for ry in range(rows):
        y0 = int(ry * cell_h)
        y1 = max(y0 + 1, int((ry + 1) * cell_h))
        char_row = []
        key_row = []
        for cx in range(cols):
            x0 = int(cx * cell_w)
            x1 = max(x0 + 1, int((cx + 1) * cell_w))

            total = 0
            bg_count = 0
            lum_sum = 0.0
            fg_count = 0
            counts = {}
            for yy in range(y0, y1):
                for xx in range(x0, x1):
                    total += 1
                    if bg_mask[yy * mw + xx]:
                        bg_count += 1
                        continue
                    r, g, b = px[xx, yy]
                    fg_count += 1
                    lum_sum += 0.299 * r + 0.587 * g + 0.114 * b
                    key = _classify_pixel(r, g, b)
                    if key != 'skip':
                        counts[key] = counts.get(key, 0) + 1
            bg_frac = (bg_count / total) if total else 1.0
            non_bg_total = sum(counts.values())

            if bg_frac >= 0.55 or non_bg_total == 0:
                # Decisive blank: the notches between hair spikes must
                # stay empty or the silhouette melts into a triangle.
                ch = ' '
                key = None
            else:
                # Minority boosts, in priority order: 'blue' (irises)
                # then 'ink' (eye outlines, mouth, whisker marks,
                # headband edge, fold lines).  Both are small features
                # that a plain majority vote erases into the
                # surrounding skin/jacket field.
                blue_n = counts.get('blue', 0)
                ink_n = counts.get('ink', 0)
                hair_n = counts.get('hair', 0)
                # The hair-guard (blue_n >= hair_n) stops the boost from
                # firing in hair-crevice cells, whose dark navy shading
                # shares the headband cloth's HSV signature; iris and
                # headband cells contain essentially no hair pixels.
                if blue_n and blue_n >= 0.22 * non_bg_total and blue_n >= hair_n:
                    key = 'blue'
                elif ink_n and ink_n >= 0.27 * non_bg_total:
                    key = 'ink'
                else:
                    key = max(counts.items(), key=lambda kv: kv[1])[0]
                if key == 'blue' and hair_n >= 0.20 * non_bg_total:
                    # A blue-majority cell with real hair presence is a
                    # navy shadow crevice INSIDE the hair mass (the
                    # shadow shares the headband cloth's HSV signature).
                    # Keep it hair-colored; its dark luminance already
                    # renders it as a chunky '@' so the shading shows.
                    # Headband/iris cells carry <=10% hair, so they are
                    # untouched.
                    key = 'hair'

                if bg_frac >= 0.32:
                    ch = '.'  # sparse silhouette edge
                elif key == 'ink':
                    # Dark features should be chunky in proportion to
                    # how much outline is actually in the cell.
                    ink_frac = ink_n / non_bg_total
                    ch = '@' if ink_frac >= 0.5 else '#'
                else:
                    # Texture: glyph by mean luminance of the cell's
                    # foreground pixels, so shading/folds read even
                    # inside a single-color mass.
                    lum = lum_sum / (fg_count * 255.0)
                    # 0.78 upper cut keeps the bright hair mass (mean
                    # lum ~0.77) at '#' so the silhouette stays dense;
                    # only true highlights (forehead, laptop lid sheen)
                    # thin out to '+'.
                    ch = '@' if lum < 0.40 else '#' if lum < 0.78 else '+'
            char_row.append(ch)
            key_row.append(key)
        grid_char.append(char_row)
        grid_key.append(key_row)

    out_rows = []
    for char_row, key_row in zip(grid_char, grid_key):
        n = len(char_row)
        while n > 0 and char_row[n - 1] == ' ':
            n -= 1
        char_row = char_row[:n]
        key_row = key_row[:n]

        runs = []
        buf = ''
        buf_key = None
        for ch, key in zip(char_row, key_row):
            k = key if key is not None else 'ink'
            if buf and k == buf_key:
                buf += ch
            else:
                if buf:
                    runs.append((buf, buf_key))
                buf = ch
                buf_key = k
        if buf:
            runs.append((buf, buf_key))
        out_rows.append(runs)
    return out_rows


if __name__ == '__main__':
    for row in art_runs():
        print(''.join(text for text, _ in row))
