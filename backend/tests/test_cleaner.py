# test_cleaner.py
# Tests for the data cleaning module.


import pytest
import sys
sys.path.append(".")

from app.pipeline.cleaner import clean_currency_value, clean_dataframe
import pandas as pd

# --- Tests for clean_currency_value ---

def test_clean_rand_formatted_value():
    """South African rand format should be cleaned to a plain float."""
    assert clean_currency_value("R 1,250,000.00") == 1_250_000.0

def test_clean_accounting_negative():
    """Accounting negative format (45,000) should become -45000.0."""
    assert clean_currency_value("(45,000)") == -45_000.0

def test_clean_plain_number():
    """Plain numbers should pass through unchanged."""
    assert clean_currency_value(1250000.0) == 1_250_000.0

def test_clean_empty_string():
    """Empty strings should return None."""
    assert clean_currency_value("") is None

def test_clean_none_value():
    """None should return None."""
    assert clean_currency_value(None) is None

def test_clean_na_string():
    """N/A strings should return None."""
    assert clean_currency_value("N/A") is None

# --- Tests for clean_dataframe ---

def test_clean_dataframe_normalises_columns():
    """Column name variations should be mapped to standard names."""
    df = pd.DataFrame({
        "Total Revenue": [1_000_000.0],
        "Cost of Sales": [400_000.0],
        "Net Profit": [200_000.0],
        "Reporting Period": ["2024-Q1"],
    })
    result = clean_dataframe(df, "test.csv")
    assert result.period_count == 1
    assert result.records[0].revenue == 1_000_000.0

def test_clean_dataframe_raises_on_missing_required_columns():
    """Missing required columns should raise a ValueError."""
    df = pd.DataFrame({
        "Some Column": [1_000_000.0],
    })
    with pytest.raises(ValueError):
        clean_dataframe(df, "test.csv")

def test_clean_dataframe_derives_gross_profit():
    """Gross profit should be derived when missing."""
    df = pd.DataFrame({
        "Total Revenue": [1_000_000.0],
        "Cost of Sales": [400_000.0],
        "Net Profit": [200_000.0],
        "Reporting Period": ["2024-Q1"],
    })
    result = clean_dataframe(df, "test.csv")
    assert result.records[0].gross_profit == 600_000.0