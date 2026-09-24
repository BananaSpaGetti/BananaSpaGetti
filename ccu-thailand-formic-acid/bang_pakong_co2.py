"""EGAT Bang Pakong: how much CO2 it emits vs how much a formic acid plant needs.

Plant facts from egat.co.th/home/bangpakong-pp/ (checked Sep 2026): 3,248 MW,
thermal + combined-cycle units, natural gas (fuel oil / diesel backup).
Capacity factor and emission factor are ASSUMED ranges (not published on that page);
replace with EGAT sustainability-report figures when available.
Run: python3 bang_pakong_co2.py
"""
import math

CAPACITY_MW = 3248
CF = (0.30, 0.50, 0.70)             # assumed capacity factor range
EF_T_PER_MWH = (0.37, 0.45)         # CCGT ~0.35-0.40, gas steam units ~0.5; blend assumed
FA_T_PER_YR = 10000                 # formic acid plant (85 % grade), ~ Thai imports, see market/
CO2_PER_T_FA = 44.01 / 46.03 * 0.85
CAPTURE_RATE = 0.90
FLUE_CO2_VOL = 0.04                 # CO2 in combined-cycle flue gas, ~3-4 vol%
DECLINE = 0.10                      # assumed yearly fall in emissions

need = FA_T_PER_YR * CO2_PER_T_FA
print(f"Formic acid {FA_T_PER_YR:,} t/yr (85 %) needs {need:,.0f} t CO2/yr")
print("\nBang Pakong emissions (Mt CO2/yr):")
print("   CF   " + "  ".join(f"EF {ef:.2f}" for ef in EF_T_PER_MWH))
lo = None
for cf in CF:
    em = [CAPACITY_MW * 8760 * cf * ef for ef in EF_T_PER_MWH]
    lo = em[0] if lo is None else min(lo, em[0])
    print(f"  {cf:.0%}   " + "    ".join(f"{e/1e6:5.1f}" for e in em)
          + f"    -> we use {need/em[0]:.2%} - {need/em[1]:.2%}")

years = math.log(lo / need) / -math.log(1 - DECLINE)
print(f"\nWorst case ({lo/1e6:.1f} Mt, falling {DECLINE:.0%}/yr): still enough CO2 for {years:.0f} years")

co2_th = need / CAPTURE_RATE / 8000           # t/h, 8,000 operating h/yr
mol_h = co2_th * 1e6 / 44.01
flue_nm3_h = mol_h / FLUE_CO2_VOL * 0.022414
print(f"\nSlipstream: {co2_th:.2f} t CO2/h in flue gas -> {flue_nm3_h:,.0f} Nm3/h at {FLUE_CO2_VOL:.0%} CO2")
print(f"  = flue gas of about {co2_th/EF_T_PER_MWH[0]:.1f} MW of combined-cycle output "
      f"({co2_th/EF_T_PER_MWH[0]/CAPACITY_MW:.2%} of the plant)")
