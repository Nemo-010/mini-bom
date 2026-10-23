# Mini — BOM and weight budget

Sourcing sheet for the KiCad BOM in
[the gist](https://gist.github.com/sounddrill31/6b8cd79947475711873521c7521a1664)
(`john-minidrone.csv`), plus the motor, battery and PCB the brief asked about.

Sourcing order was **Robu.in → Evelta → Robocraze → Mouser/Element14**, in that
order of preference. Everything was checked on **2026-10-23** by reading the
live product page (the `Availability:` field and the price at qty 1), not a
search-results badge.

- [`bom-mini.csv`](bom-mini.csv) — one chosen part per BOM line, with an
  `Included` column (`Yes` / `Optional`) next to the reference
- [`weight-budget.csv`](weight-budget.csv) — per-part mass, AUW, and the
  battery/flight-time trade
- [`not-found-exact.csv`](not-found-exact.csv) — what is not an exact match,
  and why

## The two things that need your decision

**1. 15 minutes and a 10 g battery are mutually exclusive.**

A 10 g 1S pack at the measured 154 Wh/kg is **1.54 Wh**, about 416 mAh. At a
32.5 g AUW that is **~7.6 minutes** of hover, not 15. Hitting 15 minutes needs
a **~35 g** pack, which pushes AUW to **~57 g** — nearly double the 30 g
target. So: 30 g, or 15 min. Not both on this airframe.

| | Motor 4.3 g | Motor 5.0 g | Motor 6.0 g |
|---|---|---|---|
| Airframe, no battery | 22.50 g | 25.30 g | 29.30 g |
| AUW with the 10 g pack | 32.50 g | 35.30 g | 39.30 g |
| Flight time on 10 g | 7.6 min | 7.0 min | 6.3 min |
| Pack mass for 15 min | 35.0 g | 39.4 g | 45.6 g |
| AUW needed for 15 min | 57.5 g | 64.7 g | 74.9 g |

Even at the most optimistic motor mass the board is **2.5 g over** the 30 g
budget before any frame, wires or fasteners exist.

**2. There is no 1020 motor for sale in India.**

Robu, Evelta and Robocraze do not stock a 1020. Robu's brushed-coreless
category has only 615 / 720 / 8520; Evelta has 0615 / 720 / 8520; Robocraze has
7x16 and 8x20. A 1020 means AliExpress or a direct Chinese vendor, so there is
no INR price or lead time to quote. The 720 (₹551/pair at Robu, ₹350 for 4 at
Evelta) and 8520 (₹459/pair) are the drop-in substitutes if the frame allows.

Because of that, the motor mass in the weight table is a **band, not a number**.
No 1020 datasheet was obtainable, so it is anchored on real measurements: a
720 (7 × 20 mm) is 3.4 g and an 8520 (8.5 × 20 mm) is ~4.3 g. A 1020 is a
10 × 20 mm can — fatter than both — so it cannot be lighter than 4.3 g, and
scaling the 8520 by (10/8.5)² gives ~6.0 g. Confirm on the actual part.

## The buzzer

Strictly piezoelectric, as required. **TDK PS1240P02CT3**, Robu R233556, ₹38,
in stock.

It is a passive transducer with no oscillator, so it needs a square or sine
drive at its 4 kHz resonance. From the [TDK datasheet](https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/06/C76873.pdf):

- 60 dB(A) min at 10 cm, measured on a **3 V 0-P** rectangular wave at 4 kHz
- 30 V 0-P absolute maximum
- 12.2 mm dia × 3.5 mm, **7.6 mm terminal pitch** — matches the 7.6 mm hole
  spacing, and it is placed sideways
- −10 to +70 °C operating

Rated at 3 V means a 3V3 GPIO from the nRF52840 or ESP32-S3 already gives full
rated swing, so **no boost stage is needed**. One caveat worth knowing: a piezo
is a capacitor, not a resistor, so the pin sees a transient current spike at
each edge. Driving it straight from a GPIO is fine at 4 kHz but check the
per-pin source/sink limit in the SoC datasheet before doing it without a
buffer; R10 (330 Ω) in series is what tames that.

The BOM's `BZ1` row has a blank footprint, so this is a THT part on an
otherwise mostly-SMD board. It is marked **Optional**, per your note that it is
a last-minute add-on.

## Battery connector

**CJT A2543WV-2P**, Robu R229426, ₹7, in stock — upright (180°) THT wafer,
true **2.54 mm** pitch, so it drops into the 2.54 mm holes.

One correction on the common claim: JST XH is **2.5 mm** pitch, not 2.54 mm,
even though most Indian listings title it "JST-XH 2.54mm". On a 2-pin
footprint the 0.04 mm/pin error does not matter in practice, but the A2543 is
the part that is actually 2.54 mm. It mates with the A2543H female housing and
A2543 crimp terminals. A right-angle version (A2543WRA-2P-WH, R229444, ₹9) is
also in stock if you want a lower profile.

## Cost

| | INR |
|---|---|
| Populated (`Included = Yes`) | **252.86** |
| DNP + optional if fitted | 653.01 |
| Everything fitted | 905.87 |

The DNP column is dominated by the BMI270 (₹599, **out of stock**) and the four
JST-GH connectors (₹44 each — the single most expensive thing on the board
after the IMU). The JST-GH choice is worth revisiting: GH is a 1.25 mm latching
series and needs GHR-02V-S mating plugs, which is a lot of money and fiddliness
for four motor leads on a sub-30 g build. Solder pads or JST-PH would be far
cheaper.

## Availability

| Match | Lines |
|---|---|
| Exact match, in stock | 10 |
| Nearest part only — not exact | 1 (`D1–D4` SS24L → SS24FL) |
| Exact but **out of stock** | 1 (`U2` BMI270) |
| No component to buy | 2 (solder pads, solder jumpers) |

## Parts with no exact match

| Ref | BOM part | Status |
|---|---|---|
| `D1–D4` | `SS24L`, SOD-123F | The only `SS24L` at Robu is HXY R241435 and it is **Out of Stock**; Vishay `SS24L` is not stocked. Bought `SS24FL` KEXIN (R194451, ₹3.46) — same SOD-123F/FL body, 40 V 2 A Schottky. These are the motor flyback diodes. |
| `U2` | `BMI270` | Exact part exists (R155006) but is **Out of Stock**. In-stock LGA-14 alternatives: TDK ICM-42688-P (R184326, ₹2364) or ST LSM6DSO. DNP anyway. |
| `J14–J21, J25, J26` | `Conn_01x01_Socket`, `SolderWirePad` | Ten bare 1×2 mm exposed copper pads. Board copper, not a purchased part. |
| `JP2–JP6` | `Jumper_2_Open` | Five open solder jumpers — two pads and a gap, bridged with solder. Also just board copper. A 0R 0603 would be the alternative if they were footprinted as resistors. |
| 1020 motor | — | Not stocked in India by any of the three. See above. |
| Battery | — | Every small 1S pack checked at Robu was Out of Stock (WLY 230/250/300/450 mAh). The 250 mAh cell's 6 g / 154 Wh/kg figure is used for the weight maths. |

## Weight budget detail

Component masses are datasheet values where a datasheet gives one, computed
otherwise (the PCB is 9.75 cm² × 1.6 mm × 1.85 g/cm³ = 2.89 g). Resistors and
0603 capacitors are 2 mg each; the DMN2058U is 0.009 g from the Diodes Inc
datasheet. DNP lines are listed but excluded from AUW.

Two numbers are estimates and are labelled as such in the CSV: the piezo at
~0.35 g (TDK does not publish a mass) and the propellers at 0.35 g each.

Nothing here accounts for a frame, wires, mounting hardware or solder. On a
sub-30 g target those are not negligible — the 22.5 g airframe is already 75%
of budget with no structure at all.

## Reproducing

```
python3 gen_bom.py     # writes bom-mini.csv, weight-budget.csv, not-found-exact.csv
```

All prices, stock states and SKUs are literals in `gen_bom.py` with the date
they were read, so re-running regenerates the same sheets. Refresh the literals
to re-check.
