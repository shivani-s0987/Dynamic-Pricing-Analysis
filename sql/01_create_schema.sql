-- PostgreSQL schema. Grain: one product/day/region/channel price observation; one daily demand observation.
CREATE TABLE IF NOT EXISTS products (
 product_id TEXT PRIMARY KEY, product_name TEXT NOT NULL, category TEXT NOT NULL,
 subcategory TEXT NOT NULL, brand TEXT NOT NULL, unit_cost NUMERIC(12,2) NOT NULL CHECK(unit_cost>=0),
 launch_date DATE, product_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS competitors (
 competitor_id TEXT PRIMARY KEY, competitor_name TEXT NOT NULL, competitor_type TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS price_observations (
 observation_id BIGINT PRIMARY KEY, observation_date DATE NOT NULL, product_id TEXT NOT NULL REFERENCES products(product_id),
 our_price NUMERIC(12,2) NOT NULL CHECK(our_price>0), list_price NUMERIC(12,2) NOT NULL CHECK(list_price>0),
 discount_pct NUMERIC(6,4) NOT NULL CHECK(discount_pct BETWEEN 0 AND 1),
 region_id TEXT NOT NULL, channel_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS competitor_prices (
 competitor_observation_id BIGINT PRIMARY KEY, observation_date DATE NOT NULL,
 product_id TEXT NOT NULL REFERENCES products(product_id), competitor_id TEXT NOT NULL REFERENCES competitors(competitor_id),
 competitor_price NUMERIC(12,2) NOT NULL CHECK(competitor_price>0), region_id TEXT NOT NULL, channel_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sales_demand (
 sales_id BIGINT PRIMARY KEY, sale_date DATE NOT NULL, product_id TEXT NOT NULL REFERENCES products(product_id),
 quantity_sold INTEGER NOT NULL CHECK(quantity_sold>=0), realized_unit_price NUMERIC(12,2) NOT NULL CHECK(realized_unit_price>0),
 unit_cost NUMERIC(12,2) NOT NULL CHECK(unit_cost>=0), revenue NUMERIC(14,2) NOT NULL,
 gross_profit NUMERIC(14,2) NOT NULL, region_id TEXT NOT NULL, channel_id TEXT NOT NULL,
 stockout_flag BOOLEAN NOT NULL, promotion_flag BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS inventory (
 inventory_id BIGINT PRIMARY KEY, observation_date DATE NOT NULL, product_id TEXT NOT NULL REFERENCES products(product_id),
 available_units INTEGER NOT NULL CHECK(available_units>=0), stockout_flag BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS promotions (
 promotion_id TEXT PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products(product_id),
 start_date DATE NOT NULL, end_date DATE NOT NULL, promotion_type TEXT NOT NULL,
 promotion_discount_pct NUMERIC(6,4) NOT NULL CHECK(promotion_discount_pct BETWEEN 0 AND 1),
 CHECK(end_date>=start_date)
);
CREATE INDEX IF NOT EXISTS ix_price_product_date ON price_observations(product_id,observation_date);
CREATE INDEX IF NOT EXISTS ix_comp_product_date ON competitor_prices(product_id,observation_date);
CREATE INDEX IF NOT EXISTS ix_sales_product_date ON sales_demand(product_id,sale_date);
CREATE INDEX IF NOT EXISTS ix_sales_date ON sales_demand(sale_date);
