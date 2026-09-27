"""Every input number used by the scripts, each tied to a row in SOURCES.md.

status: "ok"      value read in the source text itself
        "check"   value from a search-result excerpt; the team must open the source to confirm
        "team"    data or engineering choice supplied by the team (screenshots, shop prices, CF)
        "method"  a calculation convention, not data (e.g. six-tenths scaling rule)
Numbers with no public source are NOT in this file; they are listed in SOURCES.md as "quote needed".
"""

P = {
    # --- physical constants ---
    "M_CO2": dict(value=44.01, unit="g/mol", src="S01", status="ok"),
    "M_H2": dict(value=2.016, unit="g/mol", src="S01", status="ok"),
    "M_HCOOH": dict(value=46.03, unit="g/mol", src="S01", status="ok"),
    "EF_GAS": dict(value=56.1, unit="g CO2/MJ", src="S02", status="check"),

    # --- Bang Pakong ---
    "BP_MW": dict(value=3248, unit="MW", src="S03", status="team"),
    "BP_BLOCKS": dict(value=[("Replacement units 1-2 (CCGT, base load)", 1386, 5600, 0.65),
                             ("Block 5 (CCGT, mid-merit)", 710, 7500, 0.45),
                             ("Units 3-4 (thermal, standby)", 1152, 10500, 0.15)],
                      unit="(name, MW, heat rate kJ/kWh, CF)", src="S04", status="team"),
    "FLUE_CO2": dict(value=0.04, unit="vol fraction", src="S05", status="check"),
    "FLUE_O2": dict(value=0.12, unit="vol fraction", src="S05", status="check"),

    # --- CO2 capture with 30 wt% MEA ---
    "MEA_REGEN_GJ_T": dict(value=3.7, unit="GJ/t CO2", src="S06", status="check"),
    "MEA_MAKEUP_KG_T": dict(value=2.2, unit="kg MEA/t CO2", src="S07", status="check"),
    "CAPTURE_RATE": dict(value=0.90, unit="-", src="S08", status="check"),
    "CAPTURE_USD_T": dict(value=61, unit="USD2018/t CO2 captured", src="S08", status="check"),
    "CAPTURE_USD_T_REV4": dict(value=80, unit="USD2018/t CO2 captured", src="S08", status="check"),

    # --- H2 by PEM electrolysis ---
    "PEM_KWH_KG": dict(value=51.2, unit="kWh/kg H2", src="S09", status="check"),
    "ELEC_THB_KWH": dict(value=3.95, unit="THB/kWh (average tariff, excl. VAT)", src="S10", status="check"),

    # --- formic acid plant benchmark: Tzitzili et al. 2025, Table 5, Case A ---
    "FA_PLANT_KG_YR": dict(value=13_030_330, unit="kg HCOOH/yr (99.78 %)", src="S11", status="ok"),
    "FA_TCI_USD": dict(value=26_743_000, unit="USD", src="S11", status="ok"),
    "FA_OPEX_USD_YR": dict(value=15_386_000, unit="USD/yr", src="S11", status="ok"),
    "FA_UNIT_COST_USD_KG": dict(value=1.18, unit="USD/kg HCOOH", src="S11", status="ok"),
    "FA_PRICE_USD_KG": dict(value=1.40, unit="USD/kg (price used in the study)", src="S11", status="ok"),
    "FA_MSP_USD_KG": dict(value=1.36, unit="USD/kg minimum selling price", src="S11", status="ok"),
    "FA_CO2_KG_YR": dict(value=14_000_000, unit="kg CO2/yr processed (\"around 14 kMT\")", src="S11", status="ok"),
    "FA_OPEX_SPLIT": dict(value=dict(facility=0.22, labour=0.15, utilities=0.25, raw_materials=0.36),
                          unit="share of operating cost", src="S11", status="ok"),

    # --- markets and money ---
    "USD_THB": dict(value=33.426, unit="THB/USD, 24 Sep 2569", src="S12", status="check"),
    "WORLD_FA_T": dict(value=971_600, unit="t/yr (2025)", src="S13", status="check"),
    "THAI_IMPORT_JAN_THB": dict(value={2023: 17_949_062, 2024: 15_011_012, 2025: 24_286_161, 2026: 21_364_092},
                                unit="THB CIF, January only", src="S14", status="team"),
    "FARM_CASE_THB": dict(value=(1570, 1800), unit="THB per case of 6 x 5 kg", src="S15", status="team"),
    "FARM_GALLON_THB": dict(value=(240, 380), unit="THB per 5 kg gallon", src="S15", status="team"),

    # --- design choices (team) ---
    "TARGET_T_YR": dict(value=10_000, unit="t/yr of product", src="S18", status="team"),
    "GRADE": dict(value=0.85, unit="mass fraction HCOOH", src="S18", status="team"),

    # --- calculation conventions ---
    "SCALE_EXP": dict(value=0.6, unit="-", src="S16", status="method"),
}


def v(key):
    return P[key]["value"]


def tag(key):
    p = P[key]
    return f"[{p['src']} {p['status']}]"


if __name__ == "__main__":
    for k, p in P.items():
        print(f"{k:22s} {str(p['value'])[:40]:40s} {p['unit']:40s} {p['src']} {p['status']}")
