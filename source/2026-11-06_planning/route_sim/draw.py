import sys, json, math
from PIL import Image, ImageDraw, ImageFont
D=json.load(open('real.json')); pts=D['pts']; x0s,x1s,y0s,y1s=D['shed']
XMIN,XMAX,YMIN,YMAX=953,993,1078,1132; S=17; PW=int((XMAX-XMIN)*S); PH=int((YMAX-YMIN)*S)
def font(sz):
    for f in ('arialbd.ttf','arial.ttf'):
        try: return ImageFont.truetype(f,sz)
        except: pass
    return ImageFont.load_default()
F1,F2,F3=font(30),font(19),font(16)
def P(x,y): return ((x-XMIN)*S, (YMAX-y)*S)
def panel(name,title,sub,col):
    im=Image.new('RGB',(PW,PH+150),(236,232,220)); d=ImageDraw.Draw(im)
    ox,oy=0,150
    def Q(x,y): a,b=P(x,y); return (a+ox,b+oy)
    d.rectangle([0,oy,PW,PH+oy],fill=(196,205,170))
    # route
    d.line([Q(*p) for p in pts],fill=(40,90,200),width=3)
    for p in pts: 
        a,b=Q(*p); d.ellipse([a-3,b-3,a+3,b+3],fill=(40,90,200))
    # other placeables (footprints)
    for (cx,cz,w,h,lab) in ((959.5,-1109.5,4.5,4.5,'RTK'),(959.27,-1113.0,1.3,1.3,'')):
        d.rectangle([Q(cx-w/2,-cz+h/2),Q(cx+w/2,-cz-h/2)],fill=(150,150,150),outline=(90,90,90))
    a,b=Q(959.5,1109.5); d.text((a-14,b-9),'RTK',fill=(40,40,40),font=F3)
    # barn main building (test area)
    d.rectangle([Q(962.69,1078.45),Q(986.37,1078)],fill=(150,120,100))
    # shed
    d.rectangle([Q(x0s,y1s),Q(x1s,y0s)],fill=(160,110,60),outline=(90,55,20),width=3)
    a,b=Q(x0s+0.4,1096); d.text((a,b),'milk\npallet\nshed',fill=(255,240,220),font=F2)
    v=D['res'][name]['v']; tr=D['res'][name]['tr']; best=D['res'][name]['best']
    W=1.275
    def rect(x,y,h,F,R):
        c,s=math.cos(h),math.sin(h)
        return [Q(x+f*c-l*s, y+f*s+l*c) for f,l in ((F,W),(F,-W),(R,-W),(R,W))]
    k_end=best[3]
    for k in range(0,len(tr),45):
        if k>k_end+40: break
        x,y,h=tr[k][:3]
        d.polygon(rect(x,y,h,v['F'],v['R']),outline=col)
    x,y,h=tr[k_end][:3]
    hit=best[0]<0
    d.polygon(rect(x,y,h,v['F'],v['R']),fill=(255,80,60) if hit else (90,200,90),outline=(120,0,0) if hit else (0,90,0))
    d.polygon(rect(x,y,h,v['F'],v['F']-2.3),fill=(150,20,20) if hit else (30,120,30))   # cab
    bx,by=best[2]; a,b=Q(bx,-by); d.ellipse([a-9,b-9,a+9,b+9],outline=(0,0,0),width=3)
    d.text((14,10),title,fill=(20,20,20),font=F1)
    d.text((14,52),sub,fill=(40,40,40),font=F2)
    lab=('front-left corner reaches %.2f m INTO the shed line'%-best[0]) if hit else ('closest: %.2f m clear of the shed line'%best[0])
    d.text((14,82),lab,fill=(150,0,0) if hit else (0,100,0),font=F2)
    d.text((14,112),'blue = AutoDrive route   outlines = truck every ~1.5 s   dark = cab',fill=(60,60,60),font=F3)
    # north arrow + scale
    a,b=PW-40,oy+20; d.polygon([(a,b),(a-10,b+25),(a+10,b+25)],fill=(0,0,0)); d.text((a-6,b+28),'N',fill=(0,0,0),font=F3)
    d.line([(20,PH+oy-25),(20+5*S,PH+oy-25)],fill=(0,0,0),width=4); d.text((20,PH+oy-50),'5 m',fill=(0,0,0),font=F3)
    return im
a=panel('box now (scrub)','Box Truck (as it is now)','Goat Milk #1 PICKUP, savegame1',(200,90,30))
b=panel('milk','MAN milk truck','same route, same shed',(20,120,140))
out=Image.new('RGB',(PW*2+20,PH+150),(255,255,255)); out.paste(a,(0,0)); out.paste(b,(PW+20,0)); out.save(sys.argv[1])
print(out.size)
