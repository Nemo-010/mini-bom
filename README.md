# Mini — BOM, weight budget and endurance

Sourcing sheet for the KiCad BOM in
[the gist](https://gist.github.com/sounddrill31/6b8cd79947475711873521c7521a1664)
(`john-minidrone.csv`), plus the motors, props, flight controller, battery and
PCB the brief asked about.

Sourcing order was **Robu.in → Evelta → Robocraze → Sharvi → Mouser/Element14**.
Everything was checked on **2026-10-23** by reading the live product page (the
`Availability:` field and the qty-1 price), not a search-results badge.

- [`bom-mini.csv`](bom-mini.csv) — one chosen part per line, `Included`
  (`Yes`/`Optional`) next to the reference
- [`weight-budget.csv`](weight-budget.csv) — per-part mass, AUW against the
  40 g ceiling, and the endurance optimisation
- [`not-found-exact.csv`](not-found-exact.csv) — what is not an exact match

## Headline numbers

| | |
|---|---|
| Airframe, no battery | **23.50 g** |
| AUW with the 10 g pack | **33.50 g** |
| Budget | 40 g → **6.5 g spare** |
| Endurance, 65 mm props | **~15.7 min** (best case, k=4.5) |
| Endurance, 31 mm props | ~5.2 min |

So 15 minutes **is** reachable on a 10 g pack — but only with 65 mm props, and
with about 1.5 g of margin. The details are below.

## Sharvi: checked, still no 1020

Sharvi stocks two coreless motors, both bundled with a 65 mm propeller:

| Sharvi part | SKU | Price | Stock |
|---|---|---|---|
| Coreless Motor 7X20mm With Propeller | `ST2001RO0137` | ₹135.63 | **In stock** |
| Coreless Motor 8X20mm With Propeller | `ST2001RO0134` | ₹98.00 | Out of stock |

Their propeller category has no standalone micro prop — the 65 mm only comes
bundled with the motor. **No 1020 exists at Robu, Evelta, Robocraze or Sharvi.**
The 7×20 at ₹135.63 each (motor + prop per unit, qty 4) is the cheapest
in-stock option found, so that is what the budget uses. Rated 3.7 V, 60 mA,
48000 rpm, 7 × 20 mm can, 1 mm shaft, 100 mm wires.

Sharvi's site is behind Cloudflare and blocks direct fetching; the figures above
came from their own structured product data (SKU, price, availability fields) via
an archived copy.

## The prop size is the whole story

This is the most important finding. Endurance is dominated by prop diameter, and
**a 32.5 × 30 mm board physically cannot clear a useful prop without arms**:

| Prop | Fits the bare board? | Ideal induced power | k | Hover power | Endurance |
|---|---|---|---|---|---|
| 31 mm | yes (1 mm overlap) | 2.19 W | 6.5 | 14.24 W | **5.2 min** |
| 55 mm | no, needs arms | 1.23 W | 5.0 | 6.17 W | **12.0 min** |
| 65 mm | no, needs arms | 1.04 W | 4.5 | 4.70 W | **15.7 min** |

Motors sit 30 mm apart on the short axis and 32.5 mm on the long axis, so
anything above 30 mm needs arms. Going from 31 mm to 65 mm props is a **3×
endurance gain** — far more than any electronics or cell choice can buy.

The `k` factor is the figure of merit (how far the real machine is from
momentum-theory ideal). It is calibrated on the Eachine E010 class — 22 g AUW,
31 mm props, ~3.5 min on a 150 mAh 1S — which gives k ≈ 6.5 for tiny props. k
improves as props get bigger, hence 5.0 and 4.5 above. These are estimates, not
measured thrust-stand data; treat the endurance figures as ±25%.

## Maximising endurance on the 10 g pack

In order of impact:

1. **Fit the biggest props you can.** 31 → 65 mm is 5.2 → 15.7 min. This is an
   airframe decision, not an electronics one. It is the only lever that matters
   at this scale.
2. **Spend the 6.5 g of headroom on arms, not electronics.** Every gram of AUW
   costs ~1.5% endurance. Arms that carry 65 mm props are worth far more than
   they cost.
3. **Cell choice buys almost nothing.** 154 Wh/kg (measured on the WLY 250 mAh)
   is already near the practical ceiling for small 1S pouches — the Pro-Range
   360 mAh measures only 78 Wh/kg, which is what a bad pack looks like. An HV
   4.35 V cell buys ~5%.
4. **Drop the camera if you can.** The XIAO Sense + camera board is ~4.6 g of
   the 33.5 g. The plain XIAO ESP32S3 is lighter and ₹1139 vs ₹2199.
5. **Don't fit the piezo unless needed** — ~0.35 g, 0.5% of endurance, already
   marked Optional.

### What 15 min actually costs

| k | Max AUW for 15 min at 65 mm |
|---|---|
| 4.5 | 35 g |
| 5.0 | 33 g |
| 5.5 | 31 g |

At 33.5 g this airframe clears 15 min **only at k=4.5**, with 1.5 g spare. Any
extra frame mass, wire, or a heavier motor breaks it. On 31 mm props 15 min is
not reachable at all — it would need ~29 g of battery.

## Is the 7×20 better than a 1020 for us?

**Yes, for endurance, and it is not close.**

Hover thrust is fixed at AUW. Once a motor can swing the prop, any extra motor mass
is dead weight — it buys thrust capacity that hover never uses. A 1020 is ~1.8 g
heavier per motor (4.5–5.2 g vs 3.4 g), so 4 of them add ~7.2 g of AUW:

| Can | Mass/motor | AUW (65 mm props) | Hover endurance |
|---|---|---|---|
| 7 mm (720) | 3.4 g | 33.5 g | **15.7 min** |
| 8.5 mm (8520) | 4.3 g | 37.1 g | 13.5 min |
| 10 mm (1020) | 5.2 g | 40.7 g | 11.7 min |

Same prop, and the 1020 costs **25% of endurance** — and puts AUW at 40.7 g, i.e.
over the 40 g ceiling before any frame or arms exist.

The mass figure for a 1020 is a fit through the two measured anchors (7 mm →
3.4 g, 8.5 mm → 4.3 g), giving mass ∝ d^1.21, which lands a 1020 at ~5.2 g. The
honest band is 4.5–6.9 g, since a can is shell (∝ d·L) plus magnet/coil (∝ d²·L).
Nothing in that band changes the conclusion.

**When a 1020 would be right:** only if you want more torque for a bigger prop or
more punch. A 1020 on 90 mm props does beat the 720 on 65 mm (16.3 vs 15.7 min) —
but at 40.7 g AUW that win only exists outside your budget.

**Is the 7×20 under-powered?** No. Four of them at 18–25 g thrust each on a
33.5 g AUW gives thrust-to-weight of 2.2–3.0, which is normal for a micro quad.
There is no control-authority problem that would justify the heavier can.

So the 7×20 isn't just "the only one in stock" — on this airframe and this budget
it is the better part.

## Flight controller

**Seeed XIAO ESP32S3 Sense**, Robu `1587654`, ₹2199, **out of stock**.
21 × 17.8 mm, or 21 × 17.8 × 15 mm with the camera expansion board. ESP32-S3R8,
8 MB PSRAM, 8 MB flash, OV2640, PDM mic, microSD, ~102 mA active with the
expansion board.

Seeed publishes **no mass** for either board. The 4.6 g in the weight table is
computed from the PCB volumes plus the OV2640 module and B2B connectors, and is
labelled an estimate in the CSV. This is the one number most worth weighing
yourself once you have the part.

## The buzzer

Strictly piezoelectric: **TDK PS1240P02CT3**, Robu R233556, ₹38, in stock.

Passive transducer, no oscillator, so it needs a square/sine drive at its 4 kHz
resonance. From the [TDK datasheet](https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/06/C76873.pdf):
60 dB(A) min at 10 cm on a **3 V 0-P** rectangular wave, 30 V 0-P absolute max,
12.2 mm × 3.5 mm, **7.6 mm terminal pitch** for the sideways placement.

Rated at 3 V, so a 3V3 GPIO gives full rated swing and **no boost stage is
needed**. Caveat: a piezo is a capacitor, so each edge draws a current spike —
fine at 4 kHz, but check the SoC's per-pin limit; R10's 330 Ω is what tames it.

## Battery connector

**CJT A2543WV-2P**, Robu R229426, ₹7 — upright THT wafer, true **2.54 mm**
pitch. JST XH is **2.5 mm**, not 2.54, despite nearly every Indian listing
saying otherwise; on a 2-pin footprint it does not matter, but the A2543 is the
part that is actually 2.54 mm. Right-angle version: A2543WRA-2P-WH, R229444, ₹9.

## Cost

| | INR |
|---|---|
| Populated (`Included = Yes`) | **2994.38** |
| DNP + optional if fitted | 653.01 |
| Everything fitted | 3647.39 |

The flight controller (₹2199) is 73% of the populated cost; the four motors
(₹542.52) are next. Without the FC the board itself is ₹252.86.

## Availability

| Match | Lines |
|---|---|
| Exact, in stock | 11 |
| Nearest part only | 1 (`D1–D4` SS24L → SS24FL) |
| Substitute (no 1020 anywhere) | 1 (`M1–M4` → 7×20) |
| Exact but **out of stock** | 2 (`U1` XIAO Sense, `U2` BMI270) |
| No component to buy | 2 (solder pads, solder jumpers) |

## Parts with no exact match

| Ref | Status |
|---|---|
| `M1–M4` | No 1020 at Robu/Evelta/Robocraze/Sharvi. Using Sharvi 7×20 (₹135.63, in stock). |
| `U1` | XIAO ESP32S3 Sense is the exact part but out of stock at Robu (₹2199). |
| `U2` | BMI270 out of stock. In-stock LGA-14 alternatives: ICM-42688-P (₹2364), LSM6DSO. |
| `D1–D4` | `SS24L` only as HXY R241435, out of stock. Bought `SS24FL` KEXIN (₹3.46), same SOD-123F 40 V 2 A Schottky. |
| `J14–J21, J25, J26` | Ten bare 1×2 mm copper pads — board copper, nothing to buy. |
| `JP2–JP6` | Five open solder jumpers — two pads and a gap, bridged with solder. |
| Battery | Every small 1S pack at Robu was out of stock. 154 Wh/kg from the WLY 250 mAh is used for the maths. |

## Weight budget detail

Component masses are datasheet values where available, computed otherwise (PCB =
9.75 cm² × 1.6 mm × 1.85 g/cm³ = 2.89 g). Resistors and 0603 caps are 2 mg; the
DMN2058U is 0.009 g from the Diodes Inc datasheet. DNP lines are listed but
excluded from AUW.

Three numbers are estimates and labelled as such: the XIAO Sense at 4.6 g, the
piezo at 0.35 g, and the props at 0.35 g each.

Nothing accounts for a frame, arms, wires, mounting hardware or solder. On a
40 g ceiling with 6.5 g spare, that is where the remaining budget goes — and
arms are what let you use the 65 mm props that triple the endurance.

## Reproducing

```
python3 gen_bom.py     # writes bom-mini.csv, weight-budget.csv, not-found-exact.csv
```

Prices, stock states and SKUs are literals in `gen_bom.py` with the date read,
so re-running regenerates the same sheets.
