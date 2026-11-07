import sys
from PIL import Image, ImageDraw, ImageFont

G = 0.30            # truck root above ground
S = 92              # px per metre


def font(sz, bold=False):
    for f in (('arialbd.ttf' if bold else 'arial.ttf'), 'arial.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


F1, F2, F3 = font(32, True), font(20), font(17)
# design, truck root coords (height above ground = y - G)
DECK0, DECK1 = 1.50, 1.62            # deck underside / top (tyre tops at 1.40)
DECK_F, DECK_R = 1.50, -5.35         # deck front (behind headboard) / rear
HB_TOP = 3.738                       # headboard level with the Sleeper cab roof
SB_H = 0.60                          # side board height
ST_H = 1.20                          # stake post height
ALU, ALU_D, STEEL, DECK = (205, 208, 212), (150, 154, 160), (45, 45, 48), (95, 80, 62)
PW, PH, TOPM = int(12.4 * S), int(4.9 * S), 120


def pallets(R, base_y, rows_z, front_z):
    for layer in range(2):
        base = base_y + layer * 0.98
        for row in range(rows_z):
            z0 = front_z - 0.12 - row * 1.30
            R(z0, z0 - 1.26, base, base + 0.148, fill=(175, 135, 85), outline=(110, 80, 40))
            for k in range(3):
                cz = z0 - 0.03 - k * 0.41
                R(cz, cz - 0.38, base + 0.148, base + 0.973, fill=(200, 205, 212), outline=(120, 125, 135))
                R(cz - 0.05, cz - 0.33, base + 0.973, base + 1.079, fill=(185, 190, 198), outline=(120, 125, 135))


def side_panel(title, sub, sides, load=False, shed=False):
    im = Image.new('RGB', (PW, PH + TOPM), (245, 243, 236))
    d = ImageDraw.Draw(im, 'RGBA')

    def Q(z, y):
        return (int((z + 6.6) * S), int(TOPM + PH - 0.35 * S - (y - G) * S))

    def R(z0, z1, y0, y1, **kw):
        d.rectangle([Q(min(z0, z1), max(y0, y1)), Q(max(z0, z1), min(y0, y1))], **kw)

    R(-6.6, 5.8, G - 0.4, G, fill=(150, 135, 110))                        # ground
    if shed:
        d.rectangle([Q(-6.6, 3.75 + G), Q(5.8, 3.66 + G)], fill=(170, 100, 40, 120))
        d.text((Q(-6.5, 0)[0], Q(0, 3.75 + G)[1] - 22),
               'goat milk shed roof underside where the truck passes: 3.66 - 3.75 m', fill=(120, 60, 10), font=F3)
    R(-4.84, 4.3, 0.92, 1.18, fill=(60, 60, 60))                           # chassis
    for z, r in ((3.059, 0.536), (-0.74, 0.538), (-2.11, 0.538), (-3.49, 0.538)):
        cx = Q(z, 0)[0]; cy = Q(0, G + r)[1]; rr = r * S
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(35, 35, 35))
        d.ellipse([cx - 0.25 * S, cy - 0.25 * S, cx + 0.25 * S, cy + 0.25 * S], fill=(170, 170, 170))
    # cab (Sleeper) + roof spoiler (Aero Parts "Yes")
    d.polygon([Q(1.71, 1.35), Q(4.55, 1.35), Q(4.62, 2.2), Q(4.42, 3.69), Q(4.30, 3.738), Q(1.71, 3.738)],
              fill=(240, 240, 238), outline=(90, 90, 90))
    d.polygon([Q(4.06, 2.55), Q(4.38, 2.55), Q(4.30, 3.35), Q(4.06, 3.35)], fill=(120, 150, 170))
    R(3.17, 4.04, 2.38, 3.22, fill=(120, 150, 170))
    d.polygon([Q(3.48, 3.62), Q(1.97, 4.133), Q(1.97, 3.62)], fill=(232, 232, 230), outline=(90, 90, 90))
    # subframe + deck
    R(DECK_R + 0.1, DECK_F, 1.18, DECK0, fill=(70, 70, 72))
    R(DECK_R, DECK_F, DECK0, DECK1, fill=DECK, outline=(60, 50, 40))
    R(DECK_R, DECK_F, DECK0, DECK0 + 0.05, fill=ALU_D)
    # headboard
    R(DECK_F - 0.08, DECK_F, DECK1, HB_TOP, fill=ALU, outline=ALU_D)
    # rear light bar + underrun
    R(DECK_R - 0.05, DECK_R + 0.15, 0.62, 0.78, fill=(60, 60, 60))
    R(DECK_R - 0.06, DECK_R + 0.05, 1.20, 1.40, fill=(200, 40, 40))
    if load:
        pallets(R, DECK1, 5, DECK_F)
    L = DECK_F - DECK_R
    if sides == 'boards':
        n, pw = 3, 0.09
        for i in range(n):
            z0 = DECK_F - i * L / n; z1 = z0 - L / n
            R(z0 - pw / 2, z1 + pw / 2, DECK1, DECK1 + SB_H, fill=ALU + (235,), outline=ALU_D)
            for g in range(1, 4):
                yy = DECK1 + g * SB_H / 4
                d.line([Q(z0 - pw / 2, yy), Q(z1 + pw / 2, yy)], fill=ALU_D, width=1)
            R(z0 - 0.35, z0 - 0.25, DECK1 + 0.08, DECK1 + 0.16, fill=STEEL)       # latch
        for i in range(n + 1):
            z = DECK_F - i * L / n
            R(z - pw / 2, z + pw / 2, DECK0, DECK1 + SB_H, fill=ALU_D)
    elif sides == 'stakes':
        n = 6
        for i in range(n):
            z = DECK_F - 0.25 - i * (L - 0.5) / (n - 1)
            R(z - 0.045, z + 0.045, DECK0 - 0.06, DECK1 + ST_H, fill=STEEL)
            R(z - 0.07, z + 0.07, DECK0 - 0.06, DECK0 + 0.04, fill=(80, 80, 85))  # stake pocket
    d.text((16, 12), title, fill=(20, 20, 20), font=F1)
    d.text((16, 54), sub, fill=(50, 50, 50), font=F2)
    d.text((16, 84), 'side view to scale (Volvo FH16 8x4 Tag, Sleeper cab, same chassis as the Box Truck)',
           fill=(90, 90, 90), font=F3)
    return im


