import pandas as pd, numpy as np, pytest
from src.pricing_metrics import safe_divide, add_price_changes, competitor_benchmark, scenario

def test_safe_divide_zero():
    assert np.isnan(safe_divide(2,0))
    assert safe_divide(6,3)==2

def test_price_change():
    d=pd.DataFrame({"product_id":["P1","P1"],"observation_date":["2025-01-01","2025-01-02"],"our_price":[10,12]})
    x=add_price_changes(d)
    assert np.isnan(x.iloc[0].price_change_pct)
    assert x.iloc[1].absolute_price_change==2
    assert x.iloc[1].price_change_pct==pytest.approx(.2)

def test_competitor_median_and_missing():
    ours=pd.DataFrame({"observation_id":[1],"observation_date":["2025-01-01"],"product_id":["P1"],"our_price":[110],"region_id":["N"],"channel_id":["Online"]})
    comps=pd.DataFrame({"observation_date":["2025-01-01"]*3,"product_id":["P1"]*3,"region_id":["N"]*3,"channel_id":["Online"]*3,"competitor_price":[90,100,110]})
    x=competitor_benchmark(ours,comps)
    assert x.iloc[0].competitor_median==100
    assert x.iloc[0].relative_price_index==pytest.approx(110)

def test_scenario():
    r=scenario(100,10,60,.1,-.1,.05)
    assert r["scenario_price"]==pytest.approx(110)
    assert r["scenario_quantity"]==pytest.approx(9)
    assert r["scenario_revenue"]==pytest.approx(990)
    assert r["scenario_gross_profit"]==pytest.approx((110-63)*9)

def test_scenario_rejects_negative_demand_below_minus_100():
    with pytest.raises(ValueError): scenario(100,10,50,0,-1.1)
