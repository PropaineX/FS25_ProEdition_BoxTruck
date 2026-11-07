import sys, os
from PIL import ImageDraw, Image
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'flat.py'), encoding='utf-8').read().split('panels = [')[0]
exec(src)   # truck drawing helpers from the flatbed mock-up (same sizes)

L = DECK_F - DECK_R
CLOSED = [DECK_F - 0.25 - i * (L - 0.5) / 5 for i in range(6)][::-1]     # left (rear) to right (front): stake 1..6
GAP = 0.14                                                                 # centre distance when a stake sits next to its partner
OPEN = list(CLOSED)
for a, b in ((0, 1), (2, 3), (4, 5)):
    OPEN[a] = CLOSED[b] - GAP


def Qz(z, y):
    return (int((z + 6.6) * S), int(TOPM + PH - 0.35 * S - (y - G) * S))


def stakes_panel(title, sub, zs, moved=None, load=False):
    im = side_panel(title, sub, 'none', load=load)
    d = ImageDraw.Draw(im, 'RGBA')
    # slide rail along the deck edge
    d.rectangle([Qz(DECK_R + 0.05, DECK0 + 0.02), Qz(DECK_F - 0.05, DECK0 - 0.07)], fill=(70, 70, 75))
    for n, z in enumerate(zs, 1):
        col = (190, 40, 30) if n in (1, 3, 5) else STEEL
        d.rectangle([Qz(z - 0.045, DECK1 + ST_H), Qz(z + 0.045, DECK0 - 0.07)], fill=col)
        d.rectangle([Qz(z - 0.075, DECK0 + 0.03), Qz(z + 0.075, DECK0 - 0.08)], fill=(90, 90, 95))      # slide shoe
        tx, ty = Qz(z, DECK1 + ST_H + 0.12)
        if n in (1, 3, 5) and zs[n] - z < 0.3:
            tx -= 34; d.line([(tx + 12, ty - 4), Qz(z, DECK1 + ST_H)], fill=col, width=2)
        d.ellipse([tx - 15, ty - 30, tx + 15, ty], fill=(255, 255, 255), outline=col, width=3)
        d.text((tx - 6, ty - 27), str(n), fill=(20, 20, 20), font=F2)
    if moved:
        for a in (0, 2, 4):
            x0, y0 = Qz(moved[a], DECK1 + ST_H * 0.55); x1, _ = Qz(zs[a] - 0.12, 0)
            d.line([(x0, y0), (x1, y0)], fill=(190, 40, 30, 200), width=4)
            d.polygon([(x1, y0), (x1 - 14, y0 - 9), (x1 - 14, y0 + 9)], fill=(190, 40, 30, 200))
            gx0, _ = Qz(moved[a] - 0.045, 0)
            d.rectangle([gx0, Qz(0, DECK1 + ST_H)[1], gx0 + int(0.09 * S), Qz(0, DECK0 - 0.07)[1]], outline=(190, 40, 30, 160), width=2)
        # gap labels
        edges = [DECK_R] + [zs[1] + 0.045, zs[3] + 0.045]
        for e0, e1 in ((DECK_R, zs[0] - 0.045), (zs[1] + 0.045, zs[2] - 0.045), (zs[3] + 0.045, zs[4] - 0.045)):
            xa, ya = Qz(e0, DECK1 + 0.35); xb, _ = Qz(e1, 0)
            d.line([(xa, ya), (xb, ya)], fill=(20, 110, 40), width=2)
            d.text(((xa + xb) // 2 - 30, ya - 24), '%.1f m' % (e1 - e0), fill=(20, 110, 40), font=F2)
    return im


a = stakes_panel('Stake posts: closed (driving)', 'numbered left to right: 1 at the back ... 6 behind the headboard; red = the ones that move', CLOSED)
b = stakes_panel('Press X: 1, 3 and 5 slide forward next to 2, 4 and 6', 'animated along a rail on the deck edge (both sides together); press X again to slide them back',
                 OPEN, moved=CLOSED)
c = stakes_panel('Open, loading two layers of goat milk pallets', 'gaps for a forklift from the side; Shift+R (Universal Autoload) works either way', OPEN, load=True)
out = Image.new('RGB', (a.width, a.height * 3 + 40), (255, 255, 255))
for i, p in enumerate((a, b, c)):
    out.paste(p, (0, i * (a.height + 20)))
out.save(sys.argv[1]); print(out.size)
print('closed', ['%.2f' % z for z in CLOSED]); print('open', ['%.2f' % z for z in OPEN])
