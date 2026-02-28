from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class TriageDecision(Base):
    __tablename__ = 'triage_decisions'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Vitals
    bp_systolic = Column(Integer)
    bp_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    temperature = Column(Float)
    spo2 = Column(Integer)
    pain_score = Column(Integer)
    
    # Symptoms
    symptoms_text = Column(Text)
    
    # AI Prediction
    triage_class = Column(String)
    confidence_score = Column(Float)
    is_flagged = Column(Integer)
    
    # Explanation
    explanation = Column(Text)
    
    # Override
    was_overridden = Column(Integer, default=0)
    override_class = Column(String, nullable=True)
    override_reason = Column(Text, nullable=True)

# Create engine
engine = create_engine('sqlite:///mediguard.db')
Base.metadata.create_all(engine)

# Create session maker
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()