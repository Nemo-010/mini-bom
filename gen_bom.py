#!/usr/bin/env python3
"""Generate the Mini drone BOM, sourcing sheet and weight budget.

Input  : john-minidrone.csv  (KiCad BOM export, from the gist)
Output : bom-mini.csv, not-found-exact.csv, weight-budget.csv

Sourcing order is fixed: Robu.in first, Evelta second, Robocraze third,
Mouser / Element14 / other last.  Every price and stock field below was read
from the live product page on 2026-10-23, not from a search-results badge.
"""

import csv

# ref, qty, value, dnp, included, footprint, supplier, part, sku, mpn, unit_inr,
# avail, lead, match, url, datasheet, notes
ROWS = [
    dict(ref="BZ1", qty=1, value="Buzzer (piezo, THT)", dnp="", included="Optional",
         fp="THT radial, 7.6 mm pin pitch, mounted sideways",
         supplier="Robu", part="TDK PS1240P02CT3 piezo buzzer, 12.2 mm x 3.5 mm",
         sku="R233556", mpn="PS1240P02CT3", unit=38.00, avail="In Stock", lead="Not published",
         match="exact-piezo",
         url="https://robu.in/product/1-month-warranty-872/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/06/C76873.pdf",
         notes=("Strictly piezoelectric: passive transducer, no oscillator, needs an AC/square drive "
                "at its 4 kHz resonance. 60 dB(A) min at 10 cm on a 3 V 0-P rectangular wave; 30 V 0-P "
                "absolute max. Rated at 3 V, so a 3V3 GPIO pin is already enough swing and no boost "
                "stage is needed. Terminal pitch 7.6 mm matches the 7.6 mm hole spacing on the board. "
                "Fits the BOM footprint field, which is blank for BZ1. DNP/optional per the build note.")),

    dict(ref="C1,C2,C3,C4", qty=4, value="10n", dnp="", included="Yes",
         fp="C_0603_1608Metric",
         supplier="Robu", part="Murata GCM188R91H103KA37D 50 V 10 nF X8R 0603",
         sku="R183983", mpn="GCM188R91H103KA37D", unit=3.00, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/gcm188r91h103ka37d-murata-electronics-50v-10nf-x8r-%c2%b110-0603-multilayer-ceramic-capacitors-mlcc-smd-smt-rohs/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/11/C710687.pdf",
         notes=("Branded 10 nF 0603. The generic 50-pack (594976, Rs 0.72) is in stock and cheaper if "
                "brand does not matter. X8R is a 150 C dielectric, which is more than this needs but "
                "it is the in-stock 0603 10 nF at Robu.")),

    dict(ref="C5,C6", qty=2, value="100n", dnp="DNP", included="Optional",
         fp="C_0603_1608Metric",
         supplier="Robu", part="Murata GRM188R71H104KA93D 50 V 100 nF X7R 0603",
         sku="R207385", mpn="GRM188R71H104KA93D", unit=1.88, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/grm188r71h104ka93d-murata-electronics-50v-100nf-x7r-%c2%b110-0603-multilayer-ceramic-capacitors-mlcc-smd-smt-rohs/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/02/C77055.pdf",
         notes=("Marked DNP in the source BOM. Counted in the DNP cost column, excluded from the "
                "populated cost and from the flying weight. Generic 100 nF 0603 pack (594998) is out of stock.")),

    dict(ref="D1,D2,D3,D4", qty=4, value="SS24L", dnp="", included="Yes",
         fp="D_SOD-123F",
         supplier="Robu", part="KEXIN SS24FL 40 V 2 A SOD-123FL Schottky",
         sku="R194451", mpn="SS24FL", unit=3.46, avail="In Stock", lead="Not published",
         match="nearest-not-exact",
         url="https://robu.in/product/ss24fl-kexin-40v-550mv2a-2a-sod-123fl-schottky-diodes-rohs/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/12/C489144.pdf",
         notes=("The exact MPN SS24L is stocked only as HXY R241435 and that is Out of Stock; Vishay "
                "SS24L is not stocked at all. SS24FL is the same 40 V 2 A Schottky in the same "
                "SOD-123F/FL body. These are the motor flyback diodes. Source BOM datasheet link is the "
                "Vishay SS32 sheet, kept for reference.")),

    dict(ref="J1", qty=1, value="Conn_01x02_Socket", dnp="DNP", included="Optional",
         fp="PinHeader_1x02_P2.54mm_Vertical",
         supplier="Robu", part="CONNFLY DS1021-1x2SF11-B 1x2 2.54 mm pin header V/T",
         sku="R197647", mpn="DS1021-1x2SF11-B", unit=11.00, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/ds1021-1x2sf11-b-connfly-1x2-pin-2-54mm-pin-header-v-t-type/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/04/DS1021.pdf",
         notes="Marked DNP in the source BOM. Counted in DNP cost only, not in populated cost or weight."),

    dict(ref="J10", qty=1, value="Conn_01x02_Socket", dnp="DNP", included="Optional",
         fp="PinHeader_1x02_P1.27mm_Vertical",
         supplier="Robu", part="XUNPU PH1.27-01-02PZD 1x2 1.27 mm pin header",
         sku="R219020", mpn="PH1.27-01-02PZD", unit=1.25, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/ph1-27-01-02pzd-xunpu-plugin1x2-pin-1-27mm-pin-headers-rohs/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/06/C41360737.pdf",
         notes="Marked DNP in the source BOM. Counted in DNP cost only."),

    dict(ref="J11,J22,J23,J24", qty=4, value="Conn_01x02_Socket", dnp="", included="Yes",
         fp="JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical",
         supplier="Robu", part="JST BM02B-GHS-TBT(LF)(SN) GH 1x2 1.25 mm SMT",
         sku="R174872", mpn="BM02B-GHS-TBT(LF)(SN)", unit=44.00, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/bm02b-ghs-tbtlfsn-jst-1x2p-2p-gh-tin-2-25%e2%84%8385%e2%84%83-1a-1-1-25mm-phosphor-bronze-standing-paste-smdp1-25mm-wire-to-board-connector-rohs/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/10/C161690.pdf",
         notes=("These are the four motor connectors. GH is the 1.25 mm locking series, so the motor "
                "wires need mating GHR-02V-S plugs. Rs 44 each is the single biggest line-item cost "
                "after the IMU; a JST-PH or solder-pad alternative would be much cheaper if the "
                "latching is not required.")),

    dict(ref="J12", qty=1, value="Conn_01x02 (battery, THT upright)", dnp="", included="Yes",
         fp="THT vertical wafer, 2.54 mm pin pitch (fits 2.54 mm holes)",
         supplier="Robu", part="CJT A2543WV-2P 2.54 mm 180 deg (vertical) wafer, male, 2 pin",
         sku="R229426", mpn="A2543WV-2P", unit=7.00, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/a2543wv-2p-cjt-2-pin-2-54mm-180-wafer-male-connector-rohs/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/08/A2543WV-XP_dwg.pdf",
         notes=("Battery connector, upright THT, true 2.54 mm pin pitch so it drops straight into the "
                "2.54 mm hole spacing. Note JST XH is 2.5 mm pitch, not 2.54 mm, despite most listings "
                "saying 2.54 - on a 2-hole footprint the 0.04 mm per pin does not matter, but the A2543 "
                "is the part that is actually 2.54 mm. Mates with the CJT A2543H 2.54 mm female housing "
                "plus A2543 series crimp terminals. A 90 deg right-angle version (A2543WRA-2P-WH, "
                "R229444, Rs 9.00) is also in stock if the board needs a low profile.")),

    dict(ref="J14,J15,J16,J17,J18,J19,J20,J21,J25,J26", qty=10, value="Conn_01x01_Socket",
         dnp="", included="Yes", fp="SolderWirePad_1x01_SMD_1x2mm",
         supplier="", part="", sku="", mpn="", unit=None, avail="n/a", lead="n/a",
         match="no-component", url="", ds="",
         notes=("Bare 1x2 mm exposed SMD copper pads on the PCB for soldering wires directly to. "
                "This is board copper, not a purchased part, so there is nothing to source and no cost.")),

    dict(ref="JP2,JP3,JP4,JP5,JP6", qty=5, value="Jumper_2_Open", dnp="", included="Yes",
         fp="SolderJumper-2_P1.3mm_Open",
         supplier="", part="", sku="", mpn="", unit=None, avail="n/a", lead="n/a",
         match="no-component", url="", ds="",
         notes=("Open solder jumpers are two exposed pads with a gap, bridged with solder. Board "
                "copper only, no part to buy. A 0R 0603 (e.g. Yageo RC0603JR-070RL) would be the "
                "alternative if these were footprinted as resistors instead.")),

    dict(ref="Q1,Q2,Q3,Q4", qty=4, value="DMN2058U", dnp="", included="Yes",
         fp="SOT-23",
         supplier="Robu", part="Diodes Inc DMN2058U-13 20 V 4.6 A N-channel SOT-23",
         sku="R246407", mpn="DMN2058U-13", unit=10.00, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/dmn2058u-13-diodes-incorporated-20v-4-6a-740mw-35m%cf%8910v4-6a-1-2v-1-n-channel-sot-23-mosfets-rohs/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/08/C5245280.pdf",
         notes=("Motor low-side switches, one per motor. The -13 tape variant is in stock; the -7 is "
                "Out of Stock at Robu. 35 mOhm at 10 V gate, which is comfortably on for a 3V3 drive. "
                "Cheaper logic-level options exist (SI2300 R248300, Rs 3.08) if cost matters more "
                "than matching the original MPN.")),

    dict(ref="R1,R4,R6,R8", qty=4, value="10k", dnp="", included="Yes",
         fp="R_0603_1608Metric",
         supplier="Robu", part="Yageo RC0603JR-0710KP 10k 5% 0603",
         sku="R232165", mpn="RC0603JR-0710KP", unit=0.83, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/rc0603jr-0710kp-yageo-100mw-thick-film-resistors-%c2%b15-%c2%b1150ppm-%e2%84%83-10k%cf%89-0603-chip-resistor-surface-mount-rohs/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/07/2506161050_YAGEO-RC0402FR-07220RP_C7038454.pdf",
         notes=("Gate pulldowns for the four MOSFETs. Panasonic ERJ3EKF1002V (R241058, Rs 0.49) is "
                "also in stock and cheaper.")),

    dict(ref="R2,R3,R5,R7", qty=4, value="10", dnp="", included="Yes",
         fp="R_0603_1608Metric",
         supplier="Robu", part="Royal Ohm 0603WAF100JT5E 10 ohm 1% 0603",
         sku="R134794", mpn="0603WAF100JT5E", unit=0.12, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/0603waf100jt5e-uniohm-royal-ohm-100mw-thick-film-resistors-75v-%c2%b11-%c2%b1400ppm-%e2%84%8310%cf%89-0603-chip-resistor-surface-mount-rohs/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/07/C22859.pdf",
         notes="Series gate resistors. Panasonic ERJ3GEYJ100V (R209007, Rs 0.35) also in stock."),

    dict(ref="R10", qty=1, value="330", dnp="", included="Yes",
         fp="R_0603_1608Metric",
         supplier="Robu", part="Yageo RC0603FR-07330RL 330 ohm 1% 0603",
         sku="R138686", mpn="RC0603FR-07330RL", unit=0.22, avail="In Stock", lead="Not published",
         match="exact",
         url="https://robu.in/product/rc0603fr-07330rl-yageo-res-thick-film-0603-330-ohm-1-0-1w1-10w-%c2%b1100ppm-c-pad-smd-t-r/",
         ds="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/06/C105881.pdf",
         notes="Likely the series resistor on the buzzer drive line."),

    dict(ref="U2", qty=1, value="BMI270", dnp="DNP", included="Optional",
         fp="XDCR_BMI270 (LGA-14)",
         supplier="Robu", part="Bosch BMI270 6-axis IMU",
         sku="R155006", mpn="BMI270", unit=599.00, avail="Out of Stock", lead="Not published",
         match="exact-oos",
         url="https://robu.in/product/bosch-bmi270motion-sensoric22-g-4-g-8-g-16-g/",
         ds="",
         notes=("Marked DNP in the source BOM. Exact part, but Out of Stock at Robu on 2026-10-23. "
                "This is the only line with no in-stock exact option. Alternatives in stock at Robu: "
                "TDK ICM-42688-P (R184326, Rs 2364, LGA-14) or ST LSM6DSO (also LGA-14). BMI270 is "
                "I2C/SPI, 2.5 x 3.0 x 0.8 mm. Only needed if the flight loop runs on this board.")),
]

