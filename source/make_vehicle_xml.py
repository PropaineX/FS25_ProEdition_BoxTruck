# Writes the mod's vehicle XML (boxTruck.xml) from the game's own FH16 XML:
#   - our store data, i3d, size, mass
#   - only the "8x4 Tag" wheel option; parts the other wheel options would show are switched off
#   - no fifth wheel (semitrailer attacher joint + its hoses removed)
#   - body animations (rear doors, curtains), tension belts and i3d mappings for our nodes added
# Usage: python -I make_vehicle_xml.py <game fh16.xml> <merged boxTruck.i3d> <out boxTruck.xml>
import sys, re, os
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_stow

src_xml, i3d_path, out_path = sys.argv[1:4]
text = open(src_xml, encoding='utf-8-sig').read()
game_i3d = os.path.join(os.path.dirname(src_xml), 'fh16.i3d')

# chassis options deleted from our i3d in GIANTS Editor (only 8x4 Tag is kept), with their collisions
DELETED = ['chassis4x2', 'chassis6x4', 'chassis8x4_push', 'colPart4x2Part01', 'colPart6x4Part01', 'colPart6x4Part02']

TAGS = ('TransformGroup', 'Shape', 'Light', 'Camera', 'ReferenceNode')

def node_chains(path):
    """{i3dMapping path: name chain} and the reverse for every node. A chain step is (name, n-th sibling of that name)."""
    comps = [c for c in ET.parse(path).getroot().find('Scene') if c.tag in ('TransformGroup', 'Shape')]
    by_path, by_chain = {}, {}
    def walk(node, path_idx, chain, ci):
        seen = {}
        for i, c in enumerate([k for k in node if k.tag in TAGS]):
            nm = c.get('name'); seen[nm] = seen.get(nm, -1) + 1
            p = path_idx + [i]; ch = chain + ((nm, seen[nm]),)
            key = '%d>%s' % (ci, '|'.join(map(str, p)))
            by_path[key] = ch; by_chain[ch] = key
            walk(c, p, ch, ci)
    for ci, comp in enumerate(comps):
        ch = ((comp.get('name'), 0),)
        by_path['%d>' % ci] = ch; by_chain[ch] = '%d>' % ci
        walk(comp, [], ch, ci)
    return by_path, by_chain

base_maps = dict(re.findall(r'<i3dMapping id="([^"]+)" node="([^"]+)"', text))
deleted_paths = [base_maps[d] for d in DELETED]
GONE = {k for k, v in base_maps.items() if any(v == p or v.startswith(p + '|') for p in deleted_paths)}

def section(name, t=None):
    """(start, end) character range of a top-level section '    <name ...> ... </name>' incl. trailing newline."""
    t = text if t is None else t
    m = re.search(r'\n    <%s[ >].*?\n    </%s>\n' % (name, name), t, re.S)
    if not m:
        raise SystemExit('section not found: ' + name)
    return m.start() + 1, m.end()

def replace_section(name, new):
    global text
    a, b = section(name)
    text = text[:a] + new + text[b:]

# ---------------------------------------------------------------- store data
replace_section('storeData', '''    <storeData>
        <name>FH16 Box Truck</name>
        <specs>
            <power>600</power>
            <maxSpeed>90</maxSpeed>
        </specs>
        <functions>
            <function>$l10n_function_truck</function>
        </functions>
        <image>store_boxTruck.dds</image>
        <price>175000</price>
        <lifetime>600</lifetime>
        <rotation>0</rotation>
        <brand>VOLVO</brand>
        <category>trucks</category>
        <shopTranslationOffset>0 -0.306 0</shopTranslationOffset>
        <shopRotationOffset>0.005 0 0</shopRotationOffset>
    </storeData>
''')

# ---------------------------------------------------------------- base
text = text.replace('<vehicle type="tractor"', '<vehicle type="boxTruckPro"', 1)
text = text.replace('<filename>$data/vehicles/volvo/fh16/fh16.i3d</filename>', '<filename>boxTruck.i3d</filename>', 1)
# FH16 front bumper z 4.53, rear doors z -5.35, top of body 4.23 (body: floor lifted 0.25, moved back 0.37)
text = text.replace('<size width="2.65" length="9.05" height="4"/>',
                    '<size width="2.65" length="9.88" lengthOffset="-0.41" height="4.25"/>', 1)

