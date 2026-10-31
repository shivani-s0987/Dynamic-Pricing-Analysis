"""Reusable metric calculations with safe division and comparable time series."""
import numpy as np
import pandas as pd

def safe_divide(numerator, denominator):
    if np.isscalar(denominator) and denominator == 0: return np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        result=np.asarray(numerator)/np.asarray(denominator)
    if np.isscalar(result): return float(result) if np.isfinite(result) else np.nan
    return np.where(np.isfinite(result),result,np.nan)

def add_price_changes(df, group_col="product_id", date_col="observation_date", price_col="our_price"):
    x=df.copy(); x[date_col]=pd.to_datetime(x[date_col])
    x=x.sort_values([group_col,date_col])
    x["previous_price"]=x.groupby(group_col)[price_col].shift(1)
    x["absolute_price_change"]=x[price_col]-x["previous_price"]
    x["price_change_pct"]=safe_divide(x["absolute_price_change"],x["previous_price"])
    return x

def price_volatility(df, group_col="product_id", min_observations=10):
    x=add_price_changes(df,group_col=group_col)
    out=x.groupby(group_col).price_change_pct.agg(["std","count"]).rename(columns={"std":"price_volatility","count":"change_observations"})
    out.loc[out.change_observations<min_observations,"price_volatility"]=np.nan
    return out.reset_index()

def competitor_benchmark(our_prices, competitor_prices):
    cp=competitor_prices.groupby(["observation_date","product_id","region_id","channel_id"],as_index=False).agg(
        competitor_median=("competitor_price","median"),competitor_count=("competitor_price","count"))
    x=our_prices.merge(cp,on=["observation_date","product_id","region_id","channel_id"],how="left")
    x["price_gap"]=x.our_price-x.competitor_median
    x["price_gap_pct"]=x.price_gap/x.competitor_median
    x["relative_price_index"]=100*x.our_price/x.competitor_median
    x.loc[x.competitor_median.isna(),["price_gap","price_gap_pct","relative_price_index"]]=np.nan
    return x

def sales_metrics(sales):
    x=sales.copy()
    x["revenue_calc"]=x.realized_unit_price*x.quantity_sold
    x["cogs_calc"]=x.unit_cost*x.quantity_sold
    x["gross_profit_calc"]=x.revenue_calc-x.cogs_calc
    return x

def scenario(baseline_price, baseline_quantity, unit_cost, price_change_pct=0,
             demand_change_pct=0, cost_change_pct=0):
    vals=[baseline_price,baseline_quantity,unit_cost,price_change_pct,demand_change_pct,cost_change_pct]
    if any(pd.isna(v) for v in vals): raise ValueError("Scenario inputs must be finite numbers")
    if baseline_price<=0 or baseline_quantity<0 or unit_cost<0:
        raise ValueError("Price must be positive; quantity and cost must be non-negative")
    if demand_change_pct < -1: raise ValueError("Demand change cannot be below -100%")
    p=baseline_price*(1+price_change_pct); q=baseline_quantity*(1+demand_change_pct); c=unit_cost*(1+cost_change_pct)
    if p<=0 or c<0: raise ValueError("Scenario price must be positive and cost non-negative")
    rev0=baseline_price*baseline_quantity; gp0=(baseline_price-unit_cost)*baseline_quantity
    rev=p*q; gp=(p-c)*q
    return {"scenario_price":p,"scenario_quantity":q,"baseline_revenue":rev0,"scenario_revenue":rev,
        "revenue_difference":rev-rev0,"baseline_gross_profit":gp0,"scenario_gross_profit":gp,
        "gross_profit_difference":gp-gp0,"baseline_margin":gp0/rev0 if rev0 else np.nan,
        "scenario_margin":gp/rev if rev else np.nan,"scenario_unit_cost":c}
