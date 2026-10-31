# Data dictionary

- `products`: one row per synthetic product; `unit_cost` is the product master reference cost.
- `price_observations`: one row per product/date/region/channel with our observed price, list price and discount.
- `competitors`: one row per synthetic competitor entity.
- `competitor_prices`: one row per product/date/competitor/region/channel; missing competitor observations are omitted, not zero.
- `sales_demand`: one row per product/date/region/channel simulated demand outcome; quantity is constrained by simulated inventory.
- `inventory`: one row per product/date with available units and stockout flag.
- `promotions`: one row per generated product promotion window.
- `date_dimension`: one row per date.

All data is synthetic. Currency is an abstract illustrative unit. Gross profit excludes shipping, taxes, returns, advertising and operating expenses.
