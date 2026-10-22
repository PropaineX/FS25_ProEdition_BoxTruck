# Reference measurements: FS25_VolvoFH16Tandem (FH16VAN.xml / FH16VAN.i3d)

Someone else's mod (ALXXA, 1.0.0.3), in `mods\FS25_VolvoFH16Tandem.zip`. Used for measurements only, nothing copied.
Read 2026-10-21 from the zip (i3d node positions worked out to world space, truck origin = 0 0 0, +z = forward,
+x = left). Measured from node origins, so expect a few cm of error; exact mesh sizes need GIANTS Editor.

## Overall
| What | Value |
|---|---|
| Size (xml `<size>`) | 2.65 wide x 9.9 long x 4.0 high, lengthOffset 0.65 |
| Mass | 3,000 kg main + 3,000 kg 2nd component (+ 2 x 200 kg ramps) |
| Centre of mass | 0 0.8 -2.5 |
| Engine | 600 hp spec, max 90 km/h forward, 15 km/h reverse |
| Price | 190,000 |

## Wheels / axles
| What | Value |
|---|---|
| Layout | 6x2 / 6x4: one front steer axle + rear tandem (both rear axles dual tyres) |
| Front axle | z = +3.06 |
| Rear axle 1 / 2 | z = -2.09 / -3.45 (tandem spacing 1.36 m) |
| Wheelbase | 5.15 m (front to 1st rear), 5.83 m (front to tandem centre) |
| Track (node x) | front +-0.88 (1.76 m), rear +-0.77 (1.54 m, inner dual) |
| Tyres | Continental 315/60 R22.5 (HD3) or 315/80 R22.5 (CrossTrac); about 0.95-1.08 m diameter |
| Lift axle | yes, animation `clearance` |

## Load box (curtain sides + net, roof)
| What | Value |
|---|---|
| Front wall | z = +1.90 |
| Rear doors | z = -5.45 |
| Load length | about 7.35 m |
| Inside width | about 2.52 m (side collisions at x = +-1.26) |
| Floor height | about 1.4 m above ground (belt points at y = 1.425) |
| Roof collision | y = 3.30 (about 1.9 m inside height) |
| Top of body | about 4.2 m |
| Cab | node at z = +3.22, y = 1.59; base-game FH16 / FH Electric cab node names |
| Hitch (trailer) | z = -4.68, y = 1.04 |

## Loading
- Tension belts: 10 straps across the box, z = +1.70 to -5.15 (about 0.7-0.8 m apart), triggered by one activation trigger.
- Autoload: the base `baleLoader` (bales only, not pallets), pickupRange 10.
- Rough pallet fit for this box: 7.35 x 2.52 m = 18 EUR pallets (0.8 x 1.2, 3 across) or 12 at 1.2 x 1.2 (2 across).
