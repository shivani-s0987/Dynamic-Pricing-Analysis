from pathlib import Path
import pandas as pd, pytest
from sqlalchemy import text
from src.database import get_engine
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"data/processed"
def test_sqlite_reconciliation():
    engine=get_engine()
    with engine.connect() as con:
        tables={row[0] for row in con.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
        if "sales_demand" not in tables:
            pytest.skip("SQLite tables not loaded; run python -m src.load_data for integration reconciliation")
        count=con.execute(text("SELECT COUNT(*) FROM sales_demand")).scalar()
        if not count:
            pytest.skip("SQLite sales table is empty; run python -m src.load_data for integration reconciliation")
        revenue=con.execute(text("SELECT SUM(revenue) FROM sales_demand")).scalar()
    sales=pd.read_csv(P/"sales_demand_clean.csv")
    assert abs(float(revenue)-float(sales.revenue.sum()))<.02
