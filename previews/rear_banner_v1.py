"""Mock-up: the waving PRO EDITION banner (same texture as the ProEdition curtain) across both rear doors, centred on
the door seam, high up; shown with the doors shut and pulled apart (the banner splits at the seam).
Usage: python -I previews\\rear_banner_v1.py <out.png>   (run from the mod folder)"""
import sys

from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
BANNER_ASPECT = 6.07 / 1.247          # the curtain decal maps the whole texture onto 6.07 x 1.247 m
WIDTH_SHARE = 0.85                    # banner width / both doors
TOP_SHARE = 0.10                      # gap above the banner / door height

rear = Image.open("previews/rear_profiliner_v1_preview.png").convert("RGB").crop((1114, 50, 1645, 700))
DOOR_X0, DOOR_X1, DOOR_Y0, DOOR_Y1, SEAM = 75, 492, 73, 470, 286

doors_w = DOOR_X1 - DOOR_X0
bw = round(doors_w * WIDTH_SHARE)
bh = round(bw / BANNER_ASPECT)
banner = Image.open("boxTruckProEditionCurtain_diffuse.dds").convert("RGBA").resize((bw, bh), Image.LANCZOS)
bx = SEAM - bw // 2
by = DOOR_Y0 + round((DOOR_Y1 - DOOR_Y0) * TOP_SHARE)

shut = rear.copy()
shut.paste(banner, (bx, by), banner)

# doors pulled apart at the seam: the left door with its half, the right door with its half
gap = 120
apart = Image.new("RGB", (shut.width + gap, shut.height), (166, 166, 166))
left = shut.crop((0, 0, SEAM, shut.height))
right = shut.crop((SEAM, 0, shut.width, shut.height))
apart.paste(left, (0, 0))
apart.paste(right, (SEAM + gap, 0))
d = ImageDraw.Draw(apart)
d.rectangle([SEAM, DOOR_Y0, SEAM + gap, DOOR_Y1], fill=(40, 34, 30))     # the open load space between the doors

font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
small = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
pad, head = 30, 50
sheet = Image.new("RGB", (pad * 3 + shut.width + apart.width, head + shut.height + 80), (38, 38, 38))
s = ImageDraw.Draw(sheet)
sheet.paste(shut, (pad, head))
sheet.paste(apart, (pad * 2 + shut.width, head))
s.text((pad, 12), "Doors shut", font=font, fill=(240, 220, 120))
s.text((pad * 2 + shut.width, 12), "Doors opening: the banner splits at the seam", font=font, fill=(240, 220, 120))
metres = 2.52 * WIDTH_SHARE
s.text((pad, head + shut.height + 20),
       "Banner %.2f m x %.2f m, centred on the seam, %d %% of the door height below the top edge (Pro Edition curtain design only)"
       % (metres, metres / BANNER_ASPECT, round(TOP_SHARE * 100)), font=small, fill=(220, 220, 220))
sheet.save(OUT)
print("saved", OUT, sheet.size, "banner", bw, "x", bh, "px at", bx, by)