# ---------------------------------------------------------------- wheels: only 8x4 Tag
a, b = section('wheels')
wheels = text[a:b]
root = ET.fromstring(wheels)
configs = root.find('wheelConfigurations').findall('wheelConfiguration')
tag = next(c for c in configs if c.get('saveId') == 'CONTINENTAL_8X4_TAG')
tag_nodes = {oc.get('node') for oc in tag.findall('objectChange')}
neutral = {}
for c in configs:
    if c is tag:
        continue
    for oc in c.findall('objectChange'):
        node = oc.get('node')
        if node in tag_nodes or node in GONE:
            continue
        for attr, val in oc.attrib.items():
            if attr.endswith('Inactive'):
                neutral.setdefault(node, {})[attr[:-len('Inactive')] + 'Active'] = val
m = re.search(r'\n( *)<!-- 8x4 Tag -->\n.*?</wheelConfiguration>\n', wheels, re.S)
tag_text = m.group(0)
tag_text = tag_text.replace('price="50000" ', '')
tag_text = tag_text.replace('massActive="3545" centerOfMassActive="0 0.8 1.55"',
                            'massActive="5250" centerOfMassActive="0 1.0 0.6"')
tag_text = tag_text.replace('<foliageBendingModifier index="1" minZ="-4.55"/>',
                            '<foliageBendingModifier index="1" minZ="-5.0"/>')
extra = '\n                <!-- parts of the other wheel options (this truck only comes as 8x4 Tag) -->\n'
for node in sorted(neutral):
    attrs = ' '.join('%s="%s"' % kv for kv in sorted(neutral[node].items()))
    extra += '                <objectChange node="%s" %s/>\n' % (node, attrs)
tag_text = tag_text.replace('            </wheelConfiguration>\n', extra + '            </wheelConfiguration>\n')
head = wheels[:wheels.index('<wheelConfigurations>') + len('<wheelConfigurations>')]
tail = wheels[wheels.index('        </wheelConfigurations>'):]
text = text[:a] + head + tag_text + tail + text[b:]

# ---------------------------------------------------------------- no fifth wheel
for name in ('attacherJoints', 'connectionHoses'):
    a, b = section(name)
    text = text[:a] + text[b:].lstrip('\n')
text = re.sub(r'\n *<group name="BACK_ATTACHMENT" attacherJointIndices="1"/>', '', text)
# trailer turn-signal indicators on the dashboard only work with that group
text = re.sub(r'\n *<dashboard [^\n]*groups="[^"]*BACK_ATTACHMENT[^"]*"/>', '', text)

# ---------------------------------------------------------------- engines: four FH16 options with a hauling theme
# (user's choice: 425, 515, 585, 600 hp; the game's 700, 780 and the hidden FH Electric options are removed).
# All use the game's 600 setup (D17K600 torque curve, ATO3112F gearbox, sound); torque scales with power.
ENGINES = [  # name, hp, price add-on, diesel l/h, DEF l/h, cab badge node shown
    ('FH425 City Hauler',     425,     0, 170, 14.2, 'engine425_decals'),   # default (first option)
    ('FH515 Regional Hauler', 515, 15000, 206, 17.2, 'engine515_decals'),
    ('FH585 Long Hauler',     585, 20000, 234, 19.5, 'engine585_decals'),
    ('FH600 Heavy Hauler',    600, 25000, 240, 20.0, 'engine600_decals'),
]
BADGES = ['engine425_decals', 'engine515_decals', 'engine585_decals',
          'engine600_decals', 'engine700_decals', 'engine780_decals', 'fh16_780_decals']
