# Reference measurements: FS25_fh16BoxTruck (fh16.xml / fh16.i3d)

Someone else's mod (Onur Emre, 1.0.1.0), in `mods\FS25_fh16BoxTruck.zip`. Used for measurements only, nothing copied.
Read 2026-10-22 from the zip (i3d node positions worked out to world space, truck origin = 0 0 0, +z = forward,
+x = left). Measured from node origins, so expect a few cm of error; exact mesh sizes need GIANTS Editor
(`fh16.i3d.shapes` is encrypted).

Despite the name it is a curtain-sider with rear barn doors (X = rear doors, U = pick curtain side, Z = open that side).

## Overall
| What | Value |
|---|---|
| Size (xml `<size>`) | 2.65 wide x 9.05 long x 4.0 high |
| Mass | 4,264 kg main + 1,000 kg front-axle component |
| Centre of mass | 0 0.8 1.55 |
| Engine | 600 / 700 / 780 hp (manual or CVT), max 90 km/h forward, 15 km/h reverse |
| Price | 137,000 (+25,000 / +50,000 for the bigger engines) |
| Fuel | 755 l diesel, 64 l DEF |

## Wheels / axles (only config: "8x4 Tag")
| What | Value |
|---|---|
| Layout | front steer axle + 2 driven dual-tyre rear axles + steering tag axle at the back |
| Front axle | z = +3.07 (separate component, joint `componentJointAxle`) |
| Rear axle 1 / 2 / 3 (tag) | z = -0.74 / -2.11 / -3.49 (1.37 m and 1.38 m apart) |
| Wheelbase | 3.81 m (front to 1st rear), 4.49 m (front to middle of the driven pair), 6.56 m (front to tag) |
| Track (node x) | front +-1.06, rear +-0.77 (inner dual), tag +-1.06 |
| Tyres | front + tag: Continental HT3 385/65 R22.5; driven: HD3 315/80 R22.5 dual |
| Lift axle | none (no liftableAxle, no clearance animation) |

## Load box
| What | Value |
|---|---|
| Front wall (collision centre) | z = +2.04 |
| Rear doors | z = -4.90, hinges at x = +-1.26 |
| Load length | about 6.9 m |
| Inside width | about 2.48 m (belt ends x = +1.235 / -1.243; side collisions at x = +-1.25) |
| Floor height | about 1.48-1.50 m above ground (floor collision centre y = 1.48, belt points y = 1.52) |
| Roof | roof collision centre y = 4.38, top rails y = 4.23: roughly 2.6 m inside height (rough) |
| Cab | node at z = +3.22, y = 1.59 (base-game FH16 cab names, same spot as the FH16 Tandem) |
| Hitch (trailer) | z = -4.63, y = 0.99 |

## Loading
- Tension belts: 9 straps across the box, z = +1.57 to -4.70 (0.79 m apart), one activation trigger.
- Autoload: none.
- Rough pallet fit for 6.9 x 2.48 m: 15 EUR pallets (0.8 x 1.2) long-way in 5 rows of 3, 16 turned in 8 rows of 2,
  or 17 mixed (5 rows of 3 + 1 row of 2); 10 at 1.2 x 1.2 (2 across).
