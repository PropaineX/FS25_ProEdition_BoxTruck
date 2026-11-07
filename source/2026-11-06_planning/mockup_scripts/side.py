import sys, math
from PIL import Image, ImageDraw, ImageFont
G = 0.30                         # truck root above ground
S = 95                           # px per metre
W, H = int(12.2*S), int(5.6*S)
def font(sz, bold=False):
    for f in (('arialbd.ttf' if bold else 'arial.ttf'), 'arial.ttf'):
        try: return ImageFont.truetype(f, sz)
        except: pass
    return ImageFont.load_default()
F1, F2, F3 = font(34, True), font(21), font(17)
def P(z, y):                     # truck z (front +) -> x px (front on the right), height above ground -> y px
    return (int((z + 6.4) * S), int(H - 0.55*S - y*S))
def rect(d, z0, z1, y0, y1, **kw): d.rectangle([P(min(z0,z1), max(y0,y1)), P(max(z0,z1), min(y0,y1))], **kw)
def panel(roof_y, title, sub, after):
    im = Image.new('RGB', (W, H + 230), (245, 243, 236)); d = ImageDraw.Draw(im, 'RGBA')
    ox = 0
    def Q(z, y): x, yy = P(z, y); return (x, yy + 230)
    def R(z0, z1, y0, y1, **kw): d.rectangle([Q(min(z0,z1), max(y0,y1)), Q(max(z0,z1), min(y0,y1))], **kw)
    # ground
    R(-6.4, 5.8, -0.6, 0, fill=(150, 135, 110))
    # shed roof band (where the truck passes) + edge
    for yy, col, lab in ((3.95, (120, 70, 30, 255), 'shed roof underside at its outer edge 3.95 m'),):
        d.line([Q(-6.4, yy), Q(5.8, yy)], fill=col, width=2)
    R(-6.4, 5.8, 3.66, 3.75, fill=(170, 100, 40, 110))
    # chassis
    R(-4.84, 4.3, 0.62 - 0.0, 0.88, fill=(60, 60, 60))
    # wheels
    for z, r in ((3.059, 0.536), (-0.74, 0.538), (-2.11, 0.538), (-3.49, 0.538)):
        c = Q(z, r); d.ellipse([c[0]-r*S, c[1]-r*S, c[0]+r*S, c[1]+r*S], fill=(35, 35, 35)); d.ellipse([c[0]-0.25*S, c[1]-0.25*S, c[0]+0.25*S, c[1]+0.25*S], fill=(170, 170, 170))
    # cab (FH16 Sleeper): body + lower front + windows
    cab_top = 3.738 - G
    d.polygon([Q(1.71, 1.05), Q(4.55, 1.05), Q(4.62, 1.9), Q(4.42, cab_top - 0.05), Q(4.30, cab_top), Q(1.71, cab_top)], fill=(240, 240, 238), outline=(90, 90, 90))
    d.polygon([Q(4.06, 2.25), Q(4.38, 2.25), Q(4.30, 3.05), Q(4.06, 3.05)], fill=(120, 150, 170))
    R(3.17, 4.04, 2.08, 2.92, fill=(120, 150, 170))
    # spoiler (aero sleeper), measured y 3.62-4.13 (root) z 1.97-3.48
    sp = [Q(3.48, 3.62 - G), Q(1.97, 4.133 - G), Q(1.97, 3.62 - G)]
    if after:
        d.polygon(sp, fill=(235, 235, 232, 255), outline=(200, 40, 40))
        for i in range(0, 9):
            t = i / 8; a = (3.48 - 1.51*t, 3.62 - G + 0.513*t)
            d.line([Q(*a), Q(a[0], 3.62 - G)], fill=(200, 40, 40, 140), width=1)
    else:
        d.polygon(sp, fill=(232, 232, 230), outline=(90, 90, 90))
    # box
    top = roof_y - G; floor = 1.75 - G; bows = roof_y - 0.11 - G
    R(-5.35, 1.52, 1.47 - G, top, fill=(250, 250, 248), outline=(80, 80, 80), width=2)
    # curtain cut-away: show load inside
    R(-5.10, 1.40, floor, bows, fill=(70, 72, 78))
    R(-5.35, 1.52, floor - 0.08, floor, fill=(120, 120, 120))
    # pallets: 2 layers x 5 rows (side view), collision 0.975 tall, cans visual to 1.079
    for layer in range(2):
        base = floor + layer * 0.98
        for row in range(5):
            z0 = 1.40 - 0.02 - row * 1.30; z1 = z0 - 1.26
            R(z0, z1, base, base + 0.148, fill=(175, 135, 85), outline=(110, 80, 40))
            for k in range(3):
                cz = z0 - 0.03 - k * 0.41
                R(cz, cz - 0.38, base + 0.148, base + 0.973, fill=(200, 205, 212), outline=(120, 125, 135))
                R(cz - 0.05, cz - 0.33, base + 0.973, base + 1.079, fill=(185, 190, 198), outline=(120, 125, 135))
    # roof bows line + headroom marker
    d.line([Q(-5.10, bows), Q(1.40, bows)], fill=(255, 210, 0), width=3)
    head = (roof_y - 0.11 - 1.75) - 1.96
    hz = -5.6
    d.line([Q(hz, floor), Q(hz, bows)], fill=(0, 0, 0), width=2)
    for yy in (floor, bows): d.line([Q(hz - 0.1, yy), Q(hz + 0.1, yy)], fill=(0, 0, 0), width=2)
    d.text((Q(hz, 0)[0] - 4.6*S/8, Q(0, (floor + bows) / 2)[1] - 40), 'inside\n%.2f m' % (roof_y - 0.11 - 1.75), fill=(0, 0, 0), font=F3)
    # box top marker
    hit = top > 3.66
    d.line([Q(-6.0, top), Q(1.6, top)], fill=(200, 30, 30) if hit else (20, 130, 40), width=2)
    d.text((16, 12), title, fill=(20, 20, 20), font=F1)
    d.text((16, 58), sub, fill=(50, 50, 50), font=F2)
    d.text((16, 92), 'Box top %.2f m   |   Sleeper spoiler 3.83 m%s   |   cab roof 3.44 m' % (top, ' (looks only, no collision)' if after else ''), fill=(0, 0, 0), font=F2)
    d.text((16, 122), 'Shed roof underside (brown): 3.95 m at its edge line, 3.66 - 3.75 m where the truck side passes (band)', fill=(120, 60, 10), font=F3)
    d.text((16, 148), 'Inside height %.2f m, 2 layers of goat milk pallets need 1.96 m -> headroom %.0f cm (Universal Autoload)' % (roof_y - 0.11 - 1.75, head * 100), fill=(0, 0, 0), font=F3)
    if after:
        d.text((16, 174), 'Top-layer can lids stay 1 cm under the roof bows: nothing pokes through (yellow line = roof bows)', fill=(20, 120, 40), font=F3)
    d.text((16, 200), 'Side view to scale, heights above the ground, 5 of the 10 pallets per layer shown', fill=(90, 90, 90), font=F3)
    return im
a = panel(4.23, 'BEFORE: Box Truck now', 'box top 3.93 m and spoiler 3.83 m are above the shed roof underside -> it catches', False)
b = panel(3.93, 'AFTER: box roof lowered 0.30 m', 'box top 3.63 m clears the shed roof by 3-12 cm; spoiler kept, its collision removed', True)
out = Image.new('RGB', (W, (H + 230) * 2 + 20), (255, 255, 255)); out.paste(a, (0, 0)); out.paste(b, (0, H + 250)); out.save(sys.argv[1]); print(out.size)
