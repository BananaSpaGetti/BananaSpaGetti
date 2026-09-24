"""Lab-scale CO2 + H2 -> HCOOH in a 100 ml SS316 / PTFE-lined autoclave.

Stoichiometry, limiting reactant, theoretical and actual yield, pressure at
reaction temperature (safety check against the 0-5 MPa gauge and the liner
rating) and the charge/energy a PEM electrolyzer needs to make the H2.

Gas moles use the ideal gas law (Z ~ 0.95-1.0 for CO2/H2 below 3 MPa near room
temperature, so the error is a few %). CO2 dissolved in the liquid (large when a
base such as triethylamine or KHCO3 is present) is not counted; weigh the
autoclave before and after charging if you need the real amount.
Conversion and selectivity are inputs, not predictions: replace them with
measured values (HPLC/IC or titration of the product).
Edit ASSUMPTIONS and rerun: python3 lab_scale_calc.py
"""

R = 8.314          # J/(mol K)
F = 96485.0        # C/mol e-
M_CO2, M_H2, M_FA = 44.01, 2.016, 46.03   # g/mol

ASSUMPTIONS = dict(
    vessel_ml=100.0,            # PTFE liner volume
    liquid_ml=40.0,             # solvent + base + catalyst; headspace = vessel - liquid
    charge_temp_c=25.0,
    p_co2_mpa=0.6,              # partial pressures at charge temperature (absolute)
    p_h2_mpa=1.2,
    reaction_temp_c=80.0,
    reaction_time_h=2.0,
    conversion=0.30,            # fraction of the limiting reactant consumed
    selectivity=0.90,           # fraction of converted carbon that ends up as HCOOH
    gauge_max_mpa=5.0,          # pressure gauge full scale
    liner_max_mpa=3.0,          # typical PTFE-lined autoclave working limit
    relief_set_mpa=3.3,         # safety relief valve set point
    # PEM electrolyzer used to make the H2 charge
    cell_voltage_v=1.9,
    n_cells=1,
    current_a=2.0,
    faradaic_eff=0.95,
)


def gas_moles(p_mpa, v_ml, t_c):
    return p_mpa * 1e6 * v_ml * 1e-6 / (R * (t_c + 273.15))


def run(a):
    v_gas = a["vessel_ml"] - a["liquid_ml"]
    n_co2 = gas_moles(a["p_co2_mpa"], v_gas, a["charge_temp_c"])
    n_h2 = gas_moles(a["p_h2_mpa"], v_gas, a["charge_temp_c"])

    # CO2 + H2 -> HCOOH is 1:1, so the smaller mole count limits
    limiting = "CO2" if n_co2 <= n_h2 else "H2"
    n_lim = min(n_co2, n_h2)
    n_fa_theory = n_lim
    n_reacted = n_lim * a["conversion"]
    n_fa = n_reacted * a["selectivity"]

    t_ratio = (a["reaction_temp_c"] + 273.15) / (a["charge_temp_c"] + 273.15)
    p_hot_start = (a["p_co2_mpa"] + a["p_h2_mpa"]) * t_ratio
    # both gases are consumed 1:1 by whatever reacted
    n_gas_end = n_co2 + n_h2 - 2 * n_reacted
    p_hot_end = n_gas_end * R * (a["reaction_temp_c"] + 273.15) / (v_gas * 1e-6) / 1e6

    q = 2 * F * n_h2 / a["faradaic_eff"]              # 2 e- per H2
    t_electro_min = q / (a["current_a"] * a["n_cells"]) / 60
    e_wh = q * a["cell_voltage_v"] / 3600

    return dict(v_gas=v_gas, n_co2=n_co2, n_h2=n_h2, limiting=limiting,
                n_fa_theory=n_fa_theory, n_fa=n_fa, p_hot_start=p_hot_start,
                p_hot_end=p_hot_end, q=q, t_electro_min=t_electro_min, e_wh=e_wh)


def main(a=ASSUMPTIONS):
    r = run(a)
    print(f"Headspace             {r['v_gas']:8.1f} ml")
    print(f"CO2 charged           {r['n_co2']*1e3:8.2f} mmol = {r['n_co2']*M_CO2:.3f} g")
    print(f"H2 charged            {r['n_h2']*1e3:8.2f} mmol = {r['n_h2']*M_H2*1e3:.1f} mg")
    print(f"H2:CO2 ratio          {r['n_h2']/r['n_co2']:8.2f}  -> limiting reactant: {r['limiting']}")

    theory_g = r["n_fa_theory"] * M_FA
    actual_g = r["n_fa"] * M_FA
    print(f"\nTheoretical HCOOH     {r['n_fa_theory']*1e3:8.2f} mmol = {theory_g:.3f} g")
    print(f"Actual HCOOH          {r['n_fa']*1e3:8.2f} mmol = {actual_g:.3f} g "
          f"(X = {a['conversion']:.0%}, S = {a['selectivity']:.0%})")
    print(f"Yield                 {actual_g/theory_g:8.1%}")
    print(f"Concentration         {actual_g/(a['liquid_ml']/1000):8.2f} g/L in {a['liquid_ml']:.0f} ml liquid")
    print(f"Space-time yield      {actual_g/(a['liquid_ml']/1000)/a['reaction_time_h']:8.2f} g/(L h)")

    print(f"\nPressure at {a['reaction_temp_c']:.0f} C     "
          f"{r['p_hot_start']:8.2f} MPa at start, {r['p_hot_end']:.2f} MPa at end")
    limit = min(a["liner_max_mpa"], a["gauge_max_mpa"])
    margin = r["p_hot_start"] / limit
    status = "OK" if r["p_hot_start"] < 0.9 * limit else (
        "WARNING: within 10% of limit" if r["p_hot_start"] < limit else "UNSAFE: over limit")
    print(f"Working limit         {limit:8.2f} MPa ({margin:.0%} used) -> {status}")
    if a["relief_set_mpa"] <= r["p_hot_start"]:
        print("                      relief valve would open: lower the charge pressure or temperature")
    t_max = limit * 0.9 / (a["p_co2_mpa"] + a["p_h2_mpa"]) * (a["charge_temp_c"] + 273.15) - 273.15
    print(f"Max temp at 90% limit {t_max:8.0f} C for this charge")

    print(f"\nPEM electrolyzer for the H2 charge ({a['n_cells']} cell, {a['current_a']:g} A, "
          f"{a['cell_voltage_v']:g} V, FE {a['faradaic_eff']:.0%}):")
    print(f"  charge              {r['q']:8.0f} C")
    print(f"  time                {r['t_electro_min']:8.1f} min")
    print(f"  energy              {r['e_wh']:8.2f} Wh")

    print("\nSensitivity (actual HCOOH, mg):")
    for key, lo, hi in [("conversion", 0.1, 0.6), ("selectivity", 0.7, 1.0),
                        ("p_co2_mpa", 0.4, 0.8), ("liquid_ml", 30, 60)]:
        vals = [run(dict(a, **{key: v}))["n_fa"] * M_FA * 1e3 for v in (lo, hi)]
        print(f"  {key:12s} {lo:>6g} -> {vals[0]:6.0f} | {hi:>6g} -> {vals[1]:6.0f}")


if __name__ == "__main__":
    main()