# Non-BOM items the brief asked about: motors, battery, PCB.
EXTRAS = [
    dict(item="Motor (1020)", qty=4, supplier="", part="", sku="", unit=None, avail="n/a",
         notes=("No 1020 coreless motor is stocked by Robu, Evelta or Robocraze. Robu's brushed "
                "coreless category only has 615 / 720 / 8520; Evelta has 0615 / 720 / 8520; "
                "Robocraze has 7x16 and 8x20 only. Buying 1020 means AliExpress or a direct "
                "Chinese vendor, so there is no Indian price or lead time to quote. The 720 and "
                "8520 at Robu are the drop-in substitutes if the frame can take a 7x20 or 8.5x20 "
                "motor instead.")),
    dict(item="Battery (1S, ~10 g target)", qty=1, supplier="Robu", part="WLY 1S LiPo range",
         sku="see notes", unit=None, avail="Mostly Out of Stock",
         notes=("Every small 1S pack checked at Robu was Out of Stock on 2026-10-23 (WLY551145 "
                "230 mAh, WLY602025 250 mAh, WLY601145 300 mAh, WLY52535 450 mAh). Capacity for "
                "15 min is computed in weight-budget.csv; it comes out far above what 10 g buys, "
                "so 15 min and 10 g cannot both hold on this airframe.")),
    dict(item="PCB", qty=1, supplier="", part="32.5 mm x 30 mm, 2-layer", sku="", unit=None,
         avail="n/a",
         notes="Bare board, not a component. Weight is computed in weight-budget.csv."),
]


