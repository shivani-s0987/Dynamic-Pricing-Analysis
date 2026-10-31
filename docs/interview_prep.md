# Interview preparation

## 60–90 second pitch
I built a reproducible Dynamic Pricing Analysis and Revenue Intelligence project using Python, SQL and Streamlit. It generates 18 months of synthetic daily price and demand observations for 180 products, three synthetic competitors and ten categories. I implemented cleaning and quarantine rules, calculated price changes and volatility, benchmarked prices against the median of comparable competitor observations, and analyzed revenue, gross profit and price-demand associations. The Streamlit app has six pages, including competitor benchmarking, transparent pricing review flags and a what-if simulator. I also wrote analytical SQL using window functions and CTEs, generated CSV/Markdown/PDF reports, and added tests for metric and scenario correctness. The data is synthetic, so I present findings as demonstrations and hypotheses—not real market intelligence or proven causal improvements.

## Fifteen likely questions and answers

1. **How do you calculate price change?** `(current price - prior comparable price) / prior comparable price`; zero or missing prior prices are undefined, not zero.
2. **How is price volatility defined?** Sample standard deviation of daily percentage price changes per product, with a minimum of ten observed changes.
3. **Why use the median competitor price?** It is less sensitive to an unusually high or low competitor observation than the mean.
4. **How is relative price index interpreted?** `100 × our price / competitor median`; above 100 is above benchmark and below 100 is below benchmark.
5. **How do you handle missing competitor data?** Keep it missing, report coverage and competitor count, and never treat it as a zero price.
6. **What does Pandas add?** Repeatable cleaning, grouped summaries, joins, time-series calculations and data-quality reporting.
7. **Which SQL window functions are useful here?** `LAG` for prior price, `ROW_NUMBER` for ranking, and rolling `AVG` for moving trends.
8. **What is a CTE?** A named temporary result within a query that makes multi-stage analytical logic easier to read and maintain.
9. **How do you calculate gross profit?** Revenue minus cost of goods sold; it is not net profit because operating expenses, returns, shipping and taxes are excluded.
10. **Does price-demand correlation prove elasticity?** No. Correlation is descriptive and may be confounded by seasonality, promotions, stockouts and product mix.
11. **What would a credible elasticity model need?** Enough price variation, controls for product and time, promotions and availability, diagnostic checks, and ideally quasi-experimental or randomized price variation.
12. **Why Streamlit?** It lets an analyst expose filters, charts, tables and scenario controls quickly without a separate front-end application.
13. **How does the scenario simulator work?** It changes price, demand and unit cost by explicit user assumptions, then recalculates revenue and gross profit using consistent equations.
14. **How do you avoid false pricing recommendations?** Use transparent thresholds, evidence-quality labels, benchmark coverage and margin context; treat flags as review hypotheses rather than automatic price instructions.
15. **What would you improve next?** Load lawful licensed competitor data, model product/time controls, add a validated elasticity study, test pricing experiments, and operationalize PostgreSQL refreshes.

## Recruiter walkthrough
1. Inspect `src/generate_data.py` and `src/clean_data.py`.
2. Read `docs/metric_definitions.md` and `sql/04_pricing_analysis.sql`.
3. Run `python -m src.report_generator` and inspect the generated reports.
4. Launch Streamlit, filter category and date, explore benchmark coverage, export opportunity results, and change scenario assumptions.
5. Review tests and limitations before discussing findings.
