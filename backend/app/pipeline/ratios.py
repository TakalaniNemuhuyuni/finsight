# ratios.py
# Calculates standard financial ratios from cleaned FinancialRecord data.


from dataclasses import dataclass
from typing import Optional
from .schema import FinancialRecord

@dataclass
class FinancialRatios:
    """
    Holds all calculated ratios for a single financial period.
    Any ratio that could not be calculated due to missing data is None.
    """
    period: str

    # Profitability ratios — measures how well the business generates profit
    gross_profit_margin: Optional[float]      # % of revenue kept after cost of sales
    net_profit_margin: Optional[float]        # % of revenue kept as final profit
    operating_profit_margin: Optional[float]  # % of revenue kept after operations

    # Liquidity ratios — measures ability to pay short-term debts
    current_ratio: Optional[float]            # current assets / current liabilities
    cash_ratio: Optional[float]               # cash / current liabilities

    # Solvency ratios — measures long-term financial stability
    debt_to_equity: Optional[float]           # total liabilities / total equity
    equity_ratio: Optional[float]             # total equity / total assets

    # Efficiency ratios — measures how well revenue is managed
    cost_of_sales_ratio: Optional[float]      # cost of sales as % of revenue

    # Interpretation flags — simple health indicators for the AI narrative layer
    is_profitable: bool                       # net profit > 0
    liquidity_healthy: Optional[bool]         # current ratio >= 1.5
    high_debt_risk: Optional[bool]            # debt to equity > 2.0

def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """
    Divides two numbers safely, returning None if either value is missing
    or if the denominator is zero. This prevents division by zero errors
    and handles missing optional fields cleanly.
    """
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return None
    return numerator / denominator

def calculate_ratios(record: FinancialRecord) -> FinancialRatios:
    """
    Takes a single FinancialRecord and returns a FinancialRatios object
    with all calculable ratios populated and unavailable ones set to None.
    """
    # Profitability ratios
    gross_profit_margin = safe_divide(record.gross_profit, record.revenue)
    if gross_profit_margin is not None:
        gross_profit_margin = round(gross_profit_margin * 100, 2)

    net_profit_margin = safe_divide(record.net_profit, record.revenue)
    if net_profit_margin is not None:
        net_profit_margin = round(net_profit_margin * 100, 2)

    operating_profit_margin = safe_divide(record.operating_profit, record.revenue)
    if operating_profit_margin is not None:
        operating_profit_margin = round(operating_profit_margin * 100, 2)

    # Liquidity ratios
    current_ratio = safe_divide(record.current_assets, record.current_liabilities)
    if current_ratio is not None:
        current_ratio = round(current_ratio, 2)

    cash_ratio = safe_divide(record.cash, record.current_liabilities)
    if cash_ratio is not None:
        cash_ratio = round(cash_ratio, 2)

    # Solvency ratios
    debt_to_equity = safe_divide(record.total_liabilities, record.total_equity)
    if debt_to_equity is not None:
        debt_to_equity = round(debt_to_equity, 2)

    equity_ratio = safe_divide(record.total_equity, record.total_assets)
    if equity_ratio is not None:
        equity_ratio = round(equity_ratio, 2)

    # Efficiency ratios
    cost_of_sales_ratio = safe_divide(record.cost_of_sales, record.revenue)
    if cost_of_sales_ratio is not None:
        cost_of_sales_ratio = round(cost_of_sales_ratio * 100, 2)

    # Interpretation flags
    is_profitable = record.net_profit > 0

    liquidity_healthy = None
    if current_ratio is not None:
        liquidity_healthy = current_ratio >= 1.5

    high_debt_risk = None
    if debt_to_equity is not None:
        high_debt_risk = debt_to_equity > 2.0

    return FinancialRatios(
        period=record.period,
        gross_profit_margin=gross_profit_margin,
        net_profit_margin=net_profit_margin,
        operating_profit_margin=operating_profit_margin,
        current_ratio=current_ratio,
        cash_ratio=cash_ratio,
        debt_to_equity=debt_to_equity,
        equity_ratio=equity_ratio,
        cost_of_sales_ratio=cost_of_sales_ratio,
        is_profitable=is_profitable,
        liquidity_healthy=liquidity_healthy,
        high_debt_risk=high_debt_risk,
    )

def calculate_all_ratios(records: list[FinancialRecord]) -> list[FinancialRatios]:
    """
    Calculates ratios for every period in a list of FinancialRecords.
    The function the rest of the system calls.
    """
    return [calculate_ratios(record) for record in records]