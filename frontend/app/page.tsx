// app/page.tsx
// The main page of FinSight.


"use client"


import { useState, useEffect } from "react"
import { Analysis } from "@/types"

export default function Home() {

  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<Analysis | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<Analysis[]>([])
  const [selectedHistory, setSelectedHistory] = useState<Analysis | null>(null)


  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/analyses")
      const data = await response.json()
      setHistory(data)
    } catch {
      // If history fails to load, we just show nothing — not a critical error
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    setError(null)
    setResult(null)
    setSelectedHistory(null)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch("http://127.0.0.1:8000/api/analyse", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Analysis failed")
      }

      const data: Analysis = await response.json()
      setResult(data)
      fetchHistory() // Refresh history after new analysis
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  // Decides which analysis to display — either the latest result or a selected history item.
  
  const displayedAnalysis = selectedHistory || result

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">FinSight</h1>
        <p className="text-sm text-gray-500">
          AI-powered financial statement analyser for South African SMEs
        </p>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">

        {/* Upload Section */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">
            Upload Financial Statement
          </h2>
          <p className="text-sm text-gray-500 mb-4">
            Upload a CSV or Excel file exported from your accounting software.
            We support exports from Xero, QuickBooks, Sage, and Pastel.
          </p>

          <div className="flex items-center gap-4">
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 
                         file:rounded file:border-0 file:text-sm file:font-medium
                         file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium 
                         rounded hover:bg-blue-700 disabled:opacity-50 
                         disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Analysing..." : "Analyse"}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3" />
            <p className="text-sm text-gray-500">
              Analysing your financial statements...
            </p>
          </div>
        )}

        {/* Results Section */}
        {displayedAnalysis && !loading && (
          <div className="space-y-6">

            {/* Narrative */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Financial Health Report
              </h2>
              <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                {displayedAnalysis.narrative}
              </div>
            </div>

            {/* Warnings */}
            {displayedAnalysis.warnings.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-amber-800 mb-2">
                  Pipeline Notes
                </h3>
                <ul className="space-y-1">
                  {displayedAnalysis.warnings.map((warning, i) => (
                    <li key={i} className="text-sm text-amber-700">
                      • {warning}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Ratios Table */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Financial Ratios by Period
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 pr-4 font-medium text-gray-600">
                        Metric
                      </th>
                      {displayedAnalysis.ratios.map((r) => (
                        <th
                          key={r.period}
                          className="text-right py-2 px-4 font-medium text-gray-600"
                        >
                          {r.period}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {[
                      { label: "Gross Profit Margin", key: "gross_profit_margin", suffix: "%" },
                      { label: "Net Profit Margin", key: "net_profit_margin", suffix: "%" },
                      { label: "Operating Profit Margin", key: "operating_profit_margin", suffix: "%" },
                      { label: "Cost of Sales Ratio", key: "cost_of_sales_ratio", suffix: "%" },
                      { label: "Current Ratio", key: "current_ratio", suffix: "x" },
                      { label: "Debt to Equity", key: "debt_to_equity", suffix: "x" },
                    ].map(({ label, key, suffix }) => (
                      <tr key={key}>
                        <td className="py-2 pr-4 text-gray-700">{label}</td>
                        {displayedAnalysis.ratios.map((r) => {
                          const value = r[key as keyof typeof r]
                          return (
                            <td
                              key={r.period}
                              className="py-2 px-4 text-right text-gray-900"
                            >
                              {value !== null && value !== undefined
                                ? `${value}${suffix}`
                                : <span className="text-gray-400">N/A</span>}
                            </td>
                          )
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

        {/* History Section */}
        {history.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Analysis History
            </h2>
            <div className="space-y-2">
              {history.map((analysis) => (
                <button
                  key={analysis.id}
                  onClick={() => setSelectedHistory(analysis)}
                  className="w-full text-left px-4 py-3 rounded border border-gray-200 
                             hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-900">
                      {analysis.filename}
                    </span>
                    <span className="text-xs text-gray-500">
                      {analysis.period_count} periods
                    </span>
                  </div>
                  {analysis.created_at && (
                    <div className="text-xs text-gray-400 mt-0.5">
                      {new Date(analysis.created_at).toLocaleDateString("en-ZA")}
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

      </div>
    </main>
  )
}
