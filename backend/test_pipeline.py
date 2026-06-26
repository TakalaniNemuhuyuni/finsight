# test_pipeline.py
# Tests the full pipeline from file ingestion through to ratio calculation

import sys
sys.path.append(".")

from app.pipeline.ingestion import process_upload
from app.pipeline.ratios import calculate_all_ratios

# Step 1: Runs the cleaning pipeline
result = process_upload("sample_data/messy_financials.csv", "messy_financials.csv")

print(f"Pipeline completed successfully")
print(f"Periods found: {result.period_count}")

# Step 2: Calculates ratios
ratios = calculate_all_ratios(result.records)

print(f"Financial Ratios:")
for r in ratios:
    print(f"\n  {r.period}:")
    print(f"    Gross Profit Margin:     {r.gross_profit_margin}%")
    print(f"    Net Profit Margin:       {r.net_profit_margin}%")
    print(f"    Operating Profit Margin: {r.operating_profit_margin}%")
    print(f"    Cost of Sales Ratio:     {r.cost_of_sales_ratio}%")
    print(f"    Is Profitable:           {r.is_profitable}")
    print(f"    Current Ratio:           {r.current_ratio if r.current_ratio else 'Not available'}")
    print(f"    Debt to Equity:          {r.debt_to_equity if r.debt_to_equity else 'Not available'}")
    print(f"    Liquidity Healthy:       {r.liquidity_healthy if r.liquidity_healthy is not None else 'Not available'}")