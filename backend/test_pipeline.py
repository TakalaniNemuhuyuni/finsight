# test_pipeline.py
# Tests the complete pipeline from ingestion through to AI narrative generation

import sys
sys.path.append(".")

from app.pipeline.ingestion import process_upload
from app.pipeline.ratios import calculate_all_ratios
from app.pipeline.narrative import generate_narrative

# Step 1: Cleans the data
result = process_upload("sample_data/messy_financials.csv", "messy_financials.csv")
print(f"Pipeline completed successfully")
print(f"Periods found: {result.period_count}")

# Step 2: Calculates ratios
ratios = calculate_all_ratios(result.records)
print(f"Ratios calculated for {len(ratios)} periods")

# Step 3: Generates the AI narrative
print(f"Generating narrative...\n")
narrative = generate_narrative(ratios, result.source_filename)
print("=" * 60)
print(narrative)
print("=" * 60)