from .pricing_metrics import competitor_benchmark
import pandas as pd

def benchmark_summary(prices, competitors):
    x=competitor_benchmark(prices,competitors)
    return x

def coverage_summary(benchmark):
    return benchmark.groupby("product_id",as_index=False).agg(
        observations=("observation_id","count"),benchmark_coverage=("competitor_median",lambda s:s.notna().mean()),
        median_price_index=("relative_price_index","median"),median_gap_pct=("price_gap_pct","median"),
        median_competitors=("competitor_count","median"))