a, b = section('motorized')
motorized = text[a:b]
mc = re.search(r'\n( *)<motorConfigurations>\n(.*?)\n *</motorConfigurations>', motorized, re.S)
configs_xml = ET.fromstring('<r>' + mc.group(2) + '</r>')
removed = configs_xml.findall('motorConfiguration')
first = re.search(r'<motorConfiguration name="FH16 600".*?</motorConfiguration>', mc.group(2), re.S).group(0)
motor_el = re.search(r'( *)<motor torqueScale="([0-9.]+)"(.*?)</motor>', first, re.S)
base_torque, base_hp = float(motor_el.group(2)), 600
transmission = re.search(r' *<!-- ATO3112F -->\n *<transmission.*?</transmission>', first, re.S).group(0)
sounds = re.search(r' *<sounds>.*?</sounds>', first, re.S).group(0)
# parts the removed options switched (FH16 vs FH Electric cab): keep the FH16 state in every option
keep = {}
for c in removed:
    if c.get('name', '').startswith('FH Electric'):
        for oc in c.findall('objectChange'):
            for attr, val in oc.attrib.items():
                if attr.endswith('Inactive') and oc.get('node') not in BADGES:
                    keep.setdefault(oc.get('node'), {})[attr[:-len('Inactive')] + 'Active'] = val
new_mc = '\n%s<motorConfigurations>\n' % mc.group(1)
for i, (name, hp, price, diesel, defl, badge) in enumerate(ENGINES):
    torque = round(base_torque * hp / base_hp, 3)
    motor = motor_el.group(0).replace('torqueScale="%s"' % motor_el.group(2), 'torqueScale="%s"' % torque, 1)
    new_mc += '            <!-- %d hp: D17K600 curve, torque x %.3f -->\n' % (hp, hp / base_hp)
    new_mc += '            <motorConfiguration name="%s" hp="%d" price="%d" consumerConfigurationIndex="%d">\n' % (name, hp, price, i + 1)
    new_mc += motor.replace('\n                ', '\n                ') + '\n\n'
    new_mc += transmission + '\n\n'
    new_mc += '                <objectChange node="fh16_globetrotter_decals" visibilityActive="true"/>\n'
    for node in BADGES:
        new_mc += '                <objectChange node="%s" visibilityActive="%s"/>\n' % (node, 'true' if node == badge else 'false')
    for node in sorted(keep):
        attrs = ' '.join('%s="%s"' % kv for kv in sorted(keep[node].items()))
        new_mc += '                <objectChange node="%s" %s/>\n' % (node, attrs)
    new_mc += '\n' + sounds + '\n            </motorConfiguration>\n\n'
new_mc += '%s</motorConfigurations>' % mc.group(1)
motorized = motorized[:mc.start()] + new_mc + motorized[mc.end():]
cc = re.search(r'\n( *)<consumerConfigurations>.*?</consumerConfigurations>', motorized, re.S)
new_cc = '\n%s<consumerConfigurations>\n' % cc.group(1)
for name, hp, price, diesel, defl, badge in ENGINES:
    new_cc += ('            <consumerConfiguration> <!-- %s -->\n'
               '                <consumer fillUnitIndex="1" usage="%g"  fillType="diesel"/> <!-- usage is per hour at max load and max rpm -->\n'
               '                <consumer fillUnitIndex="2" usage="%g" fillType="def"/>\n'
               '                <consumer fillUnitIndex="3" usage="300"  fillType="air" permanentConsumption="false" refillLitersPerSecond="350" refillCapacityPercentage="0.5"/> <!-- usage per second at full brake power -->\n'
               '            </consumerConfiguration>\n') % (name, diesel, defl)
new_cc += '%s</consumerConfigurations>' % cc.group(1)
motorized = motorized[:cc.start()] + new_cc + motorized[cc.end():]
text = text[:a] + motorized + text[b:]

# ---------------------------------------------------------------- paint: a plain (non-metallic) white matching the box
# the default colours use calibratedMetallicPaint, so their white looks silver next to the box (material 0.90 0.90 0.88)
text = text.replace('        <baseColorConfiguration color="VOLVO_GREY1"/>\n',
                    '        <baseColorConfiguration color="VOLVO_GREY1"/>\n'
                    '        <baseColorConfiguration color="0.90 0.90 0.88" materialTemplateName="calibratedPaint" name="$l10n_configuration_colorBoxWhite"/>\n', 1)

