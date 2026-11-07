from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json
p=Path(__file__).resolve().parents[2]/'previews/flatbed_plate_milk_v1'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',34)
def make(name,heading,views,footer):
 sheet=Image.new('RGB',(2200,1410),(28,35,44)); d=ImageDraw.Draw(sheet)
 d.text((20,18),heading,font=title,fill='white')
 for i,(path,label) in enumerate(views):
  x=20+(i%2)*1090; y=85+(i//2)*640
  d.text((x,y),label,font=font,fill='white')
  im=Image.open(p/path).convert('RGB').crop((0,0,2032,1045))
  im.thumbnail((1070,590)); sheet.paste(im,(x+(1070-im.width)//2,y+40+(590-im.height)//2))
 d.text((20,1370),footer,font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20),fill=(205,215,225))
 sheet.save(p/name)
make('loaded_and_plate_review_v1.png','FLATBED | rear plate and two-layer milk load',[
 ('01_plate_position.png','Proposed plate: centered on the rear light bar'),
 ('08_clear_spacing_rear34.png','20 pallets: proposed spacing that clears the handles'),
 ('03_milk_side.png','Planned 0.980 m layer pitch: handles overlap pallet bases'),
 ('07_clear_spacing_side.png','Alternative 1.085 m pitch: load height about 3.49 m')],
 'Scratch geometry preview only. Extra spacing is a proposal; UAL, physics, and shed clearance remain untested in game.')
make('stack_spacing_detail_v1.png','MILK STACKING | handle and pallet-base clearance',[
 ('06_stack_close.png','Before: planned 0.980 m tier pitch'),
 ('09_clear_spacing_close.png','Alternative: upper tier raised 105 mm'),
 ('02_milk_rear34.png','Original planned layout'),
 ('08_clear_spacing_rear34.png','Alternative layout: same 20 pallets')],
 'Actual game pallet/can geometry. Comparison changes upper-tier position only; no UAL configuration was changed.')
for f in p.glob('*.png'):
 with Image.open(f) as im: im.verify()
result={'count':20,'layout':[2,5,2],'plate_center_game':[0,.985,-5.405],
 'plate_frame_m':[.53,.13],'original_plate_center_game':[.925,.909,-4.113],
 'measured_load_bounds_root':[-.8847,.8761,1.625,3.6845,-5.1281,1.2848],
 'alternative_layer_pitch':1.085,'alternative_height_root':3.7895,
 'alternative_height_above_ground':3.4895,'calculated_shed_gap_at_lowest_measured_roof':.1705,
 'verified':'actual assets and poses in GIANTS Editor; PNGs verified',
 'gameplay':'UNTESTED','runtime_changes':False}
(p/'validation.json').write_text(json.dumps(result,indent=2))
print('PNG verification passed; plate/load measurements saved')
