"""Generate reproducible synthetic pricing, competitor, demand and inventory data."""
from pathlib import Path
import numpy as np
import pandas as pd
import json

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
SEED = 20261028

def generate():
    rng = np.random.default_rng(SEED)
    RAW.mkdir(parents=True, exist_ok=True)
    PROC.mkdir(parents=True, exist_ok=True)
    dates = pd.date_range("2025-01-01", "2026-06-30", freq="D")
    categories = ["Home", "Electronics", "Beauty", "Sports", "Books", "Toys", "Apparel", "Kitchen", "Garden", "Pet Care"]
    subcats = {"Home":["Storage","Decor","Lighting"],"Electronics":["Audio","Accessories","Smart Home"],
               "Beauty":["Skincare","Haircare","Personal Care"],"Sports":["Fitness","Outdoor","Training"],
               "Books":["Fiction","Business","Education"],"Toys":["Learning","Games","Outdoor"],
               "Apparel":["Basics","Activewear","Outerwear"],"Kitchen":["Cookware","Tools","Appliances"],
               "Garden":["Tools","Planters","Outdoor"],"Pet Care":["Food","Toys","Grooming"]}
    products=[]
    for i in range(1,181):
        cat=categories[(i-1)%len(categories)]
        base=float(np.exp(rng.uniform(np.log(8),np.log(420))))
        cost=round(base*rng.uniform(.42,.76),2)
        products.append({"product_id":f"P{i:04d}","product_name":f"{cat} Product {i:03d}","category":cat,
            "subcategory":rng.choice(subcats[cat]),"brand":f"Brand {(i-1)%18+1:02d}","unit_cost":cost,
            "launch_date":pd.Timestamp("2024-01-01")+pd.Timedelta(days=int(rng.integers(0,300))),
            "product_status":"Active" if rng.random()>.04 else "Discontinued",
            "base_price":round(base,2),"elasticity":float(rng.uniform(-2.0,-.25))})
    products=pd.DataFrame(products)
    competitors=pd.DataFrame([{"competitor_id":f"C{i}","competitor_name":n,"competitor_type":t}
        for i,(n,t) in enumerate([("MarketPlace A","Marketplace"),("Value Retailer","Discount Retail"),("Premium Shop","Specialist")],1)])
    regions=["North","South","East","West","Central"]
    channels=["Online","Marketplace","Retail"]
    price_rows=[]; comp_rows=[]; sales_rows=[]; inv_rows=[]; promos=[]
    obs_id=0; sale_id=0; inv_id=0; promo_id=0
    for p in products.itertuples(index=False):
        price= p.base_price
        prev_price=None
        promo_days=set()
        # periodic promotional windows, generated per product
        if int(p.product_id[1:])%4==0:
            start=int(rng.integers(20,len(dates)-30))
            for d in range(start,min(start+7,len(dates))): promo_days.add(d)
            promo_id+=1
            promos.append({"promotion_id":f"PR{promo_id:04d}","product_id":p.product_id,
                "start_date":dates[start],"end_date":dates[min(start+6,len(dates)-1)],
                "promotion_type":"Seasonal campaign","promotion_discount_pct":round(float(rng.choice([.05,.10,.15,.20])),3)})
        region=rng.choice(regions); channel=rng.choice(channels)
        for di,date in enumerate(dates):
            season=1 + .13*np.sin(2*np.pi*(date.dayofyear/365.25)) + (.12 if date.month in [11,12] else 0)
            if rng.random()<.025:
                price *= float(rng.choice([.94,.97,1.03,1.06]))
            price=max(1,price)
            list_price=round(p.base_price*float(1+.02*np.sin(di/45)),2)
            discount=float(rng.choice([0,.03,.05,.08,.10,.15,.20,.25],p=[.22,.10,.16,.13,.15,.12,.08,.04]))
            if di in promo_days: discount=max(discount,.15)
            our_price=round(list_price*(1-discount),2)
            # competitor prices use shared market position with independent small movements
            obs_id+=1
            price_rows.append({"observation_id":obs_id,"observation_date":date,"product_id":p.product_id,
                "our_price":our_price,"list_price":list_price,"discount_pct":round((list_price-our_price)/list_price,4),
                "region_id":region,"channel_id":channel})
            for ci,comp in enumerate(competitors.itertuples(index=False),1):
                if rng.random()<.025: # missing competitor observation is omitted, never encoded as zero
                    continue
                comp_mult=[.97, .91, 1.08][ci-1]
                cp=round(max(.5, p.base_price*comp_mult*(1+.018*np.sin(di/32+ci)+rng.normal(0,.012))),2)
                comp_rows.append({"competitor_observation_id":len(comp_rows)+1,"observation_date":date,
                    "product_id":p.product_id,"competitor_id":comp.competitor_id,"competitor_price":cp,
                    "region_id":region,"channel_id":channel})
            # demand responds to price vs base and seasonal/promo factors; noise is deliberate
            unit_cost=round(p.unit_cost*(1+.025*np.sin(di/90)+rng.normal(0,.003)),2)
            price_ratio=max(.2,our_price/p.base_price)
            demand_mean=max(.2, (12*(p.base_price/55)**.35) * (price_ratio**p.elasticity) * season *
                            (1.12 if di in promo_days else 1) * (1.08 if date.weekday()>=5 else 1))
            qty=int(rng.poisson(min(demand_mean,80)))
            # occasional stockout makes observed demand censored
            available=int(rng.integers(0,40)) if rng.random()<.018 else int(rng.integers(40,180))
            stockout=available<=qty
            sold=min(qty,available)
            sale_id+=1
            sales_rows.append({"sales_id":sale_id,"sale_date":date,"product_id":p.product_id,
                "quantity_sold":sold,"realized_unit_price":our_price,"unit_cost":unit_cost,
                "revenue":round(sold*our_price,2),"gross_profit":round(sold*(our_price-unit_cost),2),
                "region_id":region,"channel_id":channel,"stockout_flag":bool(stockout),
                "promotion_flag":bool(di in promo_days)})
            inv_id+=1
            inv_rows.append({"inventory_id":inv_id,"observation_date":date,"product_id":p.product_id,
                "available_units":available,"stockout_flag":bool(stockout)})
    # Save source tables
    products.drop(columns=["base_price","elasticity"]).to_csv(RAW/"products.csv",index=False)
    competitors.to_csv(RAW/"competitors.csv",index=False)
    pd.DataFrame(price_rows).to_csv(RAW/"price_observations.csv",index=False)
    pd.DataFrame(comp_rows).to_csv(RAW/"competitor_prices.csv",index=False)
    pd.DataFrame(sales_rows).to_csv(RAW/"sales_demand.csv",index=False)
    pd.DataFrame(inv_rows).to_csv(RAW/"inventory.csv",index=False)
    pd.DataFrame(promos,columns=["promotion_id","product_id","start_date","end_date","promotion_type","promotion_discount_pct"]).to_csv(RAW/"promotions.csv",index=False)
    # Intentional imperfections in raw price observations for the cleaning pipeline to quarantine
    raw=pd.DataFrame(price_rows)
    bad=raw.sample(8,random_state=SEED).copy()
    bad["observation_id"]=[int(raw.observation_id.max())+i+1 for i in range(len(bad))]
    bad.loc[bad.index[0],"our_price"]=-10
    bad.loc[bad.index[1],"discount_pct"]=1.5
    bad.loc[bad.index[2],"product_id"]="P9999"
    bad.loc[bad.index[3],"observation_date"]="not-a-date"
    bad.loc[bad.index[4],"list_price"]=0
    bad.loc[bad.index[5],"our_price"]=np.nan
    bad.loc[bad.index[6],"observation_id"]=int(raw.observation_id.iloc[0])
    bad.loc[bad.index[7],"discount_pct"]=-.2
    pd.concat([raw,bad],ignore_index=True).to_csv(RAW/"price_observations.csv",index=False)
    # Dates dimension
    d=pd.DataFrame({"date":dates})
    d["year"]=d.date.dt.year; d["quarter"]="Q"+d.date.dt.quarter.astype(str)
    d["month"]=d.date.dt.month; d["month_name"]=d.date.dt.month_name()
    d["week"]=d.date.dt.isocalendar().week.astype(int); d["day_of_week"]=d.date.dt.day_name()
    d["is_weekend"]=d.date.dt.dayofweek>=5
    d["seasonal_period"]=np.select([d.date.dt.month.isin([12,1,2]),d.date.dt.month.isin([3,4,5]),
        d.date.dt.month.isin([6,7,8])],["Winter","Spring","Summer"],default="Autumn")
    d.to_csv(PROC/"date_dimension.csv",index=False)
    return {"products":len(products),"dates":len(dates),"price_rows":len(price_rows),"competitor_rows":len(comp_rows),
            "sales_rows":len(sales_rows),"seed":SEED}

if __name__=="__main__":
    print(generate())
