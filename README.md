# Dynamic Pricing Analysis & Revenue Intelligence

A reproducible, synthetic retail pricing analytics project using Python, SQL, and Streamlit. It explores price trends, volatility, competitor benchmarking, simulated demand, revenue, gross profit, pricing review flags, and user-entered what-if scenarios.

> **Synthetic-data disclaimer:** Products, prices, competitors, demand, inventory and revenue are generated data. This repository is a portfolio demonstration, not actual market intelligence or evidence of causal revenue improvement.

## Features
- Fixed-seed dataset generator: 180 products, 10 categories, 18 months of daily product observations.
- Cleaning pipeline with explicit quarantined rows and JSON data-quality report.
- Python pricing metrics, median competitor benchmark, volatility, demand association, and scenario simulator.
- 24 commented PostgreSQL analytical queries plus schema, load script, data-quality checks and views.
- Streamlit dashboard: executive overview, trends/volatility, competitor benchmarking, revenue/demand, pricing opportunities, what-if simulator.
- CSV, Markdown, chart and PDF report generation.
- pytest coverage for core metrics, cleaning, scenario calculations and optional SQLite reconciliation.

## Architecture
See [docs/architecture.md](docs/architecture.md). The pipeline is generator → raw CSV → cleaner/quarantine → processed CSV → Python metrics/SQL/Streamlit → reports.

## Quick start (Windows PowerShell)
Use Python 3.11 or 3.12. From repository root:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.generate_data
python -m src.clean_data
python -m src.validate_data
python -m src.load_data
python -m src.report_generator
python -m pytest -q
streamlit run app/streamlit_app.py
```
The SQLite database is created at `data/processed/dynamic_pricing.sqlite` by default. To use PostgreSQL, set `DATABASE_URL` to a SQLAlchemy PostgreSQL URL, create the database, run `sql/01_create_schema.sql`, and load the CSVs using `psql` and `sql/02_load_data.sql`. Do not use `sql/02_load_data.sql` before the schema exists.

## SQL coverage
24 analytical queries cover price changes and volatility, category comparisons, monthly growth, product ranking, discount bands, price-demand co-movement, competitor median/index/coverage, product above/below benchmark, inventory/stockout context, promotion comparisons, seasonal trends, under-cost price checks, revenue contribution, moving averages and channel margins.

## Metrics
See [docs/metric_definitions.md](docs/metric_definitions.md). Safe division is used; competitor prices are benchmarked using a median over available matched observations. Gross profit excludes shipping, returns, taxes, advertising and operating expenses.

## Reports
Run `python -m src.eda` for 14 generated PNG visualizations and `python -m src.report_generator`. It writes category/monthly/benchmark CSVs and charts under `outputs/`, plus `reports/executive_summary.md`, `reports/pricing_opportunities.csv`, and `reports/sample_report.pdf`.

## Dashboard
Launch with `streamlit run app/streamlit_app.py`. Use sidebar category and date filters. Scenario demand response is an explicit user assumption, not a validated elasticity estimate. The opportunity rules are screening flags, not automatic price recommendations.

## Testing
Run `python -m pytest -q`. For SQL reconciliation, run `python -m src.load_data` before tests. PostgreSQL-specific SQL is supplied for execution against PostgreSQL; the default portable app uses SQLite.

## Limitations and future work
Synthetic records are not real competitor observations. Demand is simulated and stockouts censor quantity. Correlation is not causation. Future work could incorporate lawful licensed market data, product-specific time controls, validated elasticity models, a production PostgreSQL instance, authentication, and experiment measurement.

## Recruiter walkthrough
1. Inspect the reproducible generator and quarantine report.
2. Review metric definitions and SQL window-function queries.
3. Run the report generator and inspect CSV/PDF findings.
4. Launch Streamlit, filter category/date, inspect competitor index, export opportunity table, and test price/demand/cost scenarios.
5. Review tests and assumptions before interpreting any recommendation.
