# Assumptions and limitations

1. All products, prices, competitor observations, demand, sales and inventory are synthetic.
2. Currency is an abstract unit; no real company or market is represented.
3. Daily quantity is simulated and censored by simulated available inventory.
4. Competitor benchmark is the median of available observations matched by product/date/region/channel. No benchmark is treated as zero when missing.
5. A competitor price index above 100 means our price is above the matched median benchmark; below 100 means below.
6. Observational associations do not establish price elasticity or causal effects. Promotions, seasonality, stockouts and other generated factors confound relationships.
7. Gross profit excludes shipping, returns, taxes, advertising and operating expenses.
8. Price review rules are screening rules, not automatic pricing instructions. Verify comparability, strategic position, data coverage and demand before changes.
9. PostgreSQL SQL is supplied but must be executed on a configured PostgreSQL server; SQLite is the local demo fallback.
