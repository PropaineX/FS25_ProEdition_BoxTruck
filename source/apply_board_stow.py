# Patches boxTruck.xml: in boxCurtainLeft / boxCurtainRight the boards' hide-one-by-one parts (startVisibility="true"
# endVisibility="false") are replaced by the stowing motion of board_stow.py, and the board knocks are moved to when
# each board lands. Run once from the mod folder: python -I source\apply_board_stow.py boxTruck.xml
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_stow

path = sys.argv[1]
text = open(path, encoding='utf-8').read()

for side, sgn in (('Left', 1), ('Right', -1)):
    m = re.search(r'(<animation name="boxCurtain%s">)(.*?)(\n\s*</animation>)' % side, text, re.S)
    body = m.group(2)
    hides = re.findall(r'\n(\s*)<part node="board%s\d\d" startTime="([\d.]+)"[^>]*startVisibility="true" endVisibility="false"/>' % side, body)
    if len(hides) != 12:
        sys.exit('%s: expected 12 board hide parts, found %d (already patched?)' % (side, len(hides)))
    indent, t0 = hides[0][0], float(hides[0][1])
    lines, landings = board_stow.stow_parts(side, sgn, t0, indent)
    # the boards' parts go where the hide parts were
    body = re.sub(r'\n\s*<part node="board%s\d\d" [^>]*startVisibility="true" endVisibility="false"/>' % side, '', body)
    anchor = re.search(r'\n\s*<part node="colSide%sPivot"[^>]*/>' % side, body)
    body = body[:anchor.end()] + '\n' + '\n'.join(lines) + body[anchor.end():]
    # knocks: one per board as it lands (instead of the 7 timed for the old hiding)
    body = re.sub(r'\n\s*<sound template="palletsFillWood"[^>]*/>', '', body)
    first_sound = re.search(r'\n\s*<sound ', body)
    knocks = ''.join('\n%s<sound template="palletsFillWood" startTime="%.3f" volumeScale="3" pitchScale="1"/>' % (indent, t - 0.02)
                     for t in landings)
    body = body[:first_sound.end() - len('<sound ') - len(indent) - 1] + knocks + body[first_sound.end() - len('<sound ') - len(indent) - 1:]
    text = text[:m.start(2)] + body + text[m.end(2):]
    print('%s: 12 boards, %.3f..%.3f s' % (side, t0, max(landings)))

open(path, 'w', encoding='utf-8').write(text)
