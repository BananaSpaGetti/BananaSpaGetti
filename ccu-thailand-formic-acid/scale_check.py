"""Convert ALL captured Bang Pakong CO2 to formic acid (team deck, Sep 2026)
vs size the unit to the Thai market (our design).

Shows why the product must be sized to the market, not to the capture potential:
at full scale the output is several times the world market and the electrolyzer
needs most of the power plant's own output.
H2 is counted on CO2 actually converted to product (1 mol H2 per mol HCOOH).
All inputs come from params.py (sources in SOURCES.md).
Run: python3 scale_check.py
"""
from bang_pakong_co2 import block_emissions
from params import v

M = dict(HCOOH=v("M_HCOOH"), CO2=v("M_CO2"), H2=v("M_H2"))
PEM_KWH_PER_KG = v("PEM_KWH_KG")                  # S09
DESIGN_T = v("TARGET_T_YR") * v("GRADE")          # S18, as 100 % HCOOH
WORLD_MARKET_T = v("WORLD_FA_T")                  # S13

rows = block_emissions()
plant_co2 = sum(r[6] for r in rows)
plant_mwh = sum(r[5] for r in rows)
GAS_POWER_T_PER_MWH = plant_co2 / plant_mwh       # Bang Pakong average, from S02 + S04

co2_ratio = v("FA_CO2_KG_YR") / v("FA_PLANT_KG_YR")   # S11: kg CO2 used per kg HCOOH
CASES = {
    # team deck (S04): 85 % capture of all CO2, 65 % reactor + purification yield
    "All captured CO2 (team deck)": dict(co2_in=plant_co2 * 0.85, yield_=0.65),
    # our design, CO2 use per kg as in the Tzitzili plant (S11)
    "Market-sized 10,000 t/yr": dict(co2_in=DESIGN_T * co2_ratio,
                                     yield_=M["CO2"] / M["HCOOH"] / co2_ratio),
}

print(f"Bang Pakong: {plant_co2/1e6:.2f} Mt CO2/yr, {plant_mwh/1e6:.2f} TWh/yr\n")
print(f"{'':34s}" + "".join(f"{k:>30s}" for k in CASES))


def row(label, fn, fmt):
    print(f"{label:34s}" + "".join(f"{fmt(fn(c)):>30s}" for c in CASES.values()))


def fa_t(c):
    return c["co2_in"] * M["HCOOH"] / M["CO2"] * c["yield_"]


def h2_t(c):
    return fa_t(c) * M["H2"] / M["HCOOH"]


def pem_mwh(c):
    return h2_t(c) * 1000 * PEM_KWH_PER_KG / 1000


row("CO2 used (t/yr)", lambda c: c["co2_in"], lambda v: f"{v:,.0f}")
row("  share of plant CO2", lambda c: c["co2_in"] / plant_co2, lambda v: f"{v:.2%}")
row("HCOOH produced (t/yr, 100 %)", fa_t, lambda v: f"{v:,.0f}")
row("  x our design size", lambda c: fa_t(c) / DESIGN_T, lambda v: f"{v:,.1f}x")
row("  x world market", lambda c: fa_t(c) / WORLD_MARKET_T, lambda v: f"{v:.3f}x")
row("H2 on converted CO2 (t/yr)", h2_t, lambda v: f"{v:,.0f}")
row("PEM electricity (GWh/yr)", lambda c: pem_mwh(c) / 1000, lambda v: f"{v:,.1f}")
row("  share of plant output", lambda c: pem_mwh(c) / plant_mwh, lambda v: f"{v:.2%}")
row("CO2 if PEM runs on gas power (t)", lambda c: pem_mwh(c) * GAS_POWER_T_PER_MWH, lambda v: f"{v:,.0f}")
row("  as share of CO2 used", lambda c: pem_mwh(c) * GAS_POWER_T_PER_MWH / c["co2_in"], lambda v: f"{v:.0%}")
print("\nThe last line does not depend on scale: gas-powered electrolysis gives back most of the CO2,"
      "\nso the PEM needs renewable power (solar / REC) at any size.")
