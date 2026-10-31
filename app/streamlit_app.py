from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from src.pricing_metrics import add_price_changes, competitor_benchmark, scenario

st.set_page_config(page_title="Dynamic Pricing Intelligence",page_icon="📈",layout="wide")
st.title("Dynamic Pricing Analysis & Revenue Intelligence")
st.caption("Synthetic retail pricing and demand analytics · Competitor data is simulated")
P=ROOT/"data/processed"
@st.cache_data
def load():
    sales=pd.read_csv(P/"sales_demand_clean.csv",parse_dates=["sale_date"])
    prices=pd.read_csv(P/"price_observations_clean.csv",parse_dates=["observation_date"])
    comps=pd.read_csv(P/"competitor_prices_clean.csv",parse_dates=["observation_date"])
    products=pd.read_csv(P/"products_clean.csv")
    return sales,prices,comps,products
try:
    sales,prices,comps,products=load()
except Exception as e:
    st.error(f"Data files unavailable. Run `python -m src.generate_data` then `python -m src.clean_data`. Details: {e}")
    st.stop()
sales=sales.merge(products[["product_id","category","product_name","unit_cost"]],on="product_id",how="left",suffixes=("","_master"))
bench=competitor_benchmark(prices,comps).merge(products[["product_id","category","product_name"]],on="product_id",how="left")
page=st.sidebar.radio("Navigate",["Executive overview","Price trends & volatility","Competitor benchmarking","Revenue & demand","Pricing opportunities","What-if simulator"])
categories=["All"]+sorted(products.category.unique().tolist())
cat_filter=st.sidebar.selectbox("Category",categories)
if cat_filter!="All":
    sales=sales[sales.category==cat_filter]; prices=prices[prices.product_id.isin(products.loc[products.category==cat_filter,"product_id"])]
    bench=bench[bench.category==cat_filter]
start=max(sales.sale_date.min(),prices.observation_date.min()).date()
end=min(sales.sale_date.max(),prices.observation_date.max()).date()
date_range=st.sidebar.date_input("Date range",(start,end),min_value=start,max_value=end)
if isinstance(date_range,tuple) and len(date_range)==2:
    lo,hi=pd.Timestamp(date_range[0]),pd.Timestamp(date_range[1])
    sales=sales[sales.sale_date.between(lo,hi)]; prices=prices[prices.observation_date.between(lo,hi)]
    bench=bench[bench.observation_date.between(lo,hi)]
