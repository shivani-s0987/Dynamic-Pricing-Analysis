"""Descriptive price-demand associations; not causal estimates."""
import pandas as pd
import numpy as np

def product_price_demand(sales, min_rows=30):
    x=sales.copy()
    x["sale_date"]=pd.to_datetime(x.sale_date)
    rows=[]
    for pid,g in x.groupby("product_id"):
        g=g[(g.realized_unit_price>0)&(g.quantity_sold>=0)]
        corr=g.realized_unit_price.corr(g.quantity_sold) if len(g)>=min_rows and g.realized_unit_price.nunique()>1 else np.nan
        rows.append({"product_id":pid,"observations":len(g),"price_demand_correlation":corr,
                     "sample_sufficient":bool(len(g)>=min_rows and g.realized_unit_price.nunique()>1)})
    return pd.DataFrame(rows)

def pre_post_price_changes(prices, sales, window=7):
    p=prices.copy(); s=sales.copy()
    p["observation_date"]=pd.to_datetime(p.observation_date); s["sale_date"]=pd.to_datetime(s.sale_date)
    p=p.sort_values(["product_id","observation_date"])
    p["prev"]=p.groupby("product_id").our_price.shift()
    p=p[(p.prev.notna()) & ((p.our_price/p.prev-1).abs()>=.03)]
    rows=[]
    for r in p.itertuples():
        before=s[(s.product_id==r.product_id)&(s.sale_date<r.observation_date)&(s.sale_date>=r.observation_date-pd.Timedelta(days=window))]
        after=s[(s.product_id==r.product_id)&(s.sale_date>=r.observation_date)&(s.sale_date<r.observation_date+pd.Timedelta(days=window))]
        if len(before) and len(after):
            rows.append({"product_id":r.product_id,"date":r.observation_date,"price_change_pct":r.our_price/r.prev-1,
                "before_units_per_day":before.quantity_sold.mean(),"after_units_per_day":after.quantity_sold.mean(),
                "demand_change_pct":after.quantity_sold.mean()/before.quantity_sold.mean()-1 if before.quantity_sold.mean() else np.nan})
    return pd.DataFrame(rows)
