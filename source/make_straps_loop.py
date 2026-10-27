"""Assemble captured GIANTS Editor mesh positions into a reversible preview loop."""
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'previews/curtain_straps_motion_v2'
paths=sorted((OUT/'loop_frames').glob('frame_*.png'))
assert len(paths)==31, f'Expected 31 engine captures, found {len(paths)}'
frames=[]
for i,path in enumerate(paths):
    image=Image.open(path).convert('RGB')
    frame=Image.new('RGB',(1020,480),(36,36,36))
    frame.paste(image,(0,40))
    draw=ImageDraw.Draw(frame)
    draw.text((18,12),f'Curtain and straps: {round(i/30*100)}% gathered | GIANTS Editor preview',fill=(240,240,240))
    frames.append(frame)
# A common palette prevents color flicker as the fabric moves.
palette=frames[0].quantize(colors=256)
sequence=frames+frames[-2:0:-1]
indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in sequence]
durations=[40]*len(indexed)
durations[0]=700;durations[30]=700
path=OUT/'curtain_straps_open_close_loop.gif'
indexed[0].save(path,save_all=True,append_images=indexed[1:],duration=durations,loop=0,disposal=2,optimize=False)
with Image.open(path) as gif:
    assert gif.n_frames==60
    assert gif.info['loop']==0
print(f'Created {path.name}: 60 frames, opening and reverse closing, {path.stat().st_size:,} bytes')