# ---------------------------------------------------------------- roof: Sleeper is the default (user, 2026-10-22)
# designConfiguration 1 = Globetrotter XL (+5000), 2 = Sleeper (0). The box top stays at 4.23 (Globetrotter level).
a = text.index('<designConfiguration name="2" price="0">')
text = text[:a] + '<designConfiguration name="2" price="0" isDefault="true">' + text[a + len('<designConfiguration name="2" price="0">'):]

# curtain design (shop option, design8 is free on the FH16): plain white (default), our waving PRO EDITION banner, or
# the Krone ProfiLiner's three ad designs (decals with the game's own ad sheets). All decals are hidden in the i3d.
DESIGN_OPTIONS = [('ProEdition', 'ProEdition'), ('Krone', 'DesignKrone'), ('$l10n_configuration_boxCurtainFSL', 'DesignFSL'),
                  ('GIANTS', 'DesignGIANTS')]
a = text.index('    </design7Configurations>\n') + len('    </design7Configurations>\n')
d8 = ('\n    <design8Configurations title="$l10n_configuration_boxCurtainDesign">\n'
      '        <design8Configuration name="$l10n_configuration_boxCurtainPlain" price="0" isDefault="true"/>\n')
for title, suffix in DESIGN_OPTIONS:
    d8 += '        <design8Configuration name="%s" price="0">\n' % title
    for side in ('Left', 'Right'):
        d8 += '            <objectChange node="curtain%s%s" visibilityActive="true" visibilityInactive="false"/>\n' % (side, suffix)
    d8 += '        </design8Configuration>\n'
d8 += '    </design8Configurations>\n'
text = text[:a] + d8 + text[a:]

# ---------------------------------------------------------------- body animations
# v8 (user 2026-10-22): the curtain SLIDES to the rear first (CURTAIN_SLIDE s, the closed curtain is scaled towards its
# rear end, where its group's origin is), then it swaps for the curtain gathered at the rear; after that it works like
# the Krone ProfiLiner's coverAnimation: the side boards fold away one by one, then the posts tilt a little and slide to
# the rear, the rear-middle post first, the front post last, with the ProfiLiner's sounds. Node positions from the i3d.
# Closing plays the same backwards (the curtain stretches out from the rear to the front last).
def node_trans(name):
    for n in ET.parse(i3d_path).getroot().iter():
        if n.get('name') == name:
            return [float(v) for v in n.get('translation', '0 0 0').split()]
    raise SystemExit('node %s not in %s' % (name, i3d_path))
