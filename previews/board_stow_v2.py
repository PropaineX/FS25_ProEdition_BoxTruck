"""v2 (user, 2026-10-24): the boards go in CROSSWAYS, end-first: from the side only their ends show, in stacks
(4 stacks of 3). Otherwise as v1.
Mock-up (user, 2026-10-24): when the curtain opens, the side boards don't vanish but are put away in the gap
between the body and the fuel tank. Drawn on the user's own screenshot (left side, curtain open).
Usage: python -I previews\\board_stow_v1.py <screenshot.png> <out.png>"""
import sys

from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
shot = Image.open(src).convert("RGB")
K = 1.28                                    # screenshot px per the coordinates below (measured on the 2000 px view)

BOARD = (104, 44, 26)
BOARD_HI = (140, 66, 38)
BOARD_LO = (60, 24, 14)
ARROW = (255, 214, 64)

# near-side board slots in the opening (4 rows x 3 bays), 2000-px coordinates; the floor edge is at ~690, 165 px/m
ROWS = [629, 563, 497, 431]
BAYS = [(140, 505), (522, 892), (910, 1265)]
BOARD_H = 24
# the gap between the body's bottom rail and the fuel tank (front of the rear wheels to the cab)
GAP = (948, 754, 1282, 774)


def board(d, x0, y0, x1, y1):
    d.rectangle([x0 * K, y0 * K, x1 * K, y1 * K], fill=BOARD)
    d.line([x0 * K, y0 * K, x1 * K, y0 * K], fill=BOARD_HI, width=3)
    d.line([x0 * K, y1 * K, x1 * K, y1 * K], fill=BOARD_LO, width=3)


def arrow(d, x0, y0, x1, y1):
    d.line([x0 * K, y0 * K, x1 * K, y1 * K], fill=ARROW, width=7)
    import math
    a = math.atan2(y1 - y0, x1 - x0)
    for s in (-0.5, 0.5):
        d.line([x1 * K, y1 * K, (x1 - 22 * math.cos(a + s)) * K, (y1 - 22 * math.sin(a + s)) * K], fill=ARROW, width=7)


END_W, END_H = 26, 6                         # board end seen from the side: ~0.15 m wide, ~0.035 m thick
END = (176, 118, 72)
END_EDGE = (66, 34, 18)
STACKS = 4


def board_end(d, x, y):
    """one board end (end grain), x/y = top-left in 2000-px coordinates"""
    d.rectangle([x * K, y * K, (x + END_W) * K, (y + END_H) * K], fill=END, outline=END_EDGE, width=2)
    d.line([(x + 4) * K, (y + END_H / 2) * K, (x + END_W - 4) * K, (y + END_H / 2 - 1) * K], fill=(150, 96, 56), width=2)


def stored(d, count):
    """count boards lying crossways in the gap: their ends, in STACKS stacks filled bottom-up, left to right"""
    x0, y0, x1, y1 = GAP
    d.rectangle([x0 * K, y0 * K, x1 * K, y1 * K], fill=(18, 16, 15))          # dark space behind the ends
    per = 3
    spacing = (x1 - x0 - STACKS * END_W) / (STACKS + 1)
    for k in range(count):
        s, level = k // per, k % per
        x = x0 + spacing + s * (END_W + spacing)
        y = y1 - (level + 1) * (END_H + 0.5)
        board_end(d, x, y)


def panel(step):
    im = shot.copy()
    d = ImageDraw.Draw(im)
    if step == 1:
        for y in ROWS:
            for a, b in BAYS:
                board(d, a, y - BOARD_H / 2, b, y + BOARD_H / 2)
    elif step == 2:
        # top rows already put away, the next board on its way down, the lower boards still waiting
        for y in ROWS[:2]:
            for a, b in BAYS:
                board(d, a, y - BOARD_H / 2, b, y + BOARD_H / 2)
        board(d, 910, 650, 1265, 674)                 # front board of row 3 sliding down the side
        arrow(d, 1090, 500, 1090, 640)
        arrow(d, 1090, 690, 1150, 750)
        stored(d, 4)
    else:
        stored(d, 12)
        x0, y0, x1, y1 = GAP
        d.rectangle([(x0 - 6) * K, (y0 - 6) * K, (x1 + 6) * K, (y1 + 6) * K], outline=ARROW, width=4)
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)


panels = [panel(k) for k in (1, 2, 3)]
titles = ["1. Curtain opens: the boards are still in place",
          "2. One by one they slide down and in under the body, crossways, end first",
          "3. Curtain open: you see the board ends, stacked in the gap above the tank"]
font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 30)
pw, ph = panels[0].size
sheet = Image.new("RGB", (pw, (ph + 60) * 3), (38, 38, 38))
d = ImageDraw.Draw(sheet)
for k, (p, t) in enumerate(zip(panels, titles)):
    y = k * (ph + 60)
    d.text((16, y + 12), t, font=font, fill=(240, 220, 120))
    sheet.paste(p, (0, y + 60))
sheet.save(out)
# a close-up of the stored boards
close = panel(3).crop((int(900 * K / 2), int(700 * K / 2), int(1330 * K / 2), int(820 * K / 2)))
close = close.resize((close.width * 3, close.height * 3), Image.LANCZOS)
close.save(out.replace(".png", "_closeup.png"))
print("saved", out, sheet.size)
