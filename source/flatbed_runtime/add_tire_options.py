"""Add the off-road single-tire shop options to flatbedTruck.xml (flatbed only, not the Box Truck).

Run after build_vehicle.py:  python -I source/flatbed_runtime/add_tire_options.py
Re-running replaces earlier generated options. Each option clones the stock 8x4 Tag configuration:
front and tag axle get the new tire; both drive axles drop the dual pair for one wide single,
moved outward (physics#xOffset) so it sits centred where the pair was.
Approved by the user 2026-11-06 from previews/tires_offroad_v1/.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
XML = ROOT / 'flatbedTruck.xml'
T = '$data/shared/wheels/tires/'
HT3 = T + 'continental/contiHybridHT3/385_65R22_5.xml'
HD3 = T + 'continental/contiHybridHD3/315_80R22_5.xml'
DUAL_X = '-0.03'      # stock dual xOffset
SINGLE_X = '0.1525'   # -0.03 + half the dual pair spread (0.365 / 2)
HUB = '<innerRim filename="$data/shared/wheels/hubs/hubTrucks.i3d" nodeLeft="6|0" nodeRight="6|1" widthAndDiam="20 21" offset="0.07" />'

# (shop name, brand, tire xml, price). 560/60 Vredesteins removed 2026-11-06 (user: too big). Prices by size, in line with base-game truck wheel options.
OPTIONS = [
    ('OffRoad HCS 445/65 R22.5', 'CONTINENTAL', 'continental/offRoadHCS/445_65R22_5.xml', 4000),
    ('AC 70G 445/65 R22.5', 'MITAS', 'mitas/AC70G/445_65R22_5.xml', 4000),
    ('AR-01 445/65 R22.5', 'MITAS', 'mitas/AR01/445_65R22_5.xml', 4000),
    ('Twin Radial 500/60 R22.5', 'TRELLEBORG', 'trelleborg/TwinRadial/500_60R22_5.xml', 6000),
    ('T404 500/60 R22.5', 'TRELLEBORG', 'trelleborg/T404/500_60R22_5.xml', 6000),
    ('T421 500/60 R22.5', 'TRELLEBORG', 'trelleborg/T421/500_60R22_5.xml', 6000),
    ('Ridemax FL 693 M 500/60 R22.5', 'BKT', 'bkt/ridemaxFL693M/500_60R22_5.xml', 6000),
    ('CargoXBib 500/60 R22.5', 'MICHELIN', 'michelin/cargoXBib/500_60R22_5.xml', 6000),
    ('CargoXBib HD 500/60 R22.5', 'MICHELIN', 'michelin/cargoXBibHD/500_60R22_5.xml', 6000),
    ('Flotation 328 500/60 R22.5', 'ALLIANCE', 'alliance/flotation328/500_60R22_5.xml', 6000),
]
MARK = '<!-- PROPAINEX_TIRE_OPTIONS -->'

raw = XML.read_bytes().decode('utf-8')
nl = '\r\n' if '\r\n' in raw else '\n'
text = raw.replace('\r\n', '\n')
# drop options from an earlier run
text = re.sub(r'\n *' + re.escape(MARK) + r'.*?' + re.escape(MARK.replace('<!-- ', '<!-- END ')) + r'\n', '\n', text, flags=re.S)

m = re.search(r'( *)<wheelConfiguration name="8×4 Tag" brand="CONTINENTAL" saveId="CONTINENTAL_8X4_TAG">.*?</wheelConfiguration>\n', text, re.S)
assert m, 'stock 8x4 Tag configuration not found'
stock, indent = m.group(0), m.group(1)
assert stock.count(HT3) == 4 and stock.count(HD3) == 8 and stock.count('configId="dual"') == 4

def make(name, brand, tire, price):
    block = stock.replace(HT3, T + tire)
    # duals -> one wide single, centred on the old pair
    block = re.sub(r'<wheel filename="' + re.escape(HD3) + r'" configId="dual" ', '<wheel filename="' + T + tire + '" ', block)
    block = re.sub(r'xOffset="' + re.escape(DUAL_X) + '"', 'xOffset="' + SINGLE_X + '"', block)
    block = re.sub(r'<additionalWheel [^>]*configId="dualConnector"[^>]*/>', HUB, block)
    save = (brand + '_' + re.sub(r'[^A-Z0-9]+', '_', name.upper())).strip('_')
    block = block.replace('<wheelConfiguration name="8×4 Tag" brand="CONTINENTAL" saveId="CONTINENTAL_8X4_TAG">',
                          f'<wheelConfiguration name="{name}" brand="{brand}" price="{price}" saveId="{save}">', 1)
    assert HD3 not in block and HT3 not in block and 'dual' not in block
    return block

added = indent + MARK + '\n' + ''.join(make(*o) for o in OPTIONS) + indent + MARK.replace('<!-- ', '<!-- END ') + '\n'
text = text[:m.end()] + added + text[m.end():]
XML.write_bytes(text.replace('\n', nl).encode('utf-8'))

root = ET.parse(XML).getroot()
configs = root.findall('wheels/wheelConfigurations/wheelConfiguration')
assert len(configs) == 1 + len(OPTIONS), len(configs)
assert len({c.get('saveId') for c in configs}) == len(configs)
gamedata = Path('G:/SteamLibrary/steamapps/common/Farming Simulator 25/data')
for c in configs:
    for w in c.iter('wheel'):
        assert (gamedata / w.get('filename').replace('$data/', '')).is_file(), w.get('filename')
print(f'{len(OPTIONS)} tire options written; {len(configs)} wheel configurations in total')
for c in configs:
    print(' ', c.get('brand'), '|', c.get('name'), '|', c.get('price', '0'), '|', c.get('saveId'))