def money(v):
    return "" if v is None else f"{v:.2f}"


def write_bom(path):
    head = ["Reference", "Qty", "Value", "Included", "DNP", "Footprint",
            "Supplier", "Product", "SKU", "MPN", "Unit_Price_INR", "Ext_Price_INR",
            "Availability", "Lead_Time", "Match", "URL", "Datasheet", "Notes"]
    tot_pop = tot_dnp = 0.0
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(head)
        for r in ROWS:
            ext = None if r["unit"] is None else r["unit"] * r["qty"]
            if ext is not None:
                if r["included"] == "Yes":
                    tot_pop += ext
                else:
                    tot_dnp += ext
            w.writerow([r["ref"], r["qty"], r["value"], r["included"], r["dnp"], r["fp"],
                        r["supplier"], r["part"], r["sku"], r["mpn"],
                        money(r["unit"]), money(ext), r["avail"], r["lead"],
                        r["match"], r["url"], r["ds"], r["notes"]])
        w.writerow([])
        w.writerow(["TOTAL", "", "", "Populated (Included=Yes)", "", "", "", "", "", "",
                    "", money(tot_pop), "", "", "", "", "",
                    "Sum of In Stock lines that are actually populated."])
        w.writerow(["TOTAL", "", "", "DNP / Optional", "", "", "", "", "", "", "",
                    money(tot_dnp), "", "", "", "", "",
                    "Cost of the DNP + optional lines if you choose to fit them."])
        w.writerow(["TOTAL", "", "", "Grand total if everything fitted", "", "", "", "", "",
                    "", "", money(tot_pop + tot_dnp), "", "", "", "", "", ""])
    return tot_pop, tot_dnp


