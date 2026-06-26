# schema.py
# Defines what "clean" financial data looks like.
# Every other part of the pipeline works toward producing data that matches this structure.

from dataclasses import dataclass
from typing import Optional

@dataclass
class FinancialRecord:
    """
    A single period's worth of financial data for an SME.
    All monetary values are stored as plain floats in ZAR with no formatting.
    Optional fields may not be present in every file we receive.
    """
    period: str                           # e.g. "2024-Q1" or "2024-03-31"
    revenue: float                        # Total income/turnover
    cost_of_sales: float                  # Direct costs of producing goods/services
    gross_profit: float                   # Revenue minus cost of sales
    operating_expenses: float             # Rent, salaries, admin costs etc.
    operating_profit: float               # Gross profit minus operating expenses
    net_profit: float                     # Final bottom line after all deductions
    total_assets: Optional[float]         # Everything the business owns
    total_liabilities: Optional[float]    # Everything the business owes
    total_equity: Optional[float]         # Assets minus liabilities
    current_assets: Optional[float]       # Assets convertible to cash within a year
    current_liabilities: Optional[float]  # Debts due within a year
    cash: Optional[float]                 # Cash and cash equivalents

@dataclass
class PipelineResult:
    """
    The object returned by the pipeline after processing a file.
    Contains the cleaned records and metadata about what we changed.
    """
    records: list[FinancialRecord]        # The cleaned financial records
    period_count: int                     # How many time periods were found
    warnings: list[str]                   # Non-fatal issues we handled
    source_filename: str                  # Original filename for reference
    detected_format: str                  # "csv" or "excel"