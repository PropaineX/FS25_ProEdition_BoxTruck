import sys, os, math
from PIL import ImageDraw, Image
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'flat.py'), encoding='utf-8').read().split('panels = [')[0])

L = DECK_F - DECK_R
N, PWID = 3, 0.09


def Qz(z, y):
    return (int((z + 6.6) * S), int(TOPM + PH - 0.35 * S - (y - G) * S))


def boards_side(title, sub, down, load=False):
    im = side_panel(title, sub, 'none', load=load)
    d = ImageDraw.Draw(im, 'RGBA')
    for i in range(N):
        z0 = DECK_F - i * L / N; z1 = z0 - L / N
        if down:   # hanging from the hinge at the deck edge, outside the wheels
            y0, y1 = DECK1 - SB_H, DECK1
        else:
            y0, y1 = DECK1, DECK1 + SB_H
        d.rectangle([Qz(z1 + PWID / 2, y1), Qz(z0 - PWID / 2, y0)], fill=ALU + (240,), outline=ALU_D)
        for g in range(1, 4):
            yy = y0 + g * SB_H / 4
            d.line([Qz(z1 + PWID / 2, yy), Qz(z0 - PWID / 2, yy)], fill=ALU_D)
        ly = y0 + 0.08 if not down else y1 - 0.16
        d.rectangle([Qz(z0 - 0.35, ly + 0.08), Qz(z0 - 0.25, ly)], fill=STEEL)          # latch
        for hz in (z1 + 0.4, z0 - 0.6):                                                   # hinges on the deck edge
            d.rectangle([Qz(hz - 0.06, DECK1 + 0.03), Qz(hz + 0.06, DECK1 - 0.05)], fill=(60, 60, 64))
    for i in range(N + 1):                                                                # posts stay up
        z = DECK_F - i * L / N
        d.rectangle([Qz(z - PWID / 2, DECK1 + SB_H), Qz(z + PWID / 2, DECK0)], fill=ALU_D)
    return im


def boards_rear():
    im = Image.new('RGB', (PW, PH + TOPM), (245, 243, 236)); d = ImageDraw.Draw(im, 'RGBA')
    cx = PW * 0.5

    def Q(x, y):
        return (int(cx + x * S), int(TOPM + PH - 0.35 * S - (y - G) * S))

    def R(x0, x1, y0, y1, **kw):
        d.rectangle([Q(min(x0, x1), max(y0, y1)), Q(max(x0, x1), min(y0, y1))], **kw)

    R(-3.5, 3.5, G - 0.4, G, fill=(150, 135, 110))
    for x in (-1.0, 1.0):
        cxp, cyp = Q(x, G + 0.538)
        d.rectangle([cxp - 0.28 * S, cyp - 0.538 * S, cxp + 0.28 * S, cyp + 0.538 * S], fill=(35, 35, 35))
    R(-1.2, 1.2, 1.35, 3.738, fill=(240, 240, 238), outline=(90, 90, 90))
    R(-1.275, 1.275, DECK0, DECK1, fill=DECK, outline=(60, 50, 40))
    R(-1.15, 1.15, DECK1, HB_TOP, fill=ALU, outline=ALU_D)
    for k in range(1, 9):
        yy = DECK1 + k * (HB_TOP - DECK1) / 9; d.line([Q(-1.15, yy), Q(1.15, yy)], fill=ALU_D)
    # left side: board up; right side: board down + swing arc
    R(-1.275, -1.235, DECK1, DECK1 + SB_H, fill=ALU, outline=ALU_D)
    R(1.275, 1.315, DECK1 - SB_H, DECK1, fill=ALU, outline=ALU_D)
    hx, hy = Q(1.275, DECK1)
    r = SB_H * S
    d.arc([hx - r, hy - r, hx + r, hy + r], start=-90, end=90, fill=(190, 40, 30), width=3)
    ex, ey = Q(1.29, DECK1 - SB_H)
    d.polygon([(ex, ey), (ex + 10, ey - 14), (ex - 8, ey - 12)], fill=(190, 40, 30))
    d.text((Q(1.5, 0)[0], Q(0, DECK1 + 0.1)[1]), 'swings out and down\n(hinge on the deck edge)', fill=(190, 40, 30), font=F3)
    d.text((Q(-3.4, 0)[0], Q(0, DECK1 + 0.4)[1]), 'board up', fill=(60, 60, 60), font=F3)
    R(-1.275, 1.275, 0.62, 0.78, fill=(60, 60, 60))
    d.text((16, 12), 'Rear view: how a side board folds', fill=(20, 20, 20), font=F1)
    d.text((16, 54), 'left side shown up, right side shown folded down; the boards hang outside the wheels', fill=(50, 50, 50), font=F2)
    return im


a = boards_side('Side boards: up (driving)', 'X folds all side boards down on both sides; X again raises them', down=False)
b = boards_side('Press X: side boards folded down', 'boards hang from hinges on the deck edge; the posts between them stay up', down=True)
c = boards_rear()
out = Image.new('RGB', (a.width, a.height * 3 + 40), (255, 255, 255))
for i, p in enumerate((a, b, c)):
    out.paste(p, (0, i * (a.height + 20)))
out.save(sys.argv[1]); print(out.size)
