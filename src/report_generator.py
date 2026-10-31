from pathlib import Path
import pandas as pd, json, logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .pricing_metrics import add_price_changes, competitor_benchmark
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"data/processed"; OUT=ROOT/"outputs"; REP=ROOT/"reports"
logging.basicConfig(level=logging.INFO,format="%(levelname)s %(message)s")
def generate():
    OUT.mkdir(exist_ok=True); REP.mkdir(exist_ok=True)
    sales=pd.read_csv(P/"sales_demand_clean.csv",parse_dates=["sale_date"])
    prod=pd.read_csv(P/"products_clean.csv")
    prices=pd.read_csv(P/"price_observations_clean.csv",parse_dates=["observation_date"])
    comps=pd.read_csv(P/"competitor_prices_clean.csv",parse_dates=["observation_date"])
    monthly=sales.assign(month=sales.sale_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(
        revenue=("revenue","sum"),gross_profit=("gross_profit","sum"),units=("quantity_sold","sum"))
    monthly["gross_margin"]=monthly.gross_profit/monthly.revenue
    cat=sales.merge(prod[["product_id","category"]],on="product_id").groupby("category",as_index=False).agg(
        revenue=("revenue","sum"),gross_profit=("gross_profit","sum"),units=("quantity_sold","sum"))
    cat["gross_margin"]=cat.gross_profit/cat.revenue
    b=competitor_benchmark(prices,comps)
    prod_b=b.groupby("product_id",as_index=False).agg(median_price_index=("relative_price_index","median"),
        median_gap_pct=("price_gap_pct","median"),competitor_coverage=("competitor_median",lambda s:s.notna().mean()))
    pp=prices.sort_values(["product_id","observation_date"]).copy()
    pp["prev"]=pp.groupby("product_id").our_price.shift()
    pp["price_change_pct"]=pp.our_price/pp.prev-1
    vol=pp.groupby("product_id",as_index=False).price_change_pct.std().rename(columns={"price_change_pct":"price_volatility"})
    prod_sales=sales.groupby("product_id",as_index=False).agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum"),
        units=("quantity_sold","sum"))
    prod_sales["gross_margin"]=prod_sales.gross_profit/prod_sales.revenue
    opp=prod.merge(prod_sales,on="product_id").merge(prod_b,on="product_id",how="left").merge(vol,on="product_id",how="left")
    opp["priority"]= "Monitor"
    opp.loc[(opp.median_price_index>115)&(opp.gross_margin<.15),"priority"]="High"
    opp.loc[(opp.median_price_index<85)&(opp.gross_margin>.25),"priority"]="Review"
    opp.loc[(opp.gross_margin<.12),"priority"]="High"
    opp["review_reason"]=opp.apply(lambda r:"Low gross margin" if r.gross_margin<.12 else
        "Above benchmark and weak margin" if r.median_price_index>115 and r.gross_margin<.15 else
        "Below benchmark; validate positioning" if r.median_price_index<85 and r.gross_margin>.25 else
        "Monitor price volatility / benchmark coverage",axis=1)
    cat.to_csv(OUT/"category_performance.csv",index=False)
    monthly.to_csv(OUT/"monthly_performance.csv",index=False)
    prod_b.to_csv(OUT/"competitor_benchmark_summary.csv",index=False)
    opp.sort_values(["priority","revenue"],ascending=[True,False]).to_csv(REP/"pricing_opportunities.csv",index=False)
    # chart outputs
    fig,ax=plt.subplots(figsize=(10,4.5)); ax.plot(monthly.month,monthly.revenue,label="Revenue"); ax.plot(monthly.month,monthly.gross_profit,label="Gross profit")
    ax.set_title("Monthly Revenue and Gross Profit (Synthetic)"); ax.set_ylabel("Currency units"); ax.tick_params(axis="x",rotation=60); ax.legend(); fig.tight_layout()
    fig.savefig(OUT/"monthly_revenue_profit.png",dpi=150); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.5)); c=cat.sort_values("revenue",ascending=False); ax.bar(c.category,c.revenue); ax.set_title("Revenue by Category (Synthetic)"); ax.tick_params(axis="x",rotation=45); fig.tight_layout()
    fig.savefig(OUT/"category_revenue.png",dpi=150); plt.close(fig)
    revenue=float(sales.revenue.sum()); gp=float(sales.gross_profit.sum()); margin=gp/revenue if revenue else float("nan")
    avg_price=float(sales.revenue.sum()/sales.quantity_sold.sum()) if sales.quantity_sold.sum() else float("nan")
    price_idx=float(prod_b.median_price_index.median())
    high=int((opp.priority=="High").sum())
    generated=pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M UTC")
    md=f"""# Dynamic Pricing Analysis — Executive Summary

Generated: {generated}

**Data disclaimer:** All products, prices, competitor observations, demand and revenue are synthetic. Results are illustrative, not real market intelligence or verified commercial outcomes.

## Scope
- {len(prod):,} products
- {len(prices):,} cleaned price observations
- {len(comps):,} competitor price observations
- {len(sales):,} daily simulated demand observations
- Period: {sales.sale_date.min().date()} to {sales.sale_date.max().date()}

## Core metrics
- Simulated revenue: {revenue:,.2f}
- Simulated gross profit: {gp:,.2f}
- Gross margin: {margin:.2%}
- Average selling price per unit: {avg_price:,.2f}
- Median product-level relative price index: {price_idx:,.1f}
- Products flagged high priority for review: {high}

## Category leaders
{cat.sort_values('revenue',ascending=False).head(5).to_markdown(index=False)}

## Pricing review
{opp.sort_values(['priority','gross_margin']).head(10)[['product_id','category','revenue','gross_margin','median_price_index','priority','review_reason']].to_markdown(index=False)}

## Interpretation
Price-index and profitability flags are screening signals, not automatic price-change recommendations. Competitor observations are synthetic. Observational price-demand associations do not establish causality; seasonality, promotions, stockouts and product mix may confound them. Validate product comparability and test proposed changes with controlled experiments before operational decisions.
"""
    (REP/"executive_summary.md").write_text(md)
    dq=json.loads((P/"data_quality_report.json").read_text())
    (OUT/"data_quality_report.json").write_text(json.dumps(dq,indent=2))
    # PDF report
    styles=getSampleStyleSheet(); story=[Paragraph("Dynamic Pricing Analysis & Revenue Intelligence",styles["Title"]),
        Paragraph("Synthetic portfolio analysis — generated "+generated,styles["Normal"]),Spacer(1,12),
        Paragraph(f"Revenue: {revenue:,.2f} | Gross profit: {gp:,.2f} | Gross margin: {margin:.2%}",styles["Heading2"]),
        Paragraph("All observations are synthetic. This report does not represent actual company or competitor performance.",styles["BodyText"]),Spacer(1,10),
        Image(str(OUT/"monthly_revenue_profit.png"),width=450,height=200),Spacer(1,10),
        Paragraph("Top categories by revenue",styles["Heading2"])]
    rows=[["Category","Revenue","Gross profit","Margin"]]+[[r.category,f"{r.revenue:,.0f}",f"{r.gross_profit:,.0f}",f"{r.gross_margin:.1%}"] for r in cat.sort_values("revenue",ascending=False).head(8).itertuples()]
    tbl=Table(rows,repeatRows=1); tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#16324F")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),.4,colors.grey),("FONTSIZE",(0,0),(-1,-1),8),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F1F5F9")])]))
    story.append(tbl); story.append(Spacer(1,12)); story.append(Paragraph("Review flags are hypotheses for investigation, not causal claims or guaranteed opportunities.",styles["BodyText"]))
    SimpleDocTemplate(str(REP/"sample_report.pdf"),pagesize=letter).build(story)
    return {"revenue":revenue,"gross_profit":gp,"gross_margin":margin,"products":len(prod),"price_observations":len(prices),"competitor_observations":len(comps),"sales_rows":len(sales),"high_priority_products":high}
if __name__=="__main__": print(generate())
