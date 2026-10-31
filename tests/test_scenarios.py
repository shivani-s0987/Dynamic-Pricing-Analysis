from src.pricing_metrics import scenario
def test_no_change_scenario_reconciles():
    x=scenario(25,100,15)
    assert x["scenario_revenue"]==x["baseline_revenue"]==2500
    assert x["scenario_gross_profit"]==x["baseline_gross_profit"]==1000
    assert x["scenario_margin"]==.4
