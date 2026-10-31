-- Reconciliation and referential checks: every query should return zero exception rows/counts.
SELECT COUNT(*) AS invalid_price_rows FROM price_observations WHERE our_price<=0 OR list_price<=0 OR discount_pct NOT BETWEEN 0 AND 1;
SELECT COUNT(*) AS unknown_products FROM price_observations p LEFT JOIN products d USING(product_id) WHERE d.product_id IS NULL;
SELECT COUNT(*) AS revenue_mismatches FROM sales_demand WHERE ABS(revenue-realized_unit_price*quantity_sold)>0.02;
SELECT COUNT(*) AS gross_profit_mismatches FROM sales_demand WHERE ABS(gross_profit-(revenue-unit_cost*quantity_sold))>0.02;
SELECT COUNT(*) AS invalid_competitor_prices FROM competitor_prices WHERE competitor_price<=0;
