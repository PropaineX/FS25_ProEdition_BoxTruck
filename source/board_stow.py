# Side boards stowed under the body when a curtain opens (user, 2026-10-24; approved GE previews
# previews\board_stow_ge_v1_*.png): instead of vanishing, each board drops out beside the body, rolls flat, shortens and
# swings crossways into 6 close piles (2 high) in the gap between the body's underside and the side guard / fuel tank,
# where only the board ends show. Closing the curtain plays it backwards. Not one-to-one: boards shorten to 0.9 m.
# Measured in GE10 (bt\v18boards): boards 0.025 x 0.14 x 2.16 m (local x, y, z); body underside y 1.47, guard top
# ~1.35 along z 0..1.45. Rotation "90 0 90" = length -> body x, height -> body z (flat); reached as (0 0 90) first, then
# (90 0 90), which keeps the long axis level the whole way (a direct blend tips it 30 degrees through the floor).
# Used by make_vehicle_xml.py (curtain_anim) and apply_board_stow.py (patches the current boxTruck.xml).

HOME_X = 1.2125                      # boards in their slots (boxBody coordinates; right side = -x)
ROW_Y = (2.12, 2.52, 2.92, 3.32)     # board01..04 = rows bottom to top in the front bay, 05..08 middle, 09..12 rear
BAY_Z = (0.4, -1.85, -4.105)
BOARD_LEN = 2.16
T_BOARD = 0.025

LEN_SCALE = 0.42                     # 2.16 m -> 0.9 m
END_X = 1.215                        # stored board ends, just inside the guard's outer face
PILES, Z_FRONT, PITCH = 6, 0.92, 0.16
Y_BASE = 1.36                        # bottom of the piles, just above the guard
DROP_X, DROP_Y = 1.55, 1.40          # beside the body, below its underside, clear of the cab steps

STEP = 0.12                          # one board starts every STEP seconds
T_DOWN, T_ROLL, T_IN = 0.16, 0.08, 0.24


def board_index(row, bay):
    return bay * 4 + row + 1


def order():
    """boards in the order they go in: top row first, front to rear"""
    return [board_index(row, bay) for row in (3, 2, 1, 0) for bay in (0, 1, 2)]


def pile_slot(j):
    """j-th board in -> stored centre (x for the left side, y, z): fills the bottom layer of all piles first"""
    pile, level = j % PILES, j // PILES
    return END_X - BOARD_LEN / 2 * LEN_SCALE, Y_BASE + T_BOARD / 2 + level * (T_BOARD + 0.002), Z_FRONT - pile * PITCH


def fmt(v):
    return ' '.join('%g' % round(c, 4) for c in v)


def stow_parts(side, sgn, t0, indent='            '):
    """<part> lines for one curtain side; the first board starts at t0. Returns (lines, landing times)."""
    lines, landings = [], []
    for j, k in enumerate(order()):
        row, bay = (k - 1) % 4, (k - 1) // 4
        node = 'board%s%02d' % (side, k)
        home = (sgn * HOME_X, ROW_Y[row], BAY_Z[bay])
        drop = (sgn * DROP_X, DROP_Y, BAY_Z[bay])
        x, y, z = pile_slot(j)
        stored = (sgn * x, y, z)
        s = t0 + STEP * j
        a, b, c = s + T_DOWN, s + T_DOWN + T_ROLL, s + T_DOWN + T_ROLL + T_IN
        lines += [
            indent + '<part node="%s" startTime="%.3f" endTime="%.3f" startTrans="%s" endTrans="%s"/>' % (node, s, a, fmt(home), fmt(drop)),
            indent + '<part node="%s" startTime="%.3f" endTime="%.3f" startRot="0 0 0" endRot="0 0 90"/>' % (node, a, b),
            indent + '<part node="%s" startTime="%.3f" endTime="%.3f" startScale="1 1 1" endScale="1 1 %g"/>' % (node, a, b, LEN_SCALE),
            indent + '<part node="%s" startTime="%.3f" endTime="%.3f" startRot="0 0 90" endRot="90 0 90"/>' % (node, b, c),
            indent + '<part node="%s" startTime="%.3f" endTime="%.3f" startTrans="%s" endTrans="%s"/>' % (node, b, c, fmt(drop), fmt(stored)),
        ]
        landings.append(c)
    return lines, landings
