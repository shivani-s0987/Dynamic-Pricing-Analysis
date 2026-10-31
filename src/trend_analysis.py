import pandas as pd
from .pricing_metrics import add_price_changes, price_volatility

def monthly_trends(sales):
    x=sales.copy(); x["sale_date"]=pd.to_datetime(x.sale_date)
    x["year_month"]=x.sale_date.dt.to_period("M").astype(str)
    return x.groupby("year_month",as_index=False).agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum"),
        units=("quantity_sold","sum"),gross_margin=("gross_profit","sum")).assign(
        gross_margin=lambda d:d.gross_profit/d.revenue)

def price_trends(prices):
    x=add_price_changes(prices)
    x["month"]=pd.to_datetime(x.observation_date).dt.to_period("M").astype(str)
    return x
