-- Product-level Pearson correlation is calculated in Python; this SQL gives comparable descriptive statistics.
SELECT product_id,COUNT(*) n,STDDEV_SAMP(realized_unit_price) price_sd,STDDEV_SAMP(quantity_sold) units_sd,
 CORR(realized_unit_price,quantity_sold) price_units_correlation
FROM sales_demand GROUP BY product_id HAVING COUNT(*)>=30 AND STDDEV_SAMP(realized_unit_price)>0;
-- Correlation is not causal; seasonality, promotions, stockouts and unobserved factors may confound.
