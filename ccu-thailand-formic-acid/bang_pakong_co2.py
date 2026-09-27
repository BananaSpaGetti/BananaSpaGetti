"""EGAT Bang Pakong: how much CO2 it emits vs how much a formic acid plant needs.

Plant facts from egat.co.th/home/bangpakong-pp/ (checked Sep 2026): 3,248 MW,
thermal + combined-cycle units, natural gas (fuel oil / diesel backup).
Emissions use the team's block-level heat-rate method (IPCC 2006 Tier 2):
  EF_block [kg CO2/kWh] = heat rate [kJ/kWh] x EF_gas [g CO2/MJ] / 1e6
  CO2 = P x 8,760 h x CF x EF_block
Capacity factors are the team's engineering assumptions, not EGAT data; replace with the
EGAT sustainability-report generation figures when available.
All inputs come from params.py (sources in SOURCES.md).
Run: python3 bang_pakong_co2.py
"""
import math

from params import v, tag

EF_GAS_G_PER_MJ = v("EF_GAS")
BLOCKS = v("BP_BLOCKS")             # (name, MW, heat rate kJ/kWh, capacity factor)
FA_T_PER_YR = v("TARGET_T_YR")
CO2_PER_T_FA = v("FA_CO2_KG_YR") / v("FA_PLANT_KG_YR") * v("GRADE")   # actual CO2 use in the Tzitzili plant
CAPTURE_RATE = v("CAPTURE_RATE")
FLUE_CO2_VOL = v("FLUE_CO2")
DECLINE = 0.10                      # what-if only, not data: emissions falling 10 %/yr


def block_emissions():
    rows = []
    for name, mw, hr, cf in BLOCKS:
        ef = hr * EF_GAS_G_PER_MJ / 1e6            # kg CO2/kWh = t CO2/MWh
        mwh = mw * 8760 * cf
        rows.append((name, mw, hr, cf, ef, mwh, mwh * ef))
    return rows


def main():
    rows = block_emissions()
    total_mwh = sum(r[5] for r in rows)
    total_co2 = sum(r[6] for r in rows)
    need = FA_T_PER_YR * CO2_PER_T_FA

    print(f"Bang Pakong emissions by block  {tag('BP_BLOCKS')} {tag('EF_GAS')}:")
    for name, mw, hr, cf, ef, mwh, co2 in rows:
        print(f"  {name:42s} {mw:5,} MW  HR {hr:6,}  CF {cf:.2f}  EF {ef:.3f} t/MWh"
              f"  {mwh/1e6:5.2f} TWh  {co2/1e6:5.2f} Mt")
    print(f"  {'Total':42s} {sum(r[1] for r in rows):5,} MW{'':33s}"
          f"{total_mwh/1e6:5.2f} TWh  {total_co2/1e6:5.2f} Mt")

    print(f"\nFormic acid {FA_T_PER_YR:,} t/yr (85 %) needs {need:,.0f} t CO2/yr "
          f"= {need/total_co2:.2%} of the plant's emissions")
    base_only = rows[0][6]
    print(f"If only units 1-2 keep running: {base_only/1e6:.2f} Mt -> we use {need/base_only:.2%}")

    years = math.log(total_co2 / need) / -math.log(1 - DECLINE)
    print(f"What-if, falling {DECLINE:.0%}/yr from {total_co2/1e6:.2f} Mt: still enough CO2 for {years:.0f} years")

    ef_ccgt = rows[0][4]
    co2_th = need / CAPTURE_RATE / 8000           # t/h, 8,000 operating h/yr
    mol_h = co2_th * 1e6 / 44.01
    flue_nm3_h = mol_h / FLUE_CO2_VOL * 0.022414
    print(f"\nSlipstream {tag('CAPTURE_RATE')} {tag('FLUE_CO2')}: {co2_th:.2f} t CO2/h in flue gas -> {flue_nm3_h:,.0f} Nm3/h at {FLUE_CO2_VOL:.0%} CO2")
    print(f"  = flue gas of about {co2_th/ef_ccgt:.1f} MW of units 1-2 output "
          f"({co2_th/ef_ccgt/rows[0][1]:.2%} of those units)")


if __name__ == "__main__":
    main()
