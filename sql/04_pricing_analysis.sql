-- 1. Price movement by product with LAG; positive change = increase.
WITH x AS (
 SELECT product_id,observation_date,our_price,LAG(our_price) OVER(PARTITION BY product_id ORDER BY observation_date) previous_price
 FROM price_observations
)
SELECT *,our_price-previous_price absolute_change,(our_price-previous_price)/NULLIF(previous_price,0) change_pct
FROM x WHERE previous_price IS NOT NULL ORDER BY ABS(our_price-previous_price) DESC;

-- 2. Volatility by product; sample standard deviation of daily percent changes.
WITH x AS (
 SELECT product_id,(our_price-LAG(our_price) OVER(PARTITION BY product_id ORDER BY observation_date))
 / NULLIF(LAG(our_price) OVER(PARTITION BY product_id ORDER BY observation_date),0) AS change_pct
 FROM price_observations
)
SELECT product_id,COUNT(change_pct) n_changes,STDDEV_SAMP(change_pct) price_volatility
FROM x GROUP BY product_id HAVING COUNT(change_pct)>=10 ORDER BY price_volatility DESC;

-- 3. Category price range and median-like percentile.
SELECT d.category,AVG(p.our_price) avg_price,MIN(p.our_price) min_price,
 MAX(p.our_price) max_price,PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY p.our_price) median_price
FROM price_observations p JOIN products d USING(product_id) GROUP BY d.category ORDER BY avg_price DESC;

-- 4. Monthly revenue and gross profit.
SELECT DATE_TRUNC('month',sale_date)::date month,SUM(revenue) revenue,SUM(gross_profit) gross_profit,
 SUM(gross_profit)/NULLIF(SUM(revenue),0) gross_margin
FROM sales_demand GROUP BY 1 ORDER BY 1;

-- 5. Month-over-month revenue growth.
WITH m AS (SELECT DATE_TRUNC('month',sale_date)::date month,SUM(revenue) revenue FROM sales_demand GROUP BY 1)
SELECT month,revenue,LAG(revenue) OVER(ORDER BY month) prior_month,
 (revenue-LAG(revenue) OVER(ORDER BY month))/NULLIF(LAG(revenue) OVER(ORDER BY month),0) mom_growth
FROM m ORDER BY month;

-- 6. Category rank by revenue and gross profit.
WITH c AS (SELECT d.category,SUM(s.revenue) revenue,SUM(s.gross_profit) gp FROM sales_demand s JOIN products d USING(product_id) GROUP BY 1)
SELECT *,RANK() OVER(ORDER BY revenue DESC) revenue_rank,RANK() OVER(ORDER BY gp DESC) profit_rank FROM c;

-- 7. Top/bottom products by revenue.
SELECT p.product_id,d.product_name,d.category,SUM(p.revenue) revenue,SUM(p.gross_profit) gp,
 SUM(p.gross_profit)/NULLIF(SUM(p.revenue),0) margin
FROM sales_demand p JOIN products d USING(product_id) GROUP BY 1,2,3 ORDER BY revenue DESC;

-- 8. Products with weak margin and meaningful revenue.
SELECT product_id,SUM(revenue) revenue,SUM(gross_profit) gp,SUM(gross_profit)/NULLIF(SUM(revenue),0) margin
FROM sales_demand GROUP BY product_id HAVING SUM(revenue)>1000 AND SUM(gross_profit)/NULLIF(SUM(revenue),0)<.12;

-- 9. Rolling 7-day revenue.
WITH d AS (SELECT sale_date,SUM(revenue) revenue FROM sales_demand GROUP BY sale_date)
SELECT sale_date,revenue,AVG(revenue) OVER(ORDER BY sale_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) rolling_7d_avg
FROM d ORDER BY sale_date;

-- 10. Product rank within category.
WITH p AS (SELECT d.category,s.product_id,SUM(s.revenue) revenue FROM sales_demand s JOIN products d USING(product_id) GROUP BY 1,2)
SELECT *,ROW_NUMBER() OVER(PARTITION BY category ORDER BY revenue DESC) category_rank FROM p;

-- 11. Discount band sales performance (discount derived from list/realized price).
WITH x AS (SELECT s.*,GREATEST(0,(p.list_price-s.realized_unit_price)/NULLIF(p.list_price,0)) discount
 FROM sales_demand s JOIN price_observations p ON p.product_id=s.product_id AND p.observation_date=s.sale_date)
SELECT CASE WHEN discount=0 THEN '0%' WHEN discount<=.05 THEN '0-5%' WHEN discount<=.10 THEN '5-10%'
 WHEN discount<=.20 THEN '10-20%' WHEN discount<=.30 THEN '20-30%' ELSE '>30%' END discount_band,
 SUM(revenue) revenue,SUM(gross_profit) gross_profit,SUM(gross_profit)/NULLIF(SUM(revenue),0) margin
FROM x GROUP BY 1 ORDER BY 1;

-- 12. Price and demand coincident changes, descriptive only.
WITH x AS (SELECT product_id,sale_date,realized_unit_price,quantity_sold,
 LAG(realized_unit_price) OVER(PARTITION BY product_id ORDER BY sale_date) prior_price,
 LAG(quantity_sold) OVER(PARTITION BY product_id ORDER BY sale_date) prior_qty FROM sales_demand)
