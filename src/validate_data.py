from pathlib import Path
import pandas as pd, json
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"data/processed"
def validate():
    prod=pd.read_csv(P/"products_clean.csv"); prices=pd.read_csv(P/"price_observations_clean.csv")
    sales=pd.read_csv(P/"sales_demand_clean.csv"); comps=pd.read_csv(P/"competitor_prices_clean.csv")
    checks={}
    checks["products_at_least_100"]=len(prod)>=100
    checks["price_observation_ids_unique"]=prices.observation_id.is_unique
    checks["price_product_fk"]=bool(prices.product_id.isin(prod.product_id).all())
    checks["positive_prices"]=bool((prices.our_price>0).all())
    checks["discount_range"]=bool(prices.discount_pct.between(0,1).all())
    checks["sales_nonnegative_quantity"]=bool((sales.quantity_sold>=0).all())
    checks["revenue_reconciliation"]=bool(((sales.revenue-sales.realized_unit_price*sales.quantity_sold).abs()<.02).all())
    checks["gross_profit_reconciliation"]=bool(((sales.gross_profit-sales.revenue+sales.unit_cost*sales.quantity_sold).abs()<.02).all())
    checks["competitor_positive_prices"]=bool((comps.competitor_price>0).all())
    result={"checks":checks,"passed":int(sum(checks.values())),"total":len(checks),"status":"PASS" if all(checks.values()) else "FAIL"}
    (P/"validation_report.json").write_text(json.dumps(result,indent=2,default=str))
    if not all(checks.values()): raise ValueError(f"Data validation failed: {result}")
    return result
if __name__=="__main__": print(json.dumps(validate(),indent=2,default=str))
