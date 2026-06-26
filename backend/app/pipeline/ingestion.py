# ingestion.py
# This module handles reading uploaded files into pandas DataFrames.
# Its only job is to get the raw data into memory so the cleaner can work on it.

import pandas as pd
from pathlib import Path
from .cleaner import clean_dataframe
from .schema import PipelineResult

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

def process_upload(file_path: str, filename: str) -> PipelineResult:
    """
    Entry point for the pipeline. Takes a file path and filename,
    reads the file into a DataFrame, and passes it to the cleaner.
    Raises ValueError for unsupported file types.
    """
    extension = Path(filename).suffix.lower()
    
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Please upload a CSV or Excel file (.csv, .xlsx, .xls)"
        )
    
    if extension == ".csv":
        # Try UTF-8 first, fall back to latin-1 which handles
        # files exported from older South African accounting software
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin-1")
    else:
        # For Excel files, read the first sheet by default
        df = pd.read_excel(file_path, sheet_name=0)
    
    return clean_dataframe(df, filename)