SELECT product_id,sale_date,(realized_unit_price-prior_price)/NULLIF(prior_price,0) price_change_pct,
 (quantity_sold-prior_qty)/NULLIF(prior_qty,0) demand_change_pct
FROM x WHERE prior_price IS NOT NULL AND ABS(realized_unit_price-prior_price)/NULLIF(prior_price,0)>.03;

-- 13. Competitor benchmark median and coverage.
WITH b AS (SELECT observation_date,product_id,region_id,channel_id,COUNT(*) competitors,
 PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY competitor_price) median_comp_price
 FROM competitor_prices GROUP BY 1,2,3,4)
SELECT p.product_id,p.observation_date,p.our_price,b.median_comp_price,b.competitors,
 (p.our_price-b.median_comp_price)/NULLIF(b.median_comp_price,0) gap_pct,
 100*p.our_price/NULLIF(b.median_comp_price,0) price_index
FROM price_observations p LEFT JOIN b USING(observation_date,product_id,region_id,channel_id);

-- 14. Products consistently above benchmark (at least 20 matched dates).
WITH b AS (SELECT observation_date,product_id,region_id,channel_id,PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY competitor_price) med
 FROM competitor_prices GROUP BY 1,2,3,4), x AS (
 SELECT p.product_id,p.our_price/b.med price_index FROM price_observations p JOIN b USING(observation_date,product_id,region_id,channel_id))
SELECT product_id,COUNT(*) matched_dates,AVG(price_index) avg_index FROM x GROUP BY 1
HAVING COUNT(*)>=20 AND AVG(price_index)>1.10 ORDER BY avg_index DESC;

-- 15. Products below competitor benchmark.
WITH b AS (SELECT observation_date,product_id,region_id,channel_id,PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY competitor_price) med
 FROM competitor_prices GROUP BY 1,2,3,4)
SELECT p.product_id,AVG(p.our_price/b.med) avg_price_index FROM price_observations p JOIN b USING(observation_date,product_id,region_id,channel_id)
GROUP BY p.product_id HAVING AVG(p.our_price/b.med)<.90 ORDER BY avg_price_index;

-- 16. Price gap by category.
WITH b AS (SELECT observation_date,product_id,region_id,channel_id,PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY competitor_price) med
 FROM competitor_prices GROUP BY 1,2,3,4)
SELECT d.category,AVG((p.our_price-b.med)/NULLIF(b.med,0)) avg_gap_pct,COUNT(*) matched_observations
FROM price_observations p JOIN b USING(observation_date,product_id,region_id,channel_id) JOIN products d USING(product_id)
GROUP BY d.category ORDER BY avg_gap_pct DESC;

-- 17. Demand trends and stockout share.
SELECT product_id,AVG(quantity_sold) avg_units,AVG(stockout_flag::int) stockout_share,
 SUM(revenue) revenue FROM sales_demand GROUP BY product_id ORDER BY stockout_share DESC;

-- 18. Promotion vs non-promotion descriptive comparison.
SELECT promotion_flag,COUNT(*) days,SUM(quantity_sold) units,AVG(quantity_sold) avg_units,
 SUM(revenue) revenue,SUM(gross_profit) gp,SUM(gross_profit)/NULLIF(SUM(revenue),0) margin
FROM sales_demand GROUP BY promotion_flag;

-- 19. Seasonal performance by quarter/month.
SELECT EXTRACT(MONTH FROM sale_date) month,SUM(revenue) revenue,SUM(quantity_sold) units,
 SUM(gross_profit)/NULLIF(SUM(revenue),0) margin FROM sales_demand GROUP BY 1 ORDER BY 1;

-- 20. Large one-day price changes for investigation.
WITH x AS (SELECT *,LAG(our_price) OVER(PARTITION BY product_id ORDER BY observation_date) prev
 FROM price_observations)
SELECT product_id,observation_date,prev,our_price,(our_price-prev)/NULLIF(prev,0) change_pct
FROM x WHERE prev IS NOT NULL AND ABS((our_price-prev)/NULLIF(prev,0))>.10 ORDER BY ABS((our_price-prev)/prev) DESC;

-- 21. Price below unit cost: join daily price and cost observations.
SELECT p.product_id,p.observation_date,p.our_price,s.unit_cost
FROM price_observations p JOIN sales_demand s ON s.product_id=p.product_id AND s.sale_date=p.observation_date
WHERE p.our_price<s.unit_cost;

-- 22. Gross margin trend by channel.
SELECT channel_id,DATE_TRUNC('month',sale_date)::date month,SUM(revenue) revenue,SUM(gross_profit) gp,
 SUM(gross_profit)/NULLIF(SUM(revenue),0) margin FROM sales_demand GROUP BY 1,2 ORDER BY 2,1;

-- 23. Revenue contribution and running total by product.
WITH p AS (SELECT product_id,SUM(revenue) revenue FROM sales_demand GROUP BY 1)
SELECT product_id,revenue,revenue/NULLIF(SUM(revenue) OVER(),0) revenue_share,
 SUM(revenue) OVER(ORDER BY revenue DESC ROWS UNBOUNDED PRECEDING) running_revenue FROM p ORDER BY revenue DESC;

-- 24. Price change moving average by product.
WITH x AS (SELECT product_id,observation_date,our_price,
 AVG(our_price) OVER(PARTITION BY product_id ORDER BY observation_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) ma7
 FROM price_observations)
SELECT * FROM x ORDER BY product_id,observation_date;