if page=="Executive overview":
    revenue=sales.revenue.sum(); gp=sales.gross_profit.sum(); units=sales.quantity_sold.sum()
    avgsp=revenue/units if units else np.nan; margin=gp/revenue if revenue else np.nan
    medchange=add_price_changes(prices).price_change_pct.median()
    priceidx=bench.relative_price_index.median()
    k=st.columns(5)
    for c,label,val in zip(k,["Revenue","Gross profit","Gross margin","Avg selling price","Median price index"],
        [f"{revenue:,.0f}",f"{gp:,.0f}",f"{margin:.1%}",f"{avgsp:,.2f}",f"{priceidx:.1f}" if pd.notna(priceidx) else "N/A"]): c.metric(label,val)
    monthly=sales.assign(month=sales.sale_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum"))
    st.plotly_chart(px.line(monthly,x="month",y=["revenue","gross_profit"],title="Monthly revenue and gross profit"),use_container_width=True)
    cat=sales.groupby("category",as_index=False).agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum"))
    st.plotly_chart(px.bar(cat,x="category",y="revenue",title="Revenue by category"),use_container_width=True)
    st.info("Overview reflects the selected date range and category. Synthetic observational data does not prove causal pricing impact.")
elif page=="Price trends & volatility":
    pids=sorted(prices.product_id.unique())
    pid=st.selectbox("Product",pids)
    x=add_price_changes(prices[prices.product_id==pid])
    st.plotly_chart(px.line(x,x="observation_date",y="our_price",title=f"Observed price history — {pid}"),use_container_width=True)
    st.plotly_chart(px.bar(x,x="observation_date",y="price_change_pct",title="Daily percentage price changes"),use_container_width=True)
    vol=add_price_changes(prices).groupby("product_id").price_change_pct.std().rename("volatility").reset_index().merge(products[["product_id","category"]],on="product_id")
    st.plotly_chart(px.box(vol,x="category",y="volatility",title="Price volatility by category"),use_container_width=True)
elif page=="Competitor benchmarking":
    st.metric("Benchmark coverage",f"{bench.competitor_median.notna().mean():.1%}")
    st.plotly_chart(px.histogram(bench,x="relative_price_index",nbins=40,title="Relative price index distribution (100 = benchmark)"),use_container_width=True)
    latest=bench.sort_values("observation_date").groupby("product_id",as_index=False).tail(1)
    st.dataframe(latest[["product_id","category","our_price","competitor_median","competitor_count","price_gap","relative_price_index"]].sort_values("relative_price_index",ascending=False),use_container_width=True)
elif page=="Revenue & demand":
    monthly=sales.assign(month=sales.sale_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum"),units=("quantity_sold","sum"))
    st.plotly_chart(px.line(monthly,x="month",y=["revenue","gross_profit"],title="Revenue and gross profit trend"),use_container_width=True)
    st.plotly_chart(px.scatter(sales,x="realized_unit_price",y="quantity_sold",color="category",opacity=.35,title="Price versus daily units sold"),use_container_width=True)
    st.warning("These are descriptive associations. Seasonality, promotions, inventory and product mix can confound price-demand relationships.")
elif page=="Pricing opportunities":
    bm=bench.groupby("product_id",as_index=False).agg(median_price_index=("relative_price_index","median"),benchmark_coverage=("competitor_median",lambda s:s.notna().mean()))
    ps=sales.groupby("product_id",as_index=False).agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum"),units=("quantity_sold","sum"))
    ps["gross_margin"]=ps.gross_profit/ps.revenue
    opp=products.merge(ps,on="product_id").merge(bm,on="product_id",how="left")
    high_margin=st.slider("Low-margin threshold",0.0,.4,.12,.01)
    gap=st.slider("Large relative price index",100,160,115,5)
    opp["review_reason"]=np.select([opp.gross_margin<high_margin,opp.median_price_index>gap,opp.median_price_index<85],
        ["Low gross margin","Above benchmark","Below benchmark"],default="Monitor")
    opp["priority"]=np.where((opp.gross_margin<high_margin)|(opp.median_price_index>gap),"High","Monitor")
    st.dataframe(opp.sort_values(["priority","gross_margin"],ascending=[True,True]),use_container_width=True)
    st.download_button("Download opportunity CSV",opp.to_csv(index=False).encode(),file_name="pricing_opportunities.csv",mime="text/csv")
else:
    pid=st.selectbox("Product for scenario",sorted(sales.product_id.unique()))
    row=sales[sales.product_id==pid]
    base_price=float(row.realized_unit_price.mean()); base_qty=float(row.quantity_sold.sum()); base_cost=float(row.unit_cost.mean())
    pchange=st.slider("Proposed price change (%)",-50,50,5,1)/100
    dchange=st.slider("Assumed demand change (%)",-100,100,-5,1)/100
    cchange=st.slider("Unit cost change (%)",-50,50,0,1)/100
    result=scenario(base_price,base_qty,base_cost,pchange,dchange,cchange)
    cols=st.columns(3)
    cols[0].metric("Baseline revenue",f"{result['baseline_revenue']:,.2f}")
    cols[1].metric("Scenario revenue",f"{result['scenario_revenue']:,.2f}",f"{result['revenue_difference']:+,.2f}")
    cols[2].metric("Scenario gross profit",f"{result['scenario_gross_profit']:,.2f}",f"{result['gross_profit_difference']:+,.2f}")
    st.write({"baseline_price":base_price,"scenario_price":result["scenario_price"],"baseline_quantity":base_qty,
        "scenario_quantity":result["scenario_quantity"],"baseline_margin":result["baseline_margin"],"scenario_margin":result["scenario_margin"]})
    st.warning("Demand response is a user-entered assumption, not a validated elasticity estimate. Results are illustrative.")
