# Quick manual test to verify the pipeline works before wire it into FastAPI in Stage 5


import sys
sys.path.append(".")

from app.pipeline.ingestion import process_upload

result = process_upload("sample_data/messy_financials.csv", "messy_financials.csv")

print(f"Pipeline completed successfully")
print(f"File: {result.source_filename}")
print(f"Periods found: {result.period_count}")
print(f"Warnings ({len(result.warnings)}):")
for w in result.warnings:
    print(f"   - {w}")

print(f"Cleaned Records:")
for record in result.records:
    print(f"\n  {record.period}:")
    print(f"    Revenue:          R {record.revenue:>15,.2f}")
    print(f"    Cost of Sales:    R {record.cost_of_sales:>15,.2f}")
    print(f"    Gross Profit:     R {record.gross_profit:>15,.2f}")
    print(f"    Net Profit:       R {record.net_profit:>15,.2f}")
    if record.cash:
        print(f"    Cash:             R {record.cash:>15,.2f}")