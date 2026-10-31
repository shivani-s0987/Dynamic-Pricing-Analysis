"""Clean and validate source extracts; invalid price observations are quarantined with reasons."""
from pathlib import Path
import pandas as pd, json, logging
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/"data/raw"; PROC=ROOT/"data/processed"
logging.basicConfig(level=logging.INFO,format="%(levelname)s %(message)s")
REQUIRED={"observation_id","observation_date","product_id","our_price","list_price","discount_pct","region_id","channel_id"}

def clean():
    PROC.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(RAW/"price_observations.csv")
    missing_cols=REQUIRED-set(raw.columns)
    if missing_cols: raise ValueError(f"Missing required columns: {sorted(missing_cols)}")
    products=pd.read_csv(RAW/"products.csv")
    raw["observation_date"]=pd.to_datetime(raw["observation_date"],errors="coerce")
    for c in ["observation_id","our_price","list_price","discount_pct"]: raw[c]=pd.to_numeric(raw[c],errors="coerce")
    raw["product_id"]=raw["product_id"].astype(str).str.strip().str.upper()
    reasons=[]
    valid_products=set(products.product_id)
    for ix,r in raw.iterrows():
        why=[]
        if pd.isna(r.observation_id): why.append("missing_observation_id")
        if pd.isna(r.observation_date): why.append("invalid_observation_date")
        if r.product_id not in valid_products: why.append("unknown_product")
        if pd.isna(r.our_price) or r.our_price<=0: why.append("invalid_our_price")
        if pd.isna(r.list_price) or r.list_price<=0: why.append("invalid_list_price")
        if pd.isna(r.discount_pct) or not 0<=r.discount_pct<=1: why.append("invalid_discount_pct")
        elif pd.notna(r.our_price) and pd.notna(r.list_price) and r.list_price>0:
            actual=(r.list_price-r.our_price)/r.list_price
            if abs(actual-r.discount_pct)>.035: why.append("discount_reconciliation_mismatch")
        reasons.append(";".join(why))
    raw["validation_reasons"]=reasons
    duplicate_ids=raw.duplicated("observation_id",keep="first")
    raw.loc[duplicate_ids & raw.validation_reasons.eq(""),"validation_reasons"]="duplicate_observation_id"
    bad=raw[raw.validation_reasons.ne("")].copy()
    good=raw[raw.validation_reasons.eq("")].drop(columns=["validation_reasons"]).copy()
    good["observation_id"]=good.observation_id.astype("int64")
    good["our_price"]=good.our_price.round(2); good["list_price"]=good.list_price.round(2)
    good["discount_pct"]=good.discount_pct.round(4)
    good.to_csv(PROC/"price_observations_clean.csv",index=False)
    bad.to_csv(PROC/"price_observations_quarantined.csv",index=False)
    # Copy clean dimension/fact tables, validating schemas and product FKs
    for name in ["products","competitors","competitor_prices","sales_demand","inventory","promotions"]:
        df=pd.read_csv(RAW/f"{name}.csv")
        if "product_id" in df.columns:
            unknown=~df.product_id.isin(valid_products)
            if unknown.any(): raise ValueError(f"{name}: unknown product foreign keys")
        df.to_csv(PROC/f"{name}_clean.csv",index=False)
    report={"raw_price_observations":int(len(raw)),"clean_price_observations":int(len(good)),
        "quarantined_price_observations":int(len(bad)),"duplicate_ids":int(raw.duplicated("observation_id").sum()),
        "quarantine_reasons":bad.validation_reasons.value_counts().to_dict(),
        "missing_values_raw":raw.isna().sum().to_dict(),"status":"PASS" if len(bad)>0 and len(good)>0 else "REVIEW"}
    (PROC/"data_quality_report.json").write_text(json.dumps(report,indent=2,default=str))
    logging.info("Cleaned %s observations; quarantined %s",len(good),len(bad))
    return report
if __name__=="__main__": print(json.dumps(clean(),indent=2))