# the side collision walls lift straight up above the roof while a curtain is open. v1 folded them inward under the
# roof: closing swung them down through the load and knocked the pallets about (in-game test 2026-10-22).
SIDE_COL_LIFT = 2.5
CURTAIN_REAR_Z = -5.21                  # build_body.py CURTAIN_REAR_Z: the posts park just in front of it
CURTAIN_FRONT_Z = 1.51                  # build_body.py CURTAIN_FRONT_Z (FRONT_Z - 0.12)
GATHER_LEN = 0.50                       # build_body.py GATHER_LEN: length of the gathered curtain
CURTAIN_SLIDE = 1.2                     # user: 1 to 1.5 s
POST_PARK = {1: CURTAIN_REAR_Z + 0.30, 2: CURTAIN_REAR_Z + 0.16}
BOARDS = 12                             # per side, build_body.py (3 bays x 4)
DOOR_OPEN_DEG = 100                     # user 2026-10-22: doors stand out behind the truck, not folded to the sides
fmt = lambda v: ' '.join('%g' % round(x, 4) for x in v)
def curtain_anim(side, sgn):
    cs = node_trans('colSide%sPivot' % side)
    T = CURTAIN_SLIDE
    gathered = GATHER_LEN / (CURTAIN_FRONT_Z - CURTAIN_REAR_Z)
    out = '        <animation name="boxCurtain%s">\n' % side
    out += '            <part node="curtain%sClosed" startTime="0.0" endTime="%g" startScale="1 1 1" endScale="1 1 %g"/>\n' % (
        side, T, round(gathered, 4))
    out += '            <part node="curtain%sClosed" startTime="%g" endTime="%g" startVisibility="true" endVisibility="false"/>\n' % (side, T - 0.05, T)
    out += '            <part node="curtain%sOpen"   startTime="%g" endTime="%g" startVisibility="false" endVisibility="true"/>\n' % (side, T - 0.05, T)
    out += '            <part node="colSide%sPivot" startTime="0.0" endTime="0.1" startTrans="%s" endTrans="%s"/>\n' % (
        side, fmt(cs), fmt([cs[0], cs[1] + SIDE_COL_LIFT, cs[2]]))
    # side boards: stowed in piles under the body instead of vanishing (board_stow.py, user 2026-10-24)
    stow_lines, landings = board_stow.stow_parts(side, sgn, T)
    out += ''.join(line + '\n' for line in stow_lines)
    tilt = '0 0 %g' % (0.65 * sgn)
    for k, (t_tilt, t_slide, t_end) in ((2, (1.0, 1.333, 2.333)), (1, (2.333, 2.667, 4.0))):
        p = node_trans('post%s%d' % (side, k))
        out += '            <part node="post%s%d" startTime="%g" endTime="%g" startRot="0 0 0" endRot="%s"/>\n' % (
            side, k, t_tilt + T, t_slide + T, tilt)
        out += '            <part node="post%s%d" startTime="%g" endTime="%g" startTrans="%s" endTrans="%s"/>\n' % (
            side, k, t_slide + T, t_end + T, fmt(p), fmt([p[0], p[1], POST_PARK[k]]))
    out += '            <sound template="fabricCover1"    startTime="0.01" direction="0"  volumeScale="5" pitchScale="1"/>\n'
    for t in landings:
        out += '            <sound template="palletsFillWood" startTime="%.3f" volumeScale="3" pitchScale="1"/>\n' % (t - 0.02)
    out += '            <sound template="slideOpen"       startTime="%g"  direction="1"  volumeScale="5" pitchScale="1"/>\n' % (1.2 + T)
    out += '            <sound template="slideOpen"       startTime="%g"  direction="0"  volumeScale="5" pitchScale="0.7"/>\n' % (2.6 + T)
    out += '            <sound template="slideOpen"       startTime="%g" direction="-1" volumeScale="6" pitchScale="0.6"/>\n' % (3.99 + T)
    out += '        </animation>\n'
    return out
anims = ('\n        <!-- Box Truck body (played by scripts/BoxTruckBody.lua) -->\n'
         '        <animation name="boxRearDoors">\n'
         '            <part node="rearDoorLeft"  startTime="0" endTime="2" startRot="0 0 0" endRot="0 -%d 0"/>\n'
         '            <part node="rearDoorRight" startTime="0" endTime="2" startRot="0 0 0" endRot="0 %d 0"/>\n'
         '        </animation>\n' % (DOOR_OPEN_DEG, DOOR_OPEN_DEG)) + curtain_anim('Left', 1) + curtain_anim('Right', -1)
a, b = section('animations')
block = text[a:b]
block = block.replace('    </animations>\n', anims + '    </animations>\n')
belts = '''
    <tensionBelts>
        <tensionBeltsConfigurations>
            <tensionBeltsConfiguration>
                <tensionBelts linkNode="tensionBelts" jointNode="fh16_main_component1" maxEdgeLength="0.1" geometryBias="0.01" ratchetPosition="0.2" defaultOffset="0.1" defaultOffsetSide="0.1" defaultHeight="2.2" activationTrigger="beltActivationTrigger">
'''
for n in range(1, 10):
    belts += '                    <tensionBelt startNode="beltStart%02d" endNode="beltStart%02dEnd"/>\n' % (n, n)
belts += '''                </tensionBelts>
            </tensionBeltsConfiguration>
        </tensionBeltsConfigurations>
    </tensionBelts>
'''
text = text[:a] + block + belts + text[b:]

