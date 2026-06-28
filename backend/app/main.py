# main.py
# FastAPI application entry point.


import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .database import get_db, engine
from .models import Base, Analysis
from .pipeline.ingestion import process_upload
from .pipeline.ratios import calculate_all_ratios
from .pipeline.narrative import generate_narrative

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Create all database tables on startup if they don't exist.

Base.metadata.create_all(bind=engine)

# Create the FastAPI application instance
app = FastAPI(
    title="FinSight API",
    description="AI-powered financial statement analyser for South African SMEs",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://finsight-azure.vercel.app"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    """Simple health check endpoint to verify the API is running."""
    return {"status": "FinSight API is running"}

@app.post("/api/analyse")
async def analyse_financial_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Main endpoint. Accepts a financial statement file upload,
    runs it through the full pipeline, and returns the analysis.
    
    File(...) tells FastAPI this is a required file upload field.
    Depends(get_db) is dependency injection — FastAPI automatically
    provides a database session to this function.
    """
    # Step 1: Save the uploaded file to a temporary location
    
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read uploaded file: {str(e)}")

    try:
        # Step 2: Run the cleaning pipeline
        pipeline_result = process_upload(tmp_path, file.filename)

        # Step 3: Calculate financial ratios
        ratios = calculate_all_ratios(pipeline_result.records)

        # Step 4: Generate AI narrative
        narrative = generate_narrative(ratios, file.filename)

        # Step 5: Serialise ratios to a JSON-compatible format for storage
        ratios_data = [
            {
                "period": r.period,
                "gross_profit_margin": r.gross_profit_margin,
                "net_profit_margin": r.net_profit_margin,
                "operating_profit_margin": r.operating_profit_margin,
                "cost_of_sales_ratio": r.cost_of_sales_ratio,
                "current_ratio": r.current_ratio,
                "debt_to_equity": r.debt_to_equity,
                "is_profitable": r.is_profitable,
                "liquidity_healthy": r.liquidity_healthy,
                "high_debt_risk": r.high_debt_risk,
            }
            for r in ratios
        ]

        # Step 6: Save the analysis to the database
        analysis = Analysis(
            filename=file.filename,
            period_count=pipeline_result.period_count,
            narrative=narrative,
            warnings=pipeline_result.warnings,
            ratios=ratios_data,
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # Step 7: Return the complete analysis to the frontend
        return {
            "id": analysis.id,
            "filename": file.filename,
            "period_count": pipeline_result.period_count,
            "warnings": pipeline_result.warnings,
            "ratios": ratios_data,
            "narrative": narrative,
        }

    except ValueError as e:
        # ValueError means the user's file had a problem we could identify
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        # cleans up the temporary file
        os.unlink(tmp_path)

@app.get("/api/analyses")
def get_analyses(db: Session = Depends(get_db)):
    """
    Returns a list of all previous analyses.
    This powers the analysis history feature on the frontend.
    """
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "filename": a.filename,
            "period_count": a.period_count,
            "created_at": a.created_at.isoformat(),
            "narrative": a.narrative,
            "ratios": a.ratios,
            "warnings": a.warnings,
        }
        for a in analyses
    ]

@app.get("/api/analyses/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Returns a single analysis by ID.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": analysis.id,
        "filename": analysis.filename,
        "period_count": analysis.period_count,
        "created_at": analysis.created_at.isoformat(),
        "narrative": analysis.narrative,
        "ratios": analysis.ratios,
        "warnings": analysis.warnings,
    }