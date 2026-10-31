CREATE OR REPLACE VIEW vw_product_profitability AS
SELECT p.product_id,d.product_name,d.category,SUM(p.revenue) revenue,SUM(p.gross_profit) gross_profit,
 SUM(p.gross_profit)/NULLIF(SUM(p.revenue),0) gross_margin,SUM(p.quantity_sold) units_sold
FROM sales_demand p JOIN products d USING(product_id) GROUP BY 1,2,3;

CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT DATE_TRUNC('month',sale_date)::date month,SUM(revenue) revenue,SUM(gross_profit) gross_profit,
 SUM(quantity_sold) units,SUM(gross_profit)/NULLIF(SUM(revenue),0) gross_margin
FROM sales_demand GROUP BY 1;
