# test_ratios.py
# Tests for the financial ratio calculation module.


import pytest
import sys
sys.path.append(".")

from app.pipeline.schema import FinancialRecord
from app.pipeline.ratios import calculate_ratios, safe_divide

# --- Tests for safe_divide ---

def test_safe_divide_normal():
    """Normal division should work correctly."""
    assert safe_divide(100.0, 4.0) == 25.0

def test_safe_divide_by_zero():
    """Division by zero should return None, not crash."""
    assert safe_divide(100.0, 0.0) is None

def test_safe_divide_none_numerator():
    """None numerator should return None."""
    assert safe_divide(None, 4.0) is None

def test_safe_divide_none_denominator():
    """None denominator should return None."""
    assert safe_divide(100.0, None) is None

# --- Tests for calculate_ratios ---

@pytest.fixture
def sample_record():
    
    return FinancialRecord(
        period="2024-Q1",
        revenue=1_250_000.0,
        cost_of_sales=487_500.0,
        gross_profit=762_500.0,
        operating_expenses=523_000.0,
        operating_profit=239_500.0,
        net_profit=180_000.0,
        total_assets=3_200_000.0,
        total_liabilities=1_450_000.0,
        total_equity=1_750_000.0,
        current_assets=None,
        current_liabilities=None,
        cash=320_000.0,
    )

def test_gross_profit_margin(sample_record):
    """Gross profit margin should be gross profit / revenue * 100."""
    ratios = calculate_ratios(sample_record)
    assert ratios.gross_profit_margin == 61.0

def test_net_profit_margin(sample_record):
    """Net profit margin should be net profit / revenue * 100."""
    ratios = calculate_ratios(sample_record)
    assert ratios.net_profit_margin == 14.4

def test_is_profitable_true(sample_record):
    """A record with positive net profit should be marked as profitable."""
    ratios = calculate_ratios(sample_record)
    assert ratios.is_profitable is True

def test_is_profitable_false(sample_record):
    """A record with negative net profit should not be marked as profitable."""
    sample_record.net_profit = -50_000.0
    ratios = calculate_ratios(sample_record)
    assert ratios.is_profitable is False

def test_current_ratio_none_when_missing(sample_record):
    """Current ratio should be None when current assets/liabilities are missing."""
    ratios = calculate_ratios(sample_record)
    assert ratios.current_ratio is None

def test_current_ratio_calculated(sample_record):
    """Current ratio should calculate correctly when data is available."""
    sample_record.current_assets = 800_000.0
    sample_record.current_liabilities = 400_000.0
    ratios = calculate_ratios(sample_record)
    assert ratios.current_ratio == 2.0

def test_liquidity_healthy_true(sample_record):
    """Liquidity should be healthy when current ratio >= 1.5."""
    sample_record.current_assets = 800_000.0
    sample_record.current_liabilities = 400_000.0
    ratios = calculate_ratios(sample_record)
    assert ratios.liquidity_healthy is True

def test_liquidity_healthy_false(sample_record):
    """Liquidity should be unhealthy when current ratio < 1.5."""
    sample_record.current_assets = 400_000.0
    sample_record.current_liabilities = 400_000.0
    ratios = calculate_ratios(sample_record)
    assert ratios.liquidity_healthy is False

def test_debt_to_equity(sample_record):
    """Debt to equity should be total liabilities / total equity."""
    ratios = calculate_ratios(sample_record)
    assert ratios.debt_to_equity == round(1_450_000.0 / 1_750_000.0, 2)