-- Load CSVs with psql \copy from repository root after schema creation.
\copy products FROM 'data/processed/products_clean.csv' WITH (FORMAT csv, HEADER true);
\copy competitors FROM 'data/processed/competitors_clean.csv' WITH (FORMAT csv, HEADER true);
\copy price_observations FROM 'data/processed/price_observations_clean.csv' WITH (FORMAT csv, HEADER true);
\copy competitor_prices FROM 'data/processed/competitor_prices_clean.csv' WITH (FORMAT csv, HEADER true);
\copy sales_demand FROM 'data/processed/sales_demand_clean.csv' WITH (FORMAT csv, HEADER true);
\copy inventory FROM 'data/processed/inventory_clean.csv' WITH (FORMAT csv, HEADER true);
\copy promotions FROM 'data/processed/promotions_clean.csv' WITH (FORMAT csv, HEADER true);
