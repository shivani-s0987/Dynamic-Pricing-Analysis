"""Database helpers. SQLite is the portable default; PostgreSQL uses DATABASE_URL."""
import os
from sqlalchemy import create_engine
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def get_engine():
    url=os.getenv("DATABASE_URL","sqlite:///"+str(ROOT/"data/processed/dynamic_pricing.sqlite"))
    return create_engine(url,future=True)