# ---------------------------------------------------------------- deleted chassis options
# everything that points at a node inside a deleted part goes: whole elements with children, then one-line elements
removed = 0
for gid in sorted(GONE):
    ref = r'node="%s"' % re.escape(gid)
    text, n1 = re.subn(r'\n *<(\w+) [^\n>]*%s[^\n>]*[^/]>.*?</\1>' % ref, '', text, flags=re.S)
    text, n2 = re.subn(r'\n *<(\w+) [^\n]*(?:node|referencePoint|referenceFrame)="%s"[^\n]*/>' % re.escape(gid), '', text)
    text, n3 = re.subn(r'\n *<i3dMapping id="%s" node="[^"]+" */>' % re.escape(gid), '', text)
    removed += n1 + n2
left = [g for g in GONE if re.search(r'"%s"' % re.escape(g), text)]
if left:
    raise SystemExit('still referenced after removing deleted parts: %s' % left)

# the remaining FH16 mappings: same node (by name chain in the game's fh16.i3d), new position in our i3d
old_chain, _ = node_chains(game_i3d)
_, new_path = node_chains(i3d_path)
def remap(m):
    ch = old_chain[m.group(2)]
    if ch not in new_path:
        raise SystemExit('mapping %s (%s) not found in %s' % (m.group(1), m.group(2), i3d_path))
    return '<i3dMapping id="%s" node="%s"' % (m.group(1), new_path[ch])
text = re.sub(r'<i3dMapping id="([^"]+)" node="([^"]+)"', remap, text)

# ---------------------------------------------------------------- i3d mappings for our nodes
i3d = ET.parse(i3d_path).getroot()
comps = [c for c in i3d.find('Scene') if c.tag in ('TransformGroup', 'Shape')]
want = {'boxBody', 'curtainLeft', 'curtainRight', 'rearDoorLeft',
        'rearDoorRight', 'colSideLeftPivot', 'colSideRightPivot', 'tensionBelts', 'beltActivationTrigger'}
want |= {'beltStart%02d' % n for n in range(1, 10)} | {'beltStart%02dEnd' % n for n in range(1, 10)}
want |= {'engine425_decals', 'engine515_decals', 'engine585_decals'}   # our cab badges (build_badges.py)
want |= {'curtainLeftProEdition', 'curtainRightProEdition'}   # ProEdition curtain design
want |= {'curtain%s%s' % (sd, part) for sd in ('Left', 'Right') for part in ('Closed', 'Open', 'DesignKrone', 'DesignFSL', 'DesignGIANTS')}
want |= {'post%s%d' % (sd, k) for sd in ('Left', 'Right') for k in (1, 2)}
want |= {'board%s%02d' % (sd, k) for sd in ('Left', 'Right') for k in range(1, 13)}
found = {}
def walk(node, comp_index, path):
    kids = [c for c in node if c.tag in ('TransformGroup', 'Shape', 'Light', 'Camera')]
    for i, c in enumerate(kids):
        p = path + [i]
        if c.get('name') in want and c.get('name') not in found:
            found[c.get('name')] = '%d>%s' % (comp_index, '|'.join(map(str, p)))
        walk(c, comp_index, p)
for ci, comp in enumerate(comps):
    walk(comp, ci, [])
missing = want - set(found)
if missing:
    raise SystemExit('nodes missing in i3d: %s' % sorted(missing))
existing = set(re.findall(r'<i3dMapping id="([^"]+)"', text))
clash = existing & set(found)
if clash:
    raise SystemExit('i3dMapping ids already used by the FH16: %s' % sorted(clash))
maps = '\n        <!-- Box Truck body -->\n'
order = sorted(found, key=lambda k: [int(x) for x in re.split(r'[>|]', found[k]) if x != ''])
for k in order:
    maps += '        <i3dMapping id="%s" node="%s" />\n' % (k, found[k])
text = text.replace('    </i3dMappings>', maps + '    </i3dMappings>', 1)

open(out_path, 'w', encoding='utf-8').write(text)
print('written', out_path, '| neutralised wheel-option nodes:', len(neutral), '| body mappings:', len(found),
      '| deleted-part mappings dropped:', len(GONE), '| elements removed:', removed)
