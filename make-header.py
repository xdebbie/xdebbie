#!/usr/bin/env python3
"""Generates bats-day-<hash>.svg (light mode), bats-night-<hash>.svg (dark mode) and README.md for the xdebbie GitHub profile:
pixel bats asleep upside down on a branch (light) or flying loops (dark), and a tiny signature in the
bottom-right corner with a blinking purple underscore."""
from pathlib import Path

W, H = 820, 220
NAME, PLACE = "deborah", "paris / barcelona"

WINGS_UP = [
    "#.............#",
    "##...........##",
    "###..#...#..###",
    ".####.###.####.",
    "..###########..",
    ".....#####.....",
    "......#.#......",
]
WINGS_DOWN = [
    "...............",
    ".....#...#.....",
    ".....#####.....",
    "...#########...",
    ".#############.",
    "##..#######..##",
    "#.....#.#.....#",
]
EYES = [(6, 3), (8, 3)]  # (col, row) in WINGS_UP; one row lower in WINGS_DOWN

# pixel size, flap period, flight duration, start offset, closed flight path
BATS = [
    (5, 0.32, 15, 0.0, "M120,110 C220,20 380,30 450,100 S640,190 720,90 S560,10 420,70 S180,190 120,110 Z"),
    (3, 0.24, 11, -4.0, "M640,60 C560,140 420,150 330,90 S140,20 90,80 S240,170 420,130 S700,10 640,60 Z"),
    (2, 0.20, 9, -2.0, "M300,40 C380,90 520,40 600,70 S700,150 560,150 S330,120 260,90 S220,10 300,40 Z"),
]


# Light mode: bats asleep upside down on a branch. 'e' = closed eye (half-height slit),
# 'w' = wing fold.
SLEEPING = [
    "...#.#...",
    "...#.#...",
    "..#####..",
    ".###w###.",
    ".##w#w##.",
    "##w#b#w##",
    "#w#bbb#w#",
    "#w#bbb#w#",
    "#w#bbb#w#",
    "##w#b#w##",
    ".#w###w#.",
    "#.#####.#",
    "..#####..",
    "..#e#e#..",
    "..#####..",
    "..##.##..",
    ".#.....#.",
]
BRANCH_Y = 52
# x of the feet, pixel size, sway angle, sway seconds, start offset, snores?
SLEEPERS = [
    (250, 6, 2.0, 5.4, 0.0, True),
    (390, 4, 3.0, 4.4, -1.7, False),
    (525, 5, 2.5, 6.0, -3.2, True),
]

THEMES = {
    "light": {"bat": "#24292f", "fold": "#57606a", "belly": "#353b43", "branch": "#d0d7de", "branch_hi": "#e6eaef", "leaf": "#b9c8b4", "eye": "#b026ff", "name": "#57606a", "place": "#8c959f",
              "cursor": "#b026ff"},
    "dark": {"bat": "#c9d1d9", "eye": "#c561ff", "name": "#8b949e", "place": "#6e7681",
             "cursor": "#c561ff"},
}
FONT = 'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"'


def sprite(rows, colour, px, eyes, eye_colour, dy=0):
    w, h = len(rows[0]) * px, len(rows) * px
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                fill = eye_colour if (x, y - dy) in eyes else colour
                out.append(f'<rect x="{x * px - w / 2:g}" y="{y * px - h / 2:g}" width="{px}" height="{px}" fill="{fill}"/>')
    return "".join(out)


def bat(t, px, flap, dur, begin, path):
    eyes_down = [(c, r + 1) for c, r in EYES]
    up = sprite(WINGS_UP, t["bat"], px, EYES, t["eye"])
    down = sprite(WINGS_DOWN, t["bat"], px, eyes_down, t["eye"])
    toggle = ('<animate attributeName="opacity" calcMode="discrete" values="{a};{b}" '
              f'dur="{flap}s" repeatCount="indefinite"/>')
    return (f'<g><animateMotion path="{path}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite" '
            'calcMode="paced"/>'
            f'<g>{up}{toggle.format(a=1, b=0)}</g>'
            f'<g opacity="0">{down}{toggle.format(a=0, b=1)}</g></g>')



