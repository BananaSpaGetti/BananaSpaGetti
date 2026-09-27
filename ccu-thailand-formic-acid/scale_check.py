"""Convert ALL captured Bang Pakong CO2 to formic acid (team deck, Sep 2026)
vs size the unit to the Thai market (our design).

Shows why the product must be sized to the market, not to the capture potential:
at full scale the output is several times the world market and the electrolyzer
needs most of the power plant's own output.
H2 is counted on CO2 actually converted to product (1 mol H2 per mol HCOOH).
Run: python3 scale_check.py
"""
from bang_pakong_co2 import block_emissions

M = dict(HCOOH=46.03, CO2=44.01, H2=2.016)
PEM_KWH_PER_KG = 52           # IRENA 2022, as in the team deck
GAS_POWER_T_PER_MWH = 0.373   # Bang Pakong average (4.55 Mt / 12.2 TWh)
THAI_IMPORT_T = 8500          # ~10,000 t/yr of 85 % acid (market/market_size.py) as 100 % HCOOH
WORLD_MARKET_T = 1_000_000    # ~ global formic acid demand

rows = block_emissions()
plant_co2 = sum(r[6] for r in rows)
plant_mwh = sum(r[5] for r in rows)

CASES = {
    # team deck: 85 % amine capture of all CO2, 65 % reactor + purification yield
    "All captured CO2 (team deck)": dict(co2_in=plant_co2 * 0.85, yield_=0.65),
    # our design: 10,000 t/yr of 85 % acid = 8,500 t HCOOH, 90 % overall yield
    "Market-sized 10,000 t/yr": dict(co2_in=8500 / 0.90 * M["CO2"] / M["HCOOH"], yield_=0.90),
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
row("  x Thai imports", lambda c: fa_t(c) / THAI_IMPORT_T, lambda v: f"{v:,.1f}x")
row("  x world market", lambda c: fa_t(c) / WORLD_MARKET_T, lambda v: f"{v:.3f}x")
row("H2 on converted CO2 (t/yr)", h2_t, lambda v: f"{v:,.0f}")
row("PEM electricity (GWh/yr)", lambda c: pem_mwh(c) / 1000, lambda v: f"{v:,.1f}")
row("  share of plant output", lambda c: pem_mwh(c) / plant_mwh, lambda v: f"{v:.2%}")
row("CO2 if PEM runs on gas power (t)", lambda c: pem_mwh(c) * GAS_POWER_T_PER_MWH, lambda v: f"{v:,.0f}")
row("  as share of CO2 used", lambda c: pem_mwh(c) * GAS_POWER_T_PER_MWH / c["co2_in"], lambda v: f"{v:.0%}")
print("\nThe last line does not depend on scale: gas-powered electrolysis gives back most of the CO2,"
      "\nso the PEM needs renewable power (solar / REC) at any size.")