def write_not_found(path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Reference", "Qty", "Value", "Footprint", "Why_not_exact",
                    "Nearest_available", "Nearest_URL", "Datasheet"])
        for r in ROWS:
            if r["match"] in ("exact", "exact-piezo"):
                continue
            nearest, nurl = "", ""
            if r["match"] == "nearest-not-exact":
                nearest = "KEXIN SS24FL, R194451, Rs 3.46, In Stock (bought as the line item)"
                nurl = r["url"]
            elif r["match"] == "exact-oos":
                nearest = "TDK ICM-42688-P R184326 Rs 2364, or ST LSM6DSO, both LGA-14, in stock"
                nurl = "https://robu.in/product/icm-42688-p-tdk-invensense/"
            w.writerow([r["ref"], r["qty"], r["value"], r["fp"], r["notes"], nearest, nurl, r["ds"]])
        w.writerow(["1020 motor", 4, "1020 coreless", "10 x 20 mm",
                    EXTRAS[0]["notes"], "", "", ""])
        w.writerow(["BAT1", 1, "1S LiPo", "~10 g",
                    EXTRAS[1]["notes"], "", "", ""])


def write_weight(path):
    """Weight budget and the battery/flight-time trade that comes with it.

    Anchors used, all from live pages or datasheets:
      720 coreless (7 x 20 mm)  = 3.4 g each      Evelta product page
      8520 coreless (8.5 x 20)  = ~4.3 g each     AliExpress listings
      WLY 250 mAh 1S            = 6 g, 154 Wh/kg  Robu product page
      Pro-Range 360 mAh 1S      = 17 g, 78 Wh/kg  Robu product page

    A 1020 is a 10 x 20 mm can, i.e. fatter than both a 720 and an 8520, so it
    cannot be lighter than 4.3 g. Scaling 8520 by (10/8.5)^2 gives ~6.0 g; the
    table uses 4.3 g / 5.0 g / 6.0 g as a band instead of pretending to one
    number, because no 1020 datasheet was obtainable.
    """
    PCB_AREA = 3.25 * 3.00          # cm
    FR4_DENSITY = 1.85              # g/cm3
    PCB_T = 0.16                    # cm, 1.6 mm
    pcb_g = PCB_AREA * PCB_T * FR4_DENSITY

    rows = [
        # section, ref, qty, each_g, source
        ("PCB", "PCB1 (32.5 x 30 mm, 1.6 mm FR4, 2-layer)", 1, round(pcb_g, 3),
         "computed: 9.75 cm2 x 0.16 cm x 1.85 g/cm3"),
        ("COMPONENT", "C1-C4 10nF 0603", 4, 0.002, "typical 0603 MLCC"),
        ("COMPONENT", "C5,C6 100nF 0603 (DNP)", 2, 0.002, "DNP, excluded from AUW"),
        ("COMPONENT", "D1-D4 SS24FL SOD-123FL", 4, 0.012, "computed from SOD-123FL body x mold density"),
        ("COMPONENT", "J11,J22,J23,J24 JST-GH 1x2 SMT", 4, 0.15, "typical 1.25 mm SMT 1x2 header + shell"),
        ("COMPONENT", "J12 CJT A2543WV-2P THT 2.54 mm wafer", 1, 0.30,
         "THT 2-pin 2.54 mm wafer + plastic body"),
        ("COMPONENT", "J1 2.54 mm 1x2 (DNP)", 1, 0.30, "DNP, excluded from AUW"),
        ("COMPONENT", "J10 1.27 mm 1x2 (DNP)", 1, 0.05, "DNP, excluded from AUW"),
        ("COMPONENT", "Q1-Q4 DMN2058U SOT-23", 4, 0.009, "Diodes Inc datasheet, 0.009 g"),
        ("COMPONENT", "R1,R4,R6,R8 10k 0603", 4, 0.002, "Vishay CRCW0603 mass = 2 mg"),
        ("COMPONENT", "R2,R3,R5,R7 10R 0603", 4, 0.002, "Vishay CRCW0603 mass = 2 mg"),
        ("COMPONENT", "R10 330R 0603", 1, 0.002, "Vishay CRCW0603 mass = 2 mg"),
        ("COMPONENT", "U2 BMI270 LGA-14 (DNP)", 1, 0.012, "DNP, excluded from AUW"),
        ("OPTIONAL", "BZ1 TDK PS1240P02CT3 piezo", 1, 0.35,
         "TDK 12.2 mm x 3.5 mm brass-disc piezo, ~0.35 g estimate; not on the datasheet"),
        ("MOTOR", "1020 coreless, low case (4.3 g)", 4, 4.3,
         "cannot be lighter than an 8520 (8.5 x 20 mm, ~4.3 g) since a 1020 is a 10 x 20 mm can"),
        ("PROP", "Propeller 1020-class 2-blade", 4, 0.35, "typical 55-65 mm micro prop"),
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Section", "Item", "Qty", "Unit_g", "Total_g", "Source"])
        pop = 0.0
        dnp = 0.0
        for sec, item, qty, each, src in rows:
            tot = qty * each
            w.writerow([sec, item, qty, f"{each:g}", f"{tot:g}", src])
            if "(DNP)" in item:
                dnp += tot
            elif sec == "OPTIONAL":
                dnp += tot
            else:
                pop += tot
        w.writerow([])
        w.writerow(["", "Populated airframe, no battery", "", "", f"{pop:.2f}", ""])
        w.writerow(["", "DNP + optional parts if fitted", "", "", f"{dnp:.2f}", ""])
        w.writerow([])
        w.writerow(["BATTERY", "10 g 1S pack = 1.54 Wh, 416 mAh nominal", 1, 10.0, 10.0,
                    "10 g at 154 Wh/kg, the WLY 250 mAh cell's measured density"])
        w.writerow(["RESULT", "AUW with the 10 g pack", "", "", f"{pop + 10.0:.2f}", ""])
        w.writerow(["RESULT", "Budget", "", "", "30.00", "given in the brief"])
        w.writerow(["RESULT", "Headroom against the 30 g budget", "", "",
                    f"{30.0 - (pop + 10.0):+.2f}",
                    "negative = over budget"])
        w.writerow(["RESULT", "Verdict", "", "",
                    "OVER BUDGET" if pop + 10.0 > 30.0 else "within budget", ""])
        w.writerow([])
        w.writerow(["PROBLEM", "15 min and a 10 g battery cannot both hold", "", "", "",
                    "a 10 g 1S pack is 1.54 Wh, which is ~7 min of hover at this AUW. "
                    "Reaching 15 min needs a ~35 g pack and pushes AUW to ~57 g, i.e. "
                    "almost double the 30 g target. Pick one: 30 g, or 15 min."])

        # Battery / flight-time trade, hover at 0.30 W/g, 80% depth of discharge.
        w.writerow(["TRADE", "Motor mass per motor (g)", "4.3", "5.0", "6.0",
                    "band: 8520-equivalent up to (10/8.5)^2 scaled from 8520"])
        psp, dod, wh_g = 0.30, 0.8, 0.154
        for mg in (4.3, 5.0, 6.0):
            pass
        # fixed airframe differs per motor mass; recompute per column
        airframes = []
        for mg in (4.3, 5.0, 6.0):
            fixed = pop - 4 * 4.3 + 4 * mg
            airframes.append(fixed)
        w.writerow(["TRADE", "Airframe, no battery (g)"] +
                   [f"{a:.2f}" for a in airframes] + [""])
        auw10 = [a + 10.0 for a in airframes]
        w.writerow(["TRADE", "AUW with 10 g pack (g)"] +
                   [f"{a:.2f}" for a in auw10] + [""])
        t10 = []
        for a in auw10:
            P = a * psp
            t10.append(10.0 * wh_g * dod / P * 60)
        w.writerow(["TRADE", "Flight time on the 10 g pack (min)"] +
                   [f"{t:.1f}" for t in t10] +
                   ["1.54 Wh x 0.8 / hover power; hover power = AUW x 0.30 W/g"])

        # Solve for the pack that would actually give 15 minutes.
        need = []
        for a in airframes:
            m = a + 20.0
            for _ in range(200):
                P = m * psp
                Wh = P * 15 / 60 / dod
                m2 = a + Wh / wh_g
                if abs(m2 - m) < 1e-9:
                    break
                m = m2
            need.append((m - a, m))
        w.writerow(["TRADE", "Pack mass for 15 min (g)"] +
                   [f"{b:.1f}" for b, _ in need] + [""])
        w.writerow(["TRADE", "AUW needed for 15 min (g)"] +
                   [f"{m:.1f}" for _, m in need] +
                   ["iterated to convergence; 15 min and a 10 g pack cannot both hold"])
    return pop, pop + 10.0


if __name__ == "__main__":
    p, d = write_bom("bom-mini.csv")
    write_not_found("not-found-exact.csv")
    a, b = write_weight("weight-budget.csv")
    print(f"populated INR {p:.2f}, DNP INR {d:.2f}")
    print(f"airframe no battery {a:.2f} g, AUW with 10 g pack {b:.2f} g")