def sleeper(t, x, px, angle, sway, begin, snores):
    w = len(SLEEPING[0]) * px
    colours = {"#": t["bat"], "w": t["fold"], "b": t["belly"]}
    rects = []
    for r, row in enumerate(SLEEPING):
        for c, ch in enumerate(row):
            if ch in colours:
                rects.append(f'<rect x="{c * px - w / 2:g}" y="{r * px}" width="{px}" height="{px}" '
                             f'fill="{colours[ch]}"/>')
            elif ch == "e":
                rects.append(f'<rect x="{c * px - w / 2:g}" y="{r * px + px / 2:g}" width="{px}" '
                             f'height="{max(1, px // 3)}" fill="{t["eye"]}"/>')
    ease = 'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" keyTimes="0;0.5;1"'
    swing = (f'<animateTransform attributeName="transform" type="rotate" values="{-angle};{angle};{-angle}" '
             f'{ease} dur="{sway}s" begin="{begin}s" repeatCount="indefinite"/>')
    breath = (f'<animateTransform attributeName="transform" type="scale" values="1,1;1.04,1.025;1,1" '
              f'{ease} dur="{sway * 0.7:.2f}s" begin="{begin}s" repeatCount="indefinite"/>')
    out = [f'<g transform="translate({x},{BRANCH_Y})"><g>{swing}<g>{"".join(rects)}{breath}</g></g></g>']
    if snores:
        h = len(SLEEPING) * px
        for i, (glyph, size) in enumerate([("z", 14), ("Z", 19), ("z", 15)]):
            delay = begin + i * 1.3
            out.append(
                f'<text x="{x + w / 2 + 6:g}" y="{BRANCH_Y + h * 0.78:g}" {FONT} font-size="{size}" '
                f'fill="{t["eye"]}" opacity="0">{glyph}'
                f'<animateTransform attributeName="transform" type="translate" values="0,0;22,-46" '
                f'dur="3.9s" begin="{delay:g}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0.55;0" keyTimes="0;0.3;1" '
                f'dur="3.9s" begin="{delay:g}s" repeatCount="indefinite"/></text>')
    return "".join(out)


def branch(t):
    y, out = BRANCH_Y - 4, []
    sag = lambda x: 2 if 330 < x < 470 else 0
    for x in range(150, 660, 4):
        out.append(f'<rect x="{x}" y="{y + sag(x)}" width="4" height="4" fill="{t["branch"]}"/>')
        if x % 12 == 2:
            out.append(f'<rect x="{x}" y="{y + sag(x)}" width="4" height="2" fill="{t["branch_hi"]}"/>')
    for x, d in [(186, -1), (470, 1), (622, -1)]:  # twigs
        out.append(f'<rect x="{x}" y="{y - 4 if d < 0 else y + 4}" width="4" height="4" fill="{t["branch"]}"/>')
        out.append(f'<rect x="{x + 4 * d}" y="{y - 8 if d < 0 else y + 8}" width="4" height="4" fill="{t["branch"]}"/>')
    for lx, ly in [(178, y - 16), (634, y - 16)]:  # leaves on the upward twigs
        for dx, dy in [(0, 4), (4, 0), (4, 4), (8, 0)]:
            out.append(f'<rect x="{lx + dx}" y="{ly + dy}" width="4" height="4" fill="{t["leaf"]}"/>')
    return "".join(out)


def build(theme):
    t = THEMES[theme]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'shape-rendering="crispEdges" role="img" aria-label="pixel bats, {NAME}, {PLACE}">']
    if theme == "light":
        out.append(branch(t))
        out += [sleeper(t, *b) for b in SLEEPERS]
    else:
        out += [bat(t, *b) for b in BATS]

    cx, base = W - 24, H - 34          # cursor x, name baseline
    out.append(f'<text x="{cx - 3}" y="{base}" text-anchor="end" {FONT} font-size="13" '
               f'fill="{t["name"]}">{NAME}</text>')
    out.append(f'<rect x="{cx}" y="{base - 2}" width="8" height="2" fill="{t["cursor"]}">'
               '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
               'dur="1.1s" repeatCount="indefinite"/></rect>')
    out.append(f'<text x="{cx + 8}" y="{base + 17}" text-anchor="end" {FONT} font-size="10" '
               f'fill="{t["place"]}">{PLACE}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


README = """<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{night}">
  <img alt="pixel bats · {name} · {place}" src="{day}">
</picture>
"""

if __name__ == "__main__":
    import hashlib
    here = Path(__file__).resolve().parent
    for old in here.glob("bats-*.svg"):
        old.unlink()
    names = {}
    for theme, label in (("light", "day"), ("dark", "night")):
        svg = build(theme)
        # content hash in the name, so GitHub's image cache never serves a stale version
        name = f"bats-{label}-{hashlib.sha1(svg.encode()).hexdigest()[:8]}.svg"
        (here / name).write_text(svg)
        names[label] = name
        print(name)
    (here / "README.md").write_text(README.format(name=NAME, place=PLACE, **names))
