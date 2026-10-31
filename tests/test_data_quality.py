from pathlib import Path
import pandas as pd, json
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"data/processed"
def test_clean_price_observations_are_valid():
    x=pd.read_csv(P/"price_observations_clean.csv")
    assert x.observation_id.is_unique
    assert (x.our_price>0).all()
    assert (x.list_price>0).all()
    assert x.discount_pct.between(0,1).all()
def test_quarantine_has_reasons():
    q=pd.read_csv(P/"price_observations_quarantined.csv")
    assert len(q)>0
    assert q.validation_reasons.notna().all()
def test_data_quality_report():
    d=json.loads((P/"data_quality_report.json").read_text())
    assert d["quarantined_price_observations"]>0
    assert d["clean_price_observations"]>10000
