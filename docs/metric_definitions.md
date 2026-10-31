# Metric definitions

- Average selling price = sum(revenue) / sum(units sold).
- Price change % = (current observed price - previous observed price) / previous observed price, per product ordered by date.
- Absolute price change = current price - previous comparable price.
- Price volatility = sample standard deviation of per-product daily price change percentages; minimum 10 changes.
- Competitor gap = our price - median available comparable competitor price.
- Competitor gap % = (our price - median benchmark) / median benchmark.
- Relative price index = 100 × our price / median benchmark.
- Discount % = (list price - realized selling price) / list price; valid positive list price required.
- Revenue = realized unit price × quantity sold.
- COGS = unit cost × quantity sold.
- Gross profit = revenue - COGS.
- Gross margin % = gross profit / revenue.
- Demand change % = change in comparable average units relative to prior period.
- Price-demand relationship = product-level Pearson correlation for product groups with sufficient observations and price variation; descriptive only.

Safe division returns null/NaN for zero denominators. Gross profit excludes shipping, returns, taxes, advertising and operating expenses.
