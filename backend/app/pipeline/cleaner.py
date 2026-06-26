# cleaner.py
# Takes a raw pandas DataFrame and transforms it into clean standardised data.
# This is where we handle all the real-world messiness of SME financial data.

import pandas as pd
import numpy as np
import re
from typing import Optional
from .schema import FinancialRecord, PipelineResult

# These are the column name variations we expect in real SME files.
# Each key is our standard name, the list contains every variation we map to it.
COLUMN_MAPPINGS = {
    "revenue": [
        "revenue", "total revenue", "turnover", "total turnover",
        "income", "total income", "sales", "total sales", "gross income"
    ],
    "cost_of_sales": [
        "cost of sales", "cost_of_sales", "cogs", "cost of goods sold",
        "direct costs", "cost of revenue"
    ],
    "gross_profit": [
        "gross profit", "gross_profit", "gross margin"
    ],
    "operating_expenses": [
        "operating expenses", "operating_expenses", "opex", "overheads",
        "overhead costs", "total expenses", "expenses"
    ],
    "operating_profit": [
        "operating profit", "operating_profit", "ebit",
        "profit from operations", "trading profit"
    ],
    "net_profit": [
        "net profit", "net_profit", "profit after tax", "pat",
        "net income", "bottom line", "profit for the period"
    ],
    "total_assets": [
        "total assets", "total_assets", "assets"
    ],
    "total_liabilities": [
        "total liabilities", "total_liabilities", "liabilities"
    ],
    "total_equity": [
        "total equity", "total_equity", "equity", "shareholders equity",
        "shareholders' equity", "net assets"
    ],
    "current_assets": [
        "current assets", "current_assets"
    ],
    "current_liabilities": [
        "current liabilities", "current_liabilities"
    ],
    "cash": [
        "cash", "cash and cash equivalents", "cash & cash equivalents",
        "bank balance", "cash balance"
    ],
    "period": [
        "period", "date", "month", "quarter", "year",
        "financial period", "reporting period"
    ]
}

def clean_currency_value(value) -> Optional[float]:
    """
    Converts messy currency strings into plain floats.
    Handles South African formats like:
    - "R 1,250,000.00" -> 1250000.0
    - "(45,000)"       -> -45000.0  (accounting negative format)
    - "1 250 000"      -> 1250000.0 (space-separated thousands)
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    str_val = str(value).strip()
    
    if str_val == "" or str_val.lower() in ["nan", "none", "n/a", "-"]:
        return None
    
    # Check for accounting negative format: (45,000)
    is_negative = str_val.startswith("(") and str_val.endswith(")")
    
    # Remove currency symbols, brackets, spaces, and thousands separators
    cleaned = re.sub(r"[R$£€\s,()]", "", str_val)
    
    try:
        result = float(cleaned)
        return -result if is_negative else result
    except ValueError:
        return None

def normalise_column_names(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Maps whatever column names are in the uploaded file to our standard names.
    Returns the renamed DataFrame and a list of warnings for unmapped columns.
    """
    warnings = []
    rename_map = {}
    
    for col in df.columns:
        normalised = col.lower().strip()
        matched = False
        
        for standard_name, variants in COLUMN_MAPPINGS.items():
            if normalised in variants:
                rename_map[col] = standard_name
                matched = True
                break
        
        if not matched and normalised != "period":
            warnings.append(f"Column '{col}' was not recognised and will be ignored.")
    
    df = df.rename(columns=rename_map)
    return df, warnings

def clean_dataframe(df: pd.DataFrame, filename: str) -> PipelineResult:
    """
    Main cleaning function. Takes a raw DataFrame and returns a PipelineResult
    with cleaned FinancialRecord objects and warnings generated during cleaning.
    """
    warnings = []
    
    # Step 1: Drop completely empty rows
    df = df.dropna(how="all")
    
    # Step 2: Normalise column names
    df, col_warnings = normalise_column_names(df)
    warnings.extend(col_warnings)
    
    # Step 3: Check required columns are present
    required_columns = ["revenue", "cost_of_sales", "net_profit"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"Could not find required columns: {missing}. "
            f"Please ensure your file contains revenue, cost of sales, and net profit data."
        )
    
    # Step 4: Clean all numeric columns
    numeric_columns = [
        "revenue", "cost_of_sales", "gross_profit", "operating_expenses",
        "operating_profit", "net_profit", "total_assets", "total_liabilities",
        "total_equity", "current_assets", "current_liabilities", "cash"
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_currency_value)
    
    # Step 5: Derive missing calculated fields where possible
    if "gross_profit" not in df.columns or df["gross_profit"].isna().all():
        if "revenue" in df.columns and "cost_of_sales" in df.columns:
            df["gross_profit"] = df["revenue"] - df["cost_of_sales"]
            warnings.append("Gross profit was calculated from revenue minus cost of sales.")
    
    if "operating_profit" not in df.columns or df["operating_profit"].isna().all():
        if "gross_profit" in df.columns and "operating_expenses" in df.columns:
            df["operating_profit"] = df["gross_profit"] - df["operating_expenses"]
            warnings.append("Operating profit was calculated from gross profit minus operating expenses.")
    
    # Step 6: Handle period column
    if "period" not in df.columns:
        df["period"] = [f"Period {i+1}" for i in range(len(df))]
        warnings.append("No period column found. Periods have been numbered automatically.")
    
    # Step 7: Build FinancialRecord objects from each row
    records = []
    for _, row in df.iterrows():
        if pd.isna(row.get("revenue")) or row.get("revenue") == 0:
            continue
            
        record = FinancialRecord(
            period=str(row.get("period", "Unknown")),
            revenue=row.get("revenue") or 0.0,
            cost_of_sales=row.get("cost_of_sales") or 0.0,
            gross_profit=row.get("gross_profit") or 0.0,
            operating_expenses=row.get("operating_expenses") or 0.0,
            operating_profit=row.get("operating_profit") or 0.0,
            net_profit=row.get("net_profit") or 0.0,
            total_assets=row.get("total_assets"),
            total_liabilities=row.get("total_liabilities"),
            total_equity=row.get("total_equity"),
            current_assets=row.get("current_assets"),
            current_liabilities=row.get("current_liabilities"),
            cash=row.get("cash"),
        )
        records.append(record)
    
    return PipelineResult(
        records=records,
        period_count=len(records),
        warnings=warnings,
        source_filename=filename,
        detected_format="csv" if filename.endswith(".csv") else "excel"
    )