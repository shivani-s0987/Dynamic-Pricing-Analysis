from pathlib import Path
import pandas as pd
from .database import get_engine
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"data/processed"
TABLES={"products":"products_clean.csv","competitors":"competitors_clean.csv",
"price_observations":"price_observations_clean.csv","competitor_prices":"competitor_prices_clean.csv",
"sales_demand":"sales_demand_clean.csv","inventory":"inventory_clean.csv","promotions":"promotions_clean.csv"}
def load():
    engine=get_engine()
    with engine.begin() as con:
        for table,file in TABLES.items():
            df=pd.read_csv(P/file)
            df.to_sql(table,con,if_exists="replace",index=False,chunksize=5000)
    return {t:len(pd.read_csv(P/f)) for t,f in TABLES.items()}
if __name__=="__main__": print(load())
