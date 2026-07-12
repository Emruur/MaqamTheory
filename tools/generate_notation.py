"""Generate staff-notation SVGs (AEU accidentals) for the maqam site.

Usage: python3 tools/generate_notation.py
Writes img/*.svg. No dependencies; hand-rolled SVG.

Coordinates: staff lines at y = 0,10,20,30,40 (top->bottom), bottom line = E4.
One diatonic step = 5 units.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import makam_data as md

OUT = Path(__file__).parent.parent / "img"

LETTERS = "CDEFGAB"

# Written spelling for each comma position used on the site.
# accidental kinds: flat1 koma (mirrored b), flat4 bakiye (b + stroke),
# flat5 kucuk mucenneb (plain b), flat8 buyuk mucenneb (b + double stroke),
# sharp1 koma (one-stroke sharp), sharp4 bakiye (plain #),
# sharp5 kucuk muc. (one-stroke # + slash), sharp8 buyuk muc. (# + slash).
SPELL = {
    9:  ("D", 4, None),
    18: ("E", 4, None),
    22: ("F", 4, None),
    26: ("F", 4, "sharp4"),
    31: ("G", 4, None),
    40: ("A", 4, None),
    44: ("B", 4, "flat5"),
    45: ("B", 4, "flat4"),
    48: ("B", 4, "flat1"),
    49: ("B", 4, None),
    53: ("C", 5, None),
    57: ("C", 5, "sharp4"),
    58: ("C", 5, "sharp5"),
    62: ("D", 5, None),
    66: ("E", 5, "flat5"),
    67: ("E", 5, "flat4"),
    71: ("E", 5, None),
    75: ("F", 5, None),
    79: ("F", 5, "sharp4"),
    84: ("G", 5, None),
    93: ("A", 5, None),
    97: ("B", 5, "flat5"),
    101: ("B", 5, "flat1"),
    102: ("B", 5, None),
    106: ("C", 6, None),
}

PERDE_NAME = {v: k for k, v in md.PERDE.items()}

KEY_SIGNATURES = {
    "rast":     [(48, ), (79, )],
    "nihavend": [(44, ), (66, )],
    "ussak":    [(48, )],
    "huseyni":  [(48, ), (79, )],
    "hicaz":    [(45, ), (57, )],
}

ACCIDENTAL_LABELS = {
    "flat1": "koma bemolu (1)", "flat4": "bakiye bemolu (4)",
    "flat5": "kucuk mucenneb bemolu (5)", "flat8": "buyuk mucenneb bemolu (8)",
    "sharp1": "koma diyezi (1)", "sharp4": "bakiye diyezi (4)",
    "sharp5": "kucuk mucenneb diyezi (5)", "sharp8": "buyuk mucenneb diyezi (8)",
    "natural": "naturel",
}


def step_of(letter: str, octave: int) -> int:
    return (octave - 4) * 7 + LETTERS.index(letter)


def y_of(step: int) -> float:
    return 40 - (step - 2) * 5


class SVG:
    def __init__(self, width, height, ox=0, oy=0):
        self.w, self.h = width, height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-ox} {-oy} '
            f'{width} {height}" width="{width}" height="{height}" '
            f'font-family="Georgia, serif">',
            f'<rect x="{-ox}" y="{-oy}" width="{width}" height="{height}" fill="#fffdf7"/>',
        ]

    def line(self, x1, y1, x2, y2, w=1.1, color="#2b2b2b", cap="butt"):
        self.parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}"/>')

    def path(self, d, w=1.6, fill="none", color="#2b2b2b", transform=""):
        t = f' transform="{transform}"' if transform else ""
        self.parts.append(
            f'<path d="{d}" stroke="{color}" stroke-width="{w}" fill="{fill}" '
            f'stroke-linecap="round" stroke-linejoin="round"{t}/>')

    def ellipse(self, cx, cy, rx, ry, rot=0, fill="#2b2b2b", stroke="none", sw=0):
        self.parts.append(
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx}" ry="{ry}" '
            f'transform="rotate({rot} {cx:.1f} {cy:.1f})" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=11, anchor="middle", color="#444",
             style="", weight="normal"):
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{color}" font-weight="{weight}" '
            f'style="{style}">{s}</text>')

    def begin_group(self, ty):
        self.parts.append(f'<g transform="translate(0 {ty:.1f})">')

    def end_group(self):
        self.parts.append("</g>")

    def save(self, name):
        OUT.mkdir(exist_ok=True)
        self.parts.append("</svg>")
        (OUT / name).write_text("\n".join(self.parts), encoding="utf-8")
        print(f"  img/{name}")


def draw_staff(svg: SVG, x0: float, x1: float):
    for i in range(5):
        svg.line(x0, i * 10, x1, i * 10, w=1.1, color="#555")


def draw_clef(svg: SVG, x: float):
    """Stylized treble clef: tall sweep with a spiral around the G line (y=30)."""
    d = (
        f"M {x-0.5} 45 "
        f"C {x+0.5} 34 {x+2.5} 14 {x+3} -2 "          # main stem sweeping up
        f"C {x+3.2} -12 {x+1} -19 {x-2} -15 "         # top bulb hooking left
        f"C {x-4.5} -11.5 {x-3} -4 {x+0.5} 2 "        # back down the front
        f"C {x+4} 8.5 {x+9.5} 14 {x+9.5} 24 "         # bulge right toward G line
        f"C {x+9.5} 33 {x+2.5} 37.5 {x-3.5} 34.5 "    # around the bottom
        f"C {x-9} 31.5 {x-8} 22.5 {x-1.5} 21.5 "      # left side, spiral up
        f"C {x+3} 21 {x+5.5} 25 {x+4} 29 "            # into the spiral centre
    )
    svg.path(d, w=2.5)
    # Bottom tail and curl.
    svg.path(f"M {x-0.5} 45 C {x-1} 50 {x-7.5} 51 {x-8} 46.5 "
             f"C {x-8.2} 43.5 {x-5} 42.5 {x-3.5} 45", w=2.2)


def draw_notehead(svg: SVG, x, y, hollow=True):
    if hollow:
        svg.ellipse(x, y, 6.2, 4.4, rot=-16, fill="#fffdf7",
                    stroke="#2b2b2b", sw=2.2)
    else:
        svg.ellipse(x, y, 5.6, 4.1, rot=-16, fill="#2b2b2b")


def draw_ledger(svg: SVG, x, step):
    """Ledger lines for notes below/above the staff."""
    s = step
    while s <= 0:                       # C4 and below
        if s % 2 == 0:
            svg.line(x - 10, y_of(s), x + 10, y_of(s), w=1.2, color="#555")
        s += 1
    s = step
    while s >= 12:                      # A5 ... above? A5 sits above top line
        if s % 2 == 0:
            svg.line(x - 10, y_of(s), x + 10, y_of(s), w=1.2, color="#555")
        s -= 1


def draw_flat(svg: SVG, x, y, mirrored=False, strokes=0):
    """Flat glyph centred at notehead height y; x = glyph centre."""
    sgn = -1 if mirrored else 1
    stem_x = x - 2.5 * sgn
    svg.path(f"M {stem_x} {y-16} L {stem_x} {y+7.5}", w=1.5)
    d = (f"M {stem_x} {y+7.5} "
         f"C {stem_x + 8*sgn} {y+1} {stem_x + 7*sgn} {y-4.5} {stem_x} {y-1.5}")
    svg.path(d, w=1.5)
    for i in range(strokes):
        yy = y - 9 - i * 4.5
        svg.path(f"M {x-4.5} {yy+2.5} L {x+4.5} {yy-2.5}", w=1.3)


def draw_sharp(svg: SVG, x, y, verticals=2, slash=False):
    if verticals == 2:
        svg.line(x - 2.1, y - 11, x - 2.1, y + 12, w=1.4)
        svg.line(x + 2.1, y - 12, x + 2.1, y + 11, w=1.4)
    else:
        svg.line(x, y - 11.5, x, y + 11.5, w=1.4)
    for yy in (y - 3.6, y + 4.4):
        svg.path(f"M {x-5} {yy+1.6} L {x+5} {yy-1.6}", w=2.6)
    if slash:
        svg.path(f"M {x-6} {y+10} L {x+6} {y-13}", w=1.3)


def draw_natural(svg: SVG, x, y):
    svg.line(x - 2.1, y - 10, x - 2.1, y + 4.5, w=1.4)
    svg.line(x + 2.1, y - 4.5, x + 2.1, y + 10, w=1.4)
    for yy in (y - 3.2, y + 3.2):
        svg.path(f"M {x-2.1} {yy+1.4} L {x+2.1} {yy-1.4}", w=2.4)


def draw_accidental(svg: SVG, kind: str, x, y):
    if kind == "flat1":
        draw_flat(svg, x, y, mirrored=True)
    elif kind == "flat4":
        draw_flat(svg, x, y, strokes=1)
    elif kind == "flat5":
        draw_flat(svg, x, y)
    elif kind == "flat8":
        draw_flat(svg, x, y, strokes=2)
    elif kind == "sharp1":
        draw_sharp(svg, x, y, verticals=1)
    elif kind == "sharp4":
        draw_sharp(svg, x, y)
    elif kind == "sharp5":
        draw_sharp(svg, x, y, verticals=1, slash=True)
    elif kind == "sharp8":
        draw_sharp(svg, x, y, slash=True)
    elif kind == "natural":
        draw_natural(svg, x, y)


def western_name(letter, acc):
    suffix = {
        None: "", "flat1": "↓¹", "flat4": "♭⁴", "flat5": "♭",
        "sharp4": "♯", "sharp5": "♯⁵",
    }.get(acc, "")
    return letter + suffix


def scale_svg(name, pitches, keysig, title=None, show_steps=True,
              inline_all=False):
    """One-line scale with key signature, perde names, and comma steps."""
    n = len(pitches)
    note_dx = 58
    x_notes = 40 + 30 + 18 * len(keysig) + 26
    width = x_notes + n * note_dx + 10
    svg = SVG(width, 128, ox=6, oy=26)
    draw_staff(svg, 0, width - 16)
    draw_clef(svg, 14)

    sig_acc = {}   # letter -> accidental in signature
    x = 42
    for (commas,) in keysig:
        letter, octv, acc = SPELL[commas]
        sig_acc[letter] = acc
        draw_accidental(svg, acc, x, y_of(step_of(letter, octv)))
        x += 17

    for i, commas in enumerate(pitches):
        letter, octv, acc = SPELL[commas]
        cx = x_notes + i * note_dx
        step = step_of(letter, octv)
        y = y_of(step)
        shown = sig_acc.get(letter, "__none__")
        if inline_all and acc:
            draw_accidental(svg, acc, cx - 14, y)
        elif acc != sig_acc.get(letter) and (acc or letter in sig_acc):
            draw_accidental(svg, acc or "natural", cx - 14, y)
        draw_ledger(svg, cx, step)
        draw_notehead(svg, cx, y)
        perde = PERDE_NAME.get(commas, "")
        svg.text(cx, 66, perde, size=10.5, color="#7a5c2e",
                 style="font-style:italic")
        svg.text(cx, -12, western_name(letter, acc), size=10.5, color="#555")
        if show_steps and i < n - 1:
            step_c = pitches[i + 1] - commas
            svg.text(cx + note_dx / 2, 84, str(step_c), size=12,
                     color="#a33", weight="bold")
    if show_steps:
        svg.text(x_notes - 30, 84, "commas:", size=10, color="#a33",
                 anchor="end")
    if title:
        svg.text(0, -16, title, size=13, anchor="start", color="#333",
                 weight="bold")
    svg.save(name)


def genus_svg(name, genus_name, root, label):
    pitches = md.steps_to_scale(root, md.GENUS[genus_name])
    scale_svg(name, pitches, [], title=label, inline_all=True)


def draw_rest(svg: SVG, x, y=20):
    """Simple stylized quarter/eighth rest squiggle on the middle of the staff."""
    svg.path(f"M {x-2.5} {y-8} L {x+2.5} {y-2} C {x-2} {y+2} {x-2} {y+4} "
             f"{x+2} {y+8}", w=2.0)


def draw_note(svg: SVG, cx, commas, beats, sig_acc):
    """One rhythmic note. Returns nothing. Supports 0.25..3.5 beats."""
    letter, octv, acc = SPELL[commas]
    step = step_of(letter, octv)
    y = y_of(step)
    if acc != sig_acc.get(letter) and (acc or letter in sig_acc):
        draw_accidental(svg, acc or "natural", cx - 13, y)
    draw_ledger(svg, cx, step)
    hollow = beats >= 2
    if hollow:
        svg.ellipse(cx, y, 5.6, 4.1, rot=-16, fill="#fffdf7",
                    stroke="#2b2b2b", sw=1.9)
    else:
        svg.ellipse(cx, y, 5.4, 4.0, rot=-16, fill="#2b2b2b")
    stem_up = step < 8
    if stem_up:
        sx, sy1, sy2 = cx + 5.2, y - 1.5, y - 30
    else:
        sx, sy1, sy2 = cx - 5.2, y + 1.5, y + 30
    svg.line(sx, sy1, sx, sy2, w=1.4)
    d = 1 if stem_up else -1
    nflags = 2 if beats == 0.25 else (1 if beats in (0.5, 0.75) else 0)
    for f in range(nflags):
        fy = sy2 + f * 7 * d
        svg.path(f"M {sx} {fy} C {sx+7} {fy + 6*d} {sx+4} {fy + 12*d} "
                 f"{sx+6.5} {fy + 17*d}", w=1.7)
    if beats in (0.75, 1.5, 3, 3.5):
        dot_y = y - 3 if step % 2 == 0 else y
        svg.ellipse(cx + 9.5, dot_y, 1.7, 1.7, fill="#2b2b2b")


def melody_svg(name, events, keysig, title=None, beats_per_bar=None,
               max_slots=18, note_dx=34):
    """Rhythmic melody, wrapped into multiple staff systems.

    events: (commas, beats); None commas = rest. Barlines drawn when
    beats_per_bar is given. Systems break at barlines after ~max_slots notes.
    """
    # Split events into systems, breaking at barlines where possible.
    systems, cur, cum = [], [], 0.0
    for commas, beats in events:
        cur.append((commas, beats, cum))
        cum += beats
        at_bar = beats_per_bar and abs(cum % beats_per_bar) < 1e-6
        if len(cur) >= max_slots and (at_bar or not beats_per_bar or
                                      len(cur) >= max_slots + 6):
            systems.append(cur)
            cur = []
    if cur:
        if systems and len(cur) <= 3:
            systems[-1].extend(cur)
        else:
            systems.append(cur)

    sys_h = 128
    x_head = 40 + 18 * len(keysig) + 24
    n_widest = max(len(s) for s in systems)
    width = x_head + n_widest * note_dx + 16
    svg = SVG(width, sys_h * len(systems) + 34, ox=6, oy=30)

    for si, sys_events in enumerate(systems):
        ty = si * sys_h
        svg.begin_group(ty)
        sys_w = x_head + len(sys_events) * note_dx - 4
        draw_staff(svg, 0, sys_w)
        draw_clef(svg, 14)
        sig_acc = {}
        x = 42
        for (commas,) in keysig:
            letter, octv, acc = SPELL[commas]
            sig_acc[letter] = acc
            draw_accidental(svg, acc, x, y_of(step_of(letter, octv)))
            x += 17
        for i, (commas, beats, start) in enumerate(sys_events):
            cx = x_head + i * note_dx
            if commas is None:
                draw_rest(svg, cx)
            else:
                draw_note(svg, cx, commas, beats, sig_acc)
            end = start + beats
            if beats_per_bar and abs(end % beats_per_bar) < 1e-6:
                bx = cx + note_dx / 2 + 3
                if i == len(sys_events) - 1:
                    bx = cx + note_dx / 2 + 6
                svg.line(bx, 0, bx, 40, w=1.2, color="#777")
        svg.end_group()
    if title:
        svg.text(0, -18, title, size=13, anchor="start", color="#333",
                 weight="bold")
    svg.save(name)


def accidental_table_svg():
    """Reference chart: all AEU accidentals with names and comma values."""
    kinds = [
        ("sharp1", "Koma diyezi", "+1 koma"),
        ("sharp4", "Bakiye diyezi", "+4 koma"),
        ("sharp5", "K. mucenneb diyezi", "+5 koma"),
        ("sharp8", "B. mucenneb diyezi", "+8 koma"),
        ("flat1", "Koma bemolu", "-1 koma"),
        ("flat4", "Bakiye bemolu", "-4 koma"),
        ("flat5", "K. mucenneb bemolu", "-5 koma"),
        ("flat8", "B. mucenneb bemolu", "-8 koma"),
    ]
    dx = 118
    width = 60 + dx * len(kinds)
    svg = SVG(width, 130, ox=10, oy=40)
    y = 20
    for i, (kind, tname, delta) in enumerate(kinds):
        x = 45 + i * dx
        draw_accidental(svg, kind, x, y)
        svg.text(x, 52, tname, size=10, color="#333")
        svg.text(x, 66, delta, size=10.5, color="#a33", weight="bold")
    svg.save("accidentals_table.svg")


def perde_ladder_svg():
    """The main perdeler from rast to tiz cargah on the staff."""
    ladder = [31, 40, 44, 45, 48, 49, 53, 57, 62, 66, 67, 71, 75, 79, 84, 93]
    note_dx = 52
    x_notes = 62
    width = x_notes + len(ladder) * note_dx + 8
    svg = SVG(width, 150, ox=6, oy=30)
    draw_staff(svg, 0, width - 14)
    draw_clef(svg, 14)
    for i, commas in enumerate(ladder):
        letter, octv, acc = SPELL[commas]
        cx = x_notes + i * note_dx
        step = step_of(letter, octv)
        y = y_of(step)
        if acc:
            draw_accidental(svg, acc, cx - 14, y)
        draw_ledger(svg, cx, step)
        draw_notehead(svg, cx, y)
        ty = 64 if i % 2 == 0 else 80
        svg.text(cx, ty, PERDE_NAME.get(commas, ""), size=10.5,
                 color="#7a5c2e", style="font-style:italic")
        svg.text(cx, -12, western_name(letter, acc), size=10, color="#555")
    svg.save("perde_ladder.svg")


def keysig_svg(makam):
    """Small key-signature-only image for chapter headers."""
    keysig = KEY_SIGNATURES[makam]
    width = 60 + 20 * len(keysig)
    svg = SVG(width, 96, ox=6, oy=24)
    draw_staff(svg, 0, width - 14)
    draw_clef(svg, 14)
    x = 42
    for (commas,) in keysig:
        letter, octv, acc = SPELL[commas]
        draw_accidental(svg, acc, x, y_of(step_of(letter, octv)))
        x += 17
    svg.save(f"keysig_{makam}.svg")


def main():
    print("writing SVGs:")
    for key, m in md.MAKAMLAR.items():
        keysig = KEY_SIGNATURES[key]
        scale_svg(f"scale_{key}_asc.svg", m["asc"], keysig)
        if m["desc"] != m["asc"]:
            scale_svg(f"scale_{key}_desc.svg", list(reversed(m["desc"])), keysig)
        keysig_svg(key)

    for gname, (genus_name, root) in md.GENUS_DEMOS.items():
        pretty = genus_name.replace("dortlusu", "tetrachord (dortlu)")
        genus_svg(f"genus_{gname}.svg", genus_name, root,
                  f"{gname.capitalize()} {pretty.split(' ', 1)[1]} on dugah (A)")

    # The five makams' own genera (lower + upper) for their chapters.
    for key, m in md.MAKAMLAR.items():
        for part in ("lower_genus", "upper_genus"):
            label, genus_name, root = m[part]
            genus_svg(f"{key}_{part}.svg", genus_name, root, label)

    for key, m in md.MAKAMLAR.items():
        melody_svg(f"seyir_{key}.svg", m["seyir"], KEY_SIGNATURES[key],
                   title=f"{m['title']} seyir sketch")

    for key, song in md.SONGS.items():
        melody_svg(f"song_{key}.svg", song["events"], KEY_SIGNATURES[key],
                   title=song["title"],
                   beats_per_bar=song["beats_per_bar"], note_dx=32)

    accidental_table_svg()
    perde_ladder_svg()
    print("done")


if __name__ == "__main__":
    main()
