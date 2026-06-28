# models.py
# Defines the database tables using SQLAlchemy ORM.
# SQLAlchemy handles generating the actual SQL to create and query them.

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone


# All our model classes inherit from Base so SQLAlchemy knows they represent database tables
Base = declarative_base()

class Analysis(Base):
    """
    Stores the result of each financial analysis run.
    Each row represents one file upload and its complete analysis result.
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)           # Original uploaded filename
    period_count = Column(Integer, nullable=False)      # Number of periods analysed
    narrative = Column(Text, nullable=False)            # AI generated narrative
    warnings = Column(JSON, nullable=True)              # List of pipeline warnings
    ratios = Column(JSON, nullable=True)                # Calculated ratios as JSON
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Analysis id={self.id} filename={self.filename}>"