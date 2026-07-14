# FinSight

AI-powered financial statement analyser for South African SMEs.

**Live Demo:** https://finsight-azure.vercel.app  


---

## The Business Problem

Small and medium enterprises make up over 90% of registered businesses in South Africa, yet most SME owners cannot afford a financial analyst and find bank-generated reports confusing. Before approaching a lender like Absa or Nedbank for credit, an SME owner needs to understand their own financial health but the raw numbers from their accounting software tell them very little without interpretation.

FinSight solves this by accepting a financial statement export from any major South African accounting package, cleaning and normalising the messy real-world data, calculating standard financial ratios, and using the Gemini AI API to generate a plain English narrative that the business owner can read, understand, and act on immediately.

## Who It Is For

A small business owner or their bookkeeper who wants to understand their financial health before approaching a bank, without needing to hire a financial analyst.

---

## Key Features

- Accepts messy real-world CSV and Excel exports from Xero, QuickBooks, Sage, and Pastel
- Handles South African currency formatting including rand symbols, comma-separated thousands, and accounting negative format like (45,000)
- Maps 50+ column name variations to standard financial field names automatically
- Derives missing calculated fields like gross profit when revenue and cost of sales are present
- Calculates profitability, liquidity, solvency, and efficiency ratios across multiple periods
- Generates plain English AI narrative using Google Gemini, addressed directly to the SME owner
- Stores all analyses in PostgreSQL for historical retrieval
- 22 unit tests covering edge cases in the cleaning and ratio calculation pipeline
- Fully deployed with a live frontend on Vercel and a live API on Railway

---

## Tech Stack

| Technology | Role | Why This Choice |
|---|---|---|
| Python 3.12 | Backend language | Industry standard for data pipelines and AI integration |
| FastAPI | REST API framework | Automatic OpenAPI documentation, async support, and type safety via Pydantic |
| Pandas | Data processing | Best-in-class library for tabular data cleaning and transformation |
| SQLAlchemy | ORM | Python equivalent of Entity Framework — maps classes to database tables without writing raw SQL |
| PostgreSQL | Database | Production-grade relational database with native JSON column support for variable-length ratio data |
| Docker | Local database containerisation | Ensures environment parity between local development and production |
| Google Gemini API | AI narrative generation | Free tier sufficient for development, and the pipeline is architected to be swappable with any LLM |
| Next.js | Frontend framework | Industry standard React framework with server-side rendering and first-class Vercel deployment support |
| Tailwind CSS | Styling | Utility-first CSS that produces consistent, responsive UI without custom stylesheets |
| Pytest | Testing | Python standard for unit testing, equivalent to xUnit in C# |
| Railway | Backend deployment | Supports persistent server processes and managed PostgreSQL in a single platform |
| Vercel | Frontend deployment | Built by the Next.js team, zero-configuration deployment with global CDN |

---

## Architecture

User uploads CSV or Excel file

↓

Next.js Frontend (Vercel)

↓ POST /api/analyse

FastAPI Backend (Railway)

↓

┌──────────────────────────────────────┐

│              Pipeline                │

│                                      │

│  1. Ingestion (ingestion.py)         │

│     Read CSV or Excel file           │

│     Handle UTF-8 and latin-1         │

│                                      │

│  2. Cleaning (cleaner.py)            │

│     Normalise 50+ column variations  │

│     Strip South African currency     │

│     Handle accounting negatives      │

│     Derive missing calculated fields │

│                                      │

│  3. Ratios (ratios.py)               │

│     Calculate 8 financial ratios     │

│     Generate health indicator flags  │

│                                      │

│  4. Narrative (narrative.py)         │

│     Engineer prompt for SME context  │

│     Generate AI summary via Gemini   │

└──────────────────────────────────────┘

↓

PostgreSQL Database (Railway)

Stores analysis for historical retrieval

↓

JSON response returned to frontend

Results displayed to user

---

## Sample Data

A sample financial statement CSV is included at `backend/sample_data/messy_financials.csv`. This file intentionally uses inconsistent column names, South African rand formatting, and missing fields to demonstrate the pipeline's cleaning capabilities. Upload it on the live demo or locally to see the full analysis.

---

## What I Learned

Working with real-world messy financial data was significantly harder than I expected. SME owners export files from many different accounting packages, each with different column naming conventions, currency formatting, and encoding. Building a pipeline robust enough to handle all of these cases taught me that production data engineering is mostly about defensive programming like anticipating every way input can be malformed and handling it gracefully rather than crashing.

Prompt engineering for the AI narrative layer was more nuanced than I anticipated. The quality of the Gemini output changed dramatically based on how specifically I defined the audience, the purpose, and the constraints in the prompt. Vague prompts produced generic output that would not be useful to a real SME owner. Structuring the prompt around who would read it, what they needed to do with it, and what the AI should not do was as important as the data we passed in.

Deploying a multi-service application taught me that environment parity matters significantly. What works on your local machine does not automatically work in production, and managing environment variables, database connections, and CORS configuration across environments requires deliberate planning rather than an afterthought.
