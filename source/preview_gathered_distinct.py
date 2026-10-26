"""Build three independent fold layouts under the approved full-height rules."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
base=(ROOT/'source/preview_gathered_v7.py').read_text()
configs=[
    (4,[1.6,.5,1.15,.75],[.35,.17,.28,.23],23,.229),
    (6,[.45,1.5,.6,1.1,.4,1.35],[.16,.31,.22,.35,.18,.27],57,.279),
    (5,[1.4,.45,.55,1.75,.85],[.29,.21,.34,.19,.36],89,.254),
]
for variant,(folds,widths,amps,seed,flare) in enumerate(configs,1):
    folder=f'previews/gathered_distinct_v1/version_{variant}'
    out=ROOT/folder; out.mkdir(parents=True,exist_ok=True)
    # Blender loads the existing PNG copy; no production textures are modified.
    (out/'banner.png').write_bytes((ROOT/'previews/gathered_v7/banner.png').read_bytes())
    code=base.replace("OUT = ROOT/'previews/gathered_v7'",f"OUT = ROOT/'{folder}'")
    code=code.replace("('Left',1,7),('Right',-1,11)",f"('Left',1,{seed}),('Right',-1,{seed+13})")
    code=code.replace('folds=5; cols=folds*48; rows=96',f'folds={folds}; cols=folds*48; rows=96')
    code=code.replace('widths=[.65,1.65,.85,1.45,.5]',f'widths={widths!r}')
    code=code.replace('amps=[.22,.34,.18,.29,.23]',f'amps={amps!r}')
    code=code.replace('.254*(1-t)',f'{flare}*(1-t)')
    # Independent broad meandering changes where folds lean and gather.
    code=code.replace('t*6.5+u*8',f't*{[5.2,7.4,6.1][variant-1]}+u*{[11,6,9.5][variant-1]}')
    code=code.replace('t*11-u*13',f't*{[9,12.5,10][variant-1]}-u*{[10,16,12][variant-1]}')
    exec(compile(code,f'distinct_version_{variant}', 'exec'),{'__file__':str(ROOT/'source/preview_gathered_v7.py'),'__name__':'__main__'})
