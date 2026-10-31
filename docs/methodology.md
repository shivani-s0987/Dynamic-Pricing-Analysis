# Methodology

A fixed-seed generator creates 180 products across 10 categories from 2025-01-01 through 2026-06-30. Price observations are daily. Three synthetic competitor price series are sampled with occasional missing observations. Simulated daily demand depends on relative price, category-independent seasonal patterns, promotion status and noise; stockouts censor observed units. This is designed for portfolio analysis, not calibrated to a real business.

Price volatility is the sample standard deviation of daily percentage price changes after sorting observations by product/date; at least 10 price changes are required. Competitor benchmark is the median of available comparable competitor prices at matching date/product/region/channel. Relative price index = 100 × our price / benchmark. Price-demand correlation is descriptive, with no causal interpretation.
