// types/index.ts
// Defines the shape of data we receive from the FinSight API.


export interface RatioPeriod {
  period: string
  gross_profit_margin: number | null
  net_profit_margin: number | null
  operating_profit_margin: number | null
  cost_of_sales_ratio: number | null
  current_ratio: number | null
  debt_to_equity: number | null
  is_profitable: boolean
  liquidity_healthy: boolean | null
  high_debt_risk: boolean | null
}

export interface Analysis {
  id: number
  filename: string
  period_count: number
  warnings: string[]
  ratios: RatioPeriod[]
  narrative: string
  created_at?: string
}