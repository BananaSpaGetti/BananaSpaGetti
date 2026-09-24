"""Cryogenic CO2 capture with LNG cold at Bang Pakong, then dry ice -> autoclave.

Why CO2 freezes out and N2/O2/Ar do not is phase equilibrium, not a reaction:
each gas condenses (or, for CO2, desublimes to dry ice) only when the temperature
falls below the point where its vapour pressure equals its partial pressure.
Clausius-Clapeyron:  ln(p / 1 atm) = -(dH/R) * (1/T - 1/T_1atm)
Accuracy is a few K, fine for a feasibility check.
Run: python3 cryo_capture.py
"""
import math

R = 8.314
# gas: (mole fraction in combined-cycle flue gas after water removal is NOT applied here,
#       T at 1 atm [K], enthalpy of vaporisation / sublimation [J/mol])
FLUE = {
    "N2":  (0.74, 77.36, 5570),
    "O2":  (0.12, 90.19, 6820),
    "Ar":  (0.009, 87.30, 6430),
    "CO2": (0.04, 194.69, 25200),   # sublimation: solid <-> gas (dry ice)
}
H2O_FRAC = 0.08                     # removed first by cooling + drying, else it freezes and blocks the exchanger
P_ATM = 1.0                         # flue gas pressure, atm (compressing raises every partial pressure)
T_LNG_C = (-150, -180)              # planned cold-box temperature range

CO2_T_PER_YR = 8127                 # from bang_pakong_co2.py (10,000 t/yr formic acid 85 %)
LNG_COLD_KJ_PER_KG = 830            # LNG -162 C -> 25 C gas, latent + sensible
CP_FLUE = 29.5                      # J/(mol K)
RECUPERATION = 0.85                 # share of cold recovered from the cold outlet gas


def vap_p_atm(gas, t_k):
    _, tb, dh = FLUE[gas]
    return math.exp(-dh / R * (1 / t_k - 1 / tb))


def cond_temp_k(gas, p_atm):
    _, tb, dh = FLUE[gas]
    return 1 / (1 / tb - R * math.log(p_atm) / dh)


print(f"Flue gas at {P_ATM} atm. A gas condenses/freezes below its point:")
for g, (x, _, _) in FLUE.items():
    t = cond_temp_k(g, x * P_ATM)
    print(f"  {g:4s} {x:6.1%}  partial {x*P_ATM:6.3f} atm -> {t-273.15:7.1f} C "
          + ("(solid, dry ice)" if g == "CO2" else "(liquid)"))

print("\nCO2 captured as dry ice vs cold-box temperature:")
x_co2 = FLUE["CO2"][0]
for tc in (-110, -120, -130, -140, -150, -160, -170, -180):
    left = min(vap_p_atm("CO2", tc + 273.15) / P_ATM, x_co2)
    cap = 1 - left * (1 - x_co2) / (x_co2 * (1 - left))
    o2_liq = tc + 273.15 < cond_temp_k("O2", FLUE["O2"][0] * P_ATM)
    print(f"  {tc:5d} C  capture {cap:6.1%}" + ("   O2 would liquefy!" if o2_liq else ""))

# LNG needed: cool whole flue stream from 25 C to -150 C, freeze CO2, minus recuperation
mol_co2 = CO2_T_PER_YR * 1e6 / 44.01
mol_flue = mol_co2 / x_co2 * (1 - H2O_FRAC)  # dry flue per mol CO2
q_gj = (mol_flue * CP_FLUE * 175 * (1 - RECUPERATION) + mol_co2 * 25200) / 1e9
lng_t = q_gj * 1e6 / LNG_COLD_KJ_PER_KG / 1000
print(f"\nCold duty for {CO2_T_PER_YR:,} t CO2/yr (recuperation {RECUPERATION:.0%}): "
      f"{q_gj:,.0f} GJ/yr -> LNG {lng_t:,.0f} t/yr ({lng_t/365:.0f} t/day)")
q0 = (mol_flue * CP_FLUE * 175 + mol_co2 * 25200) / 1e9
print(f"  without recuperation: {q0:,.0f} GJ/yr -> LNG {q0*1e6/LNG_COLD_KJ_PER_KG/1000:,.0f} t/yr")

# Dry ice charge for the 100 ml autoclave (60 ml headspace), CO2:H2 = 1:1
v = 60e-6
print("\nDry ice in the 100 ml autoclave (60 ml headspace, ignores CO2 absorbed by NH3 solution):")
for g in (0.5, 1.0, 1.5):
    n = g / 44.01
    p25 = n * R * 298.15 / v / 1e6
    p80 = 2 * n * R * 353.15 / v / 1e6
    print(f"  {g:.1f} g dry ice -> CO2 alone {p25:4.2f} MPa at 25 C; "
          f"with equal mol H2 at 80 C {p80:4.2f} MPa" + ("  OVER 3 MPa liner" if p80 > 3 else ""))
n_max = 3.0e6 * 0.9 * v / (R * 353.15) / 2
print(f"  max dry ice for 90 % of 3 MPa at 80 C: {n_max*44.01:.2f} g")
