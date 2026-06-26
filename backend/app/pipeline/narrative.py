# narrative.py
# Sends calculated financial ratios to the Gemini API and returns a plain English narrative summary of the SME's financial health.
# asks Gemini only to communicate the results clearly while retaining control over the accuracy of the numbers.

import os
from google import genai
from dotenv import load_dotenv
from .ratios import FinancialRatios

# Loads the environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

def build_prompt(ratios_list: list[FinancialRatios], filename: str) -> str:
    """
    Constructs the prompt we send to Gemini.
    A well-structured prompt is the difference between a generic response
    and a genuinely useful financial narrative.
    """
    # Building a readable summary of each period's ratios
    periods_text = ""
    for r in ratios_list:
        periods_text += f"""
Period: {r.period}
- Gross Profit Margin: {r.gross_profit_margin}%
- Net Profit Margin: {r.net_profit_margin}%
- Operating Profit Margin: {r.operating_profit_margin}%
- Cost of Sales Ratio: {r.cost_of_sales_ratio}%
- Is Profitable: {r.is_profitable}
- Current Ratio: {r.current_ratio if r.current_ratio is not None else 'Not available'}
- Debt to Equity: {r.debt_to_equity if r.debt_to_equity is not None else 'Not available'}
- Liquidity Healthy: {r.liquidity_healthy if r.liquidity_healthy is not None else 'Not available'}
- High Debt Risk: {r.high_debt_risk if r.high_debt_risk is not None else 'Not available'}
"""

    prompt = f"""
You are a friendly but professional financial advisor writing a report for a South African 
small business owner. This person runs their own business and understands their operations 
well, but is not a financial expert. Your job is to explain their financial health in plain, 
clear English that they can understand and act on.

You have been given the following financial ratio data calculated from their uploaded 
financial statements ({filename}), covering {len(ratios_list)} reporting period(s):

{periods_text}

Please write a financial health narrative that does the following:
1. Opens with a one-sentence overall assessment of the business's financial health
2. Explains what the profitability ratios mean for this specific business in plain English
3. Comments on any trends you can see across the periods (improving, declining, stable)
4. If liquidity or debt data is available, comment on the business's financial risk
5. Closes with two or three specific, actionable recommendations the owner can act on

Important rules:
- Write in plain English. Avoid jargon. If you must use a financial term, explain it immediately.
- Be honest but constructive. If something looks concerning, say so clearly but helpfully.
- Keep the entire response under 400 words.
- Do not repeat the raw numbers back to the user — interpret what they mean instead.
- Address the business owner directly using "your business" and "you".
- Write for a South African context where relevant.
"""
    return prompt

def generate_narrative(ratios_list: list[FinancialRatios], filename: str) -> str:
    """
    Calls the Gemini API with prompt and returns the narrative text.
    Handles API errors gracefully so the rest of the system keeps working
    even if the AI call fails.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "AI narrative unavailable: GEMINI_API_KEY not configured."
    
    try:
        # Configures the Gemini client with our API key
        client = genai.Client(api_key=api_key)
        
        # Builds the prompt
        prompt = build_prompt(ratios_list, filename)
        
        # Calls the API using the latest Gemini Flash model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # Extracts the text from the response
        return response.text
        
    except Exception as e:
        # If the API call fails for any reason, return a helpful message
        return f"AI narrative could not be generated at this time. Error: {str(e)}"