def rear_panel():
    im = Image.new('RGB', (PW, PH + TOPM), (245, 243, 236))
    d = ImageDraw.Draw(im, 'RGBA')
    for cx, sides, lab in ((PW * 0.27, 'boards', 'side boards'), (PW * 0.73, 'stakes', 'stake posts')):
        def Q(x, y, cx=cx):
            return (int(cx + x * S), int(TOPM + PH - 0.35 * S - (y - G) * S))

        def R(x0, x1, y0, y1, **kw):
            d.rectangle([Q(min(x0, x1), max(y0, y1)), Q(max(x0, x1), min(y0, y1))], **kw)

        R(-3.0, 3.0, G - 0.4, G, fill=(150, 135, 110))
        d.rectangle([Q(-3.0, 3.75 + G), Q(3.0, 3.66 + G)], fill=(170, 100, 40, 120))
        for x in (-1.0, 1.0):
            cxp, cyp = Q(x, G + 0.538)
            d.rectangle([cxp - 0.28 * S, cyp - 0.538 * S, cxp + 0.28 * S, cyp + 0.538 * S], fill=(35, 35, 35))
        R(-1.2, 1.2, 1.35, 3.738, fill=(240, 240, 238), outline=(90, 90, 90))             # cab behind
        R(-1.275, 1.275, DECK0, DECK1, fill=DECK, outline=(60, 50, 40))
        R(-1.15, 1.15, DECK1, HB_TOP, fill=ALU, outline=ALU_D)                             # headboard
        for k in range(1, 9):
            yy = DECK1 + k * (HB_TOP - DECK1) / 9
            d.line([Q(-1.15, yy), Q(1.15, yy)], fill=ALU_D)
        for layer in range(2):
            base = DECK1 + layer * 0.98
            for px in (-1.20, 0.05):
                R(px, px + 1.15, base, base + 0.148, fill=(175, 135, 85), outline=(110, 80, 40))
                for k in range(3):
                    x0 = px + 0.02 + k * 0.38
                    R(x0, x0 + 0.36, base + 0.148, base + 0.973, fill=(200, 205, 212), outline=(120, 125, 135))
                    R(x0 + 0.05, x0 + 0.31, base + 0.973, base + 1.079, fill=(185, 190, 198), outline=(120, 125, 135))
        if sides == 'boards':
            for s in (-1, 1):
                R(s * 1.235, s * 1.275, DECK1, DECK1 + SB_H, fill=ALU, outline=ALU_D)
        else:
            for s in (-1, 1):
                R(s * 1.23, s * 1.275, DECK0 - 0.06, DECK1 + ST_H, fill=STEEL)
        R(-1.275, 1.275, 0.62, 0.78, fill=(60, 60, 60))
        d.text((Q(-1.5, 0)[0], TOPM + 6), 'rear view, ' + lab, fill=(20, 20, 20), font=F2)
        d.text((Q(-2.9, 0)[0], Q(0, 3.75 + G)[1] - 24), 'shed roof 3.66 m', fill=(120, 60, 10), font=F3)
    d.text((16, 12), 'Loaded: 2 layers of goat milk pallets (20)', fill=(20, 20, 20), font=F1)
    d.text((16, 54), 'deck 1.32 m, top can lids 3.38 m, headboard 3.44 m (level with the cab roof): clears the shed roof by 22-28 cm',
           fill=(50, 50, 50), font=F2)
    d.text((16, 84), 'note: the cab roof spoiler (Aero Parts "Yes", 3.83 m) would still catch that shed; Aero Parts None / Design 1 has no spoiler',
           fill=(150, 0, 0), font=F3)
    return im


panels = [side_panel('Option 1: headboard + side boards', '3 aluminium drop-side boards per side (0.60 m) with hinged posts, empty', 'boards'),
          side_panel('Option 2: headboard + stake posts', '6 steel stake posts per side (1.20 m) in stake pockets, empty', 'stakes'),
          side_panel('Option 1 loaded (Shift+R, Universal Autoload)', '10 milk pallets per layer x 2 layers; shed roof band shown',
                     'boards', load=True, shed=True),
          rear_panel()]
out = Image.new('RGB', (PW, sum(p.height for p in panels) + 20 * (len(panels) - 1)), (255, 255, 255))
y = 0
for p in panels:
    out.paste(p, (0, y)); y += p.height + 20
out.save(sys.argv[1]); print(out.size)
