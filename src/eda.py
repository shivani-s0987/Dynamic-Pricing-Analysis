from pathlib import Path
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .pricing_metrics import add_price_changes, competitor_benchmark
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"data/processed"; OUT=ROOT/"outputs"
def generate():
    OUT.mkdir(exist_ok=True)
    sales=pd.read_csv(P/"sales_demand_clean.csv",parse_dates=["sale_date"])
    prices=pd.read_csv(P/"price_observations_clean.csv",parse_dates=["observation_date"])
    comps=pd.read_csv(P/"competitor_prices_clean.csv",parse_dates=["observation_date"])
    products=pd.read_csv(P/"products_clean.csv")
    sales=sales.merge(products[["product_id","category"]],on="product_id")
    b=competitor_benchmark(prices,comps).merge(products[["product_id","category"]],on="product_id")
    x=add_price_changes(prices).merge(products[["product_id","category"]],on="product_id")
    monthly=sales.assign(month=sales.sale_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(revenue=("revenue","sum"),gp=("gross_profit","sum"),units=("quantity_sold","sum"))
    vol=x.groupby(["product_id","category"],as_index=False).price_change_pct.std()
    figs=[]
    def save(name, title, plotter):
        fig,ax=plt.subplots(figsize=(9,4.5)); plotter(ax); ax.set_title(title); fig.tight_layout(); fig.savefig(OUT/f"{name}.png",dpi=140); plt.close(fig); figs.append(name)
    save("overall_price_trend","Average observed price over time",lambda ax: ax.plot(prices.groupby("observation_date").our_price.mean().index,prices.groupby("observation_date").our_price.mean().values))
    pid=prices.product_id.iloc[0]
    save("product_price_trend",f"Observed price trend — {pid}",lambda ax: ax.plot(prices[prices.product_id==pid].observation_date,prices[prices.product_id==pid].our_price))
    save("competitor_price_comparison","Our price versus competitor median",lambda ax: ax.scatter(b.our_price,b.competitor_median,s=5,alpha=.25))
    save("competitor_gap_distribution","Competitor price-gap percentage distribution",lambda ax: ax.hist(b.price_gap_pct.dropna().clip(-.6,.6),bins=40))
    save("price_volatility_category","Price volatility by category",lambda ax: [ax.boxplot([vol.loc[vol.category==c,"price_change_pct"].dropna(),],positions=[i]) for i,c in enumerate(sorted(vol.category.unique()))] if False else ax.bar(vol.groupby("category").price_change_pct.std().index,vol.groupby("category").price_change_pct.std().values))
    save("price_change_distribution","Daily percentage price-change distribution",lambda ax: ax.hist(x.price_change_pct.dropna().clip(-.3,.3),bins=50))
    save("monthly_revenue_trend","Monthly revenue trend",lambda ax: ax.plot(monthly.month,monthly.revenue))
    save("monthly_gross_profit_trend","Monthly gross-profit trend",lambda ax: ax.plot(monthly.month,monthly.gp))
    save("price_vs_quantity","Observed price versus daily quantity sold",lambda ax: ax.scatter(sales.realized_unit_price,sales.quantity_sold,s=5,alpha=.2))
    save("category_price_comparison","Average observed price by category",lambda ax: ax.bar(prices.merge(products[["product_id","category"]],on="product_id").groupby("category").our_price.mean().index,prices.merge(products[["product_id","category"]],on="product_id").groupby("category").our_price.mean().values))
    save("largest_price_deviations","Products with largest median price-index deviation",lambda ax: ax.bar(b.groupby("product_id").relative_price_index.median().sub(100).abs().nlargest(15).index,b.groupby("product_id").relative_price_index.median().sub(100).abs().nlargest(15).values))
    # Discount and margin comparison by matching date/product
    joined=sales.merge(prices[["product_id","observation_date","list_price","discount_pct"]],left_on=["product_id","sale_date"],right_on=["product_id","observation_date"],how="left")
    bands=pd.cut(joined.discount_pct,[ -0.001,.0001,.05,.10,.20,.30,1.01],labels=["0%","0-5%","5-10%","10-20%","20-30%",">30%"],include_lowest=True)
    dm=joined.assign(discount_band=bands).groupby("discount_band",observed=False).apply(lambda d:d.gross_profit.sum()/d.revenue.sum() if d.revenue.sum() else np.nan)
    save("discount_margin_comparison","Gross margin by discount band",lambda ax: ax.bar(dm.index.astype(str),dm.values))
    save("demand_units_trend","Monthly units sold",lambda ax: ax.plot(monthly.month,monthly.units))
    # Product benchmark opportunity scatter
    prod=sales.groupby("product_id",as_index=False).agg(revenue=("revenue","sum"),gp=("gross_profit","sum"))
    idx=b.groupby("product_id",as_index=False).relative_price_index.median().merge(prod,on="product_id")
    save("pricing_opportunity_scatter","Relative price index versus product revenue",lambda ax: ax.scatter(idx.relative_price_index,idx.revenue,s=idx.gp.clip(lower=0)/idx.gp.clip(lower=0).max()*80+5,alpha=.5))
    return figs
if __name__=="__main__": print(generate())
