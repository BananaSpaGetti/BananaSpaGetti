"""Cost of CO2 capture (30 wt% MEA) at a 655 MW USC lignite plant (Mae Moh-like),
and a rough levelized cost of CO2-based formic acid.

All inputs are literature-typical assumptions, NOT values from
Win, Opaprakasit & Papong (2023), J. Clean. Prod. 414, 137595 (paywalled).
Edit ASSUMPTIONS and rerun: python3 cost_model.py
"""

ASSUMPTIONS = dict(
    net_mw=655,                 # plant rating, MW
    capacity_factor=0.80,
    ef_t_per_mwh=0.95,          # t CO2/MWh, lignite USC
    capture_rate=0.90,
    capex_usd=900e6,            # capture + compression plant, USD
    discount_rate=0.08,
    life_yr=25,
    fixed_om_frac=0.03,         # of CAPEX per year
    elec_penalty_mwh_per_t=0.28,  # steam for reboiler (~3.6 GJ/t) + compression, as lost power
    elec_price_usd_mwh=60,
    mea_kg_per_t=1.5,
    mea_usd_per_kg=2.0,
    other_var_usd_per_t=2.0,    # cooling water, NaOH, waste disposal
    usd_thb=34.0,
    # formic acid (CO2 + H2 -> HCOOH, amine-assisted, Ru catalyst)
    h2_usd_per_kg=4.0,          # green H2; grey H2 ~1.5-2
    fa_steam_gj_per_t=15.0,     # formate splitting + distillation
    steam_usd_per_gj=8.0,
    fa_elec_mwh_per_t=0.3,
    fa_capex_usd_per_t_yr=1200, # USD per (t/yr) capacity
    fa_other_usd_per_t=40,      # catalyst, amine makeup, labour, maintenance
)


def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def capture_cost(a):
    mwh = a["net_mw"] * 8760 * a["capacity_factor"]
    co2 = mwh * a["ef_t_per_mwh"]
    captured = co2 * a["capture_rate"]
    capex_yr = a["capex_usd"] * crf(a["discount_rate"], a["life_yr"])
    fom_yr = a["capex_usd"] * a["fixed_om_frac"]
    var_t = (a["elec_penalty_mwh_per_t"] * a["elec_price_usd_mwh"]
             + a["mea_kg_per_t"] * a["mea_usd_per_kg"] + a["other_var_usd_per_t"])
    total_yr = capex_yr + fom_yr + var_t * captured
    return dict(mwh=mwh, co2=co2, captured=captured, capex_t=capex_yr / captured,
                fom_t=fom_yr / captured, var_t=var_t, cost_t=total_yr / captured)


def formic_acid_cost(a, co2_cost_t):
    co2_t = 44.01 / 46.03            # t CO2 per t HCOOH
    h2_kg = 2.016 / 46.03 * 1000     # kg H2 per t HCOOH
    items = {
        "CO2": co2_t * co2_cost_t,
        "H2": h2_kg * a["h2_usd_per_kg"],
        "steam": a["fa_steam_gj_per_t"] * a["steam_usd_per_gj"],
        "electricity": a["fa_elec_mwh_per_t"] * a["elec_price_usd_mwh"],
        "capex": a["fa_capex_usd_per_t_yr"] * crf(a["discount_rate"], a["life_yr"]),
        "other": a["fa_other_usd_per_t"],
    }
    return co2_t, h2_kg, items


def main(a=ASSUMPTIONS):
    c = capture_cost(a)
    print(f"Generation        {c['mwh']/1e6:8.2f} TWh/yr")
    print(f"CO2 emitted       {c['co2']/1e6:8.2f} Mt/yr")
    print(f"CO2 captured      {c['captured']/1e6:8.2f} Mt/yr")
    print(f"  CAPEX           {c['capex_t']:8.1f} USD/t")
    print(f"  fixed O&M       {c['fom_t']:8.1f} USD/t")
    print(f"  variable+energy {c['var_t']:8.1f} USD/t")
    print(f"Capture cost      {c['cost_t']:8.1f} USD/t  = {c['cost_t']*a['usd_thb']:,.0f} THB/t")

    print("\nSensitivity (capture cost, USD/t):")
    for key, lo, hi in [("capex_usd", 600e6, 1200e6), ("elec_price_usd_mwh", 40, 90),
                        ("capacity_factor", 0.6, 0.9), ("discount_rate", 0.05, 0.10)]:
        vals = []
        for v in (lo, hi):
            b = dict(a, **{key: v})
            vals.append(capture_cost(b)["cost_t"])
        print(f"  {key:20s} {lo:>10g} -> {vals[0]:5.1f} | {hi:>10g} -> {vals[1]:5.1f}")

    co2_t, h2_kg, items = formic_acid_cost(a, c["cost_t"])
    print(f"\nFormic acid: {co2_t:.3f} t CO2 and {h2_kg:.1f} kg H2 per t HCOOH (100% basis)")
    for k, v in items.items():
        print(f"  {k:12s} {v:7.0f} USD/t")
    total = sum(items.values())
    print(f"Levelized cost    {total:7.0f} USD/t HCOOH = {total*a['usd_thb']:,.0f} THB/t")
    print(f"Grey H2 (1.8 USD/kg): {total - h2_kg*(a['h2_usd_per_kg']-1.8):7.0f} USD/t")
    print(f"If all captured CO2 went to FA: {c['captured']/co2_t/1e6:.1f} Mt HCOOH/yr "
          "(global market is ~1 Mt/yr)")


if __name__ == "__main__":
    main()
