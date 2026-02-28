from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import json
import numpy as np
from database import SessionLocal, TriageDecision
from datetime import datetime

app = FastAPI(title="MediGuard Triage API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
with open('triage_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('label_map.json', 'r') as f:
    label_map = json.load(f)

reverse_label_map = {v: k for k, v in label_map.items()}

# Request/Response models
class VitalSigns(BaseModel):
    bp_systolic: int
    bp_diastolic: int
    heart_rate: int
    temperature: float
    spo2: int
    pain_score: int

class PatientInput(BaseModel):
    patient_id: str
    vitals: VitalSigns
    symptoms: str

class TriageResponse(BaseModel):
    patient_id: str
    triage_class: str
    confidence_score: float
    is_flagged: bool
    explanation: str
    timestamp: str

# Helper functions
def extract_features(vitals: VitalSigns):
    return [
        vitals.bp_systolic,
        vitals.bp_diastolic,
        vitals.heart_rate,
        vitals.temperature,
        vitals.spo2,
        vitals.pain_score,
        vitals.bp_systolic - vitals.bp_diastolic,
        vitals.heart_rate / vitals.bp_systolic if vitals.bp_systolic > 0 else 0,
    ]

def generate_explanation(vitals: VitalSigns, triage_class: str, confidence: float):
    """Simple rule-based explanation (we'll replace with Bedrock tomorrow)"""
    
    explanations = {
        "emergent": f"Critical vital signs detected: BP {vitals.bp_systolic}/{vitals.bp_diastolic}, HR {vitals.heart_rate}. Immediate medical attention required per emergency protocols.",
        "urgent": f"Concerning presentation requires timely evaluation. Vital signs: BP {vitals.bp_systolic}/{vitals.bp_diastolic}, HR {vitals.heart_rate}, Pain {vitals.pain_score}/10.",
        "non-urgent": f"Stable vital signs: BP {vitals.bp_systolic}/{vitals.bp_diastolic}, HR {vitals.heart_rate}. Can be managed in routine care setting."
    }
    
    base_explanation = explanations.get(triage_class, "Assessment based on clinical presentation.")
    
    if confidence < 0.70:
        base_explanation += f" UNCERTAINTY FLAG: Confidence only {confidence:.0%}. This case requires senior clinician review due to atypical presentation or conflicting indicators."
    
    return base_explanation

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "MediGuard Triage API", "status": "running"}

@app.post("/triage", response_model=TriageResponse)
def triage_patient(patient: PatientInput):
    try:
        # Extract features
        features = extract_features(patient.vitals)
        
        # Predict
        pred_proba = model.predict_proba([features])[0]
        pred_class_encoded = model.predict([features])[0]
        confidence = float(max(pred_proba))
        triage_class = reverse_label_map[int(pred_class_encoded)]
        
        # Flag if low confidence
        is_flagged = confidence < 0.70
        
        # Generate explanation
        explanation = generate_explanation(patient.vitals, triage_class, confidence)
        
        # Save to database
        db = SessionLocal()
        decision = TriageDecision(
            patient_id=patient.patient_id,
            bp_systolic=patient.vitals.bp_systolic,
            bp_diastolic=patient.vitals.bp_diastolic,
            heart_rate=patient.vitals.heart_rate,
            temperature=patient.vitals.temperature,
            spo2=patient.vitals.spo2,
            pain_score=patient.vitals.pain_score,
            symptoms_text=patient.symptoms,
            triage_class=triage_class,
            confidence_score=confidence,
            is_flagged=1 if is_flagged else 0,
            explanation=explanation
        )
        db.add(decision)
        db.commit()
        db.close()
        
        # Return response
        return TriageResponse(
            patient_id=patient.patient_id,
            triage_class=triage_class,
            confidence_score=confidence,
            is_flagged=is_flagged,
            explanation=explanation,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)