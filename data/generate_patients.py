import json
import random

# Define patient scenarios
def generate_patients():
    patients = []
    
    # EMERGENT CASES (High confidence)
    emergent_scenarios = [
        {
            "vitals": {"bp_sys": 180, "bp_dia": 115, "hr": 105, "temp": 37.2, "spo2": 95, "pain": 9},
            "symptoms": "Severe crushing chest pain radiating to left arm, profuse sweating, nausea",
            "label": "emergent",
            "confidence": 0.94,
            "reason": "STEMI criteria - immediate cardiac workup needed"
        },
        {
            "vitals": {"bp_sys": 200, "bp_dia": 120, "hr": 110, "temp": 37.5, "spo2": 94, "pain": 8},
            "symptoms": "Worst headache of life, visual disturbances, confusion",
            "label": "emergent",
            "confidence": 0.92,
            "reason": "Hypertensive emergency with neurological symptoms"
        },
        {
            "vitals": {"bp_sys": 90, "bp_dia": 60, "hr": 120, "temp": 39.1, "spo2": 88, "pain": 7},
            "symptoms": "Fever, rapid breathing, altered mental status, rapid heart rate",
            "label": "emergent",
            "confidence": 0.95,
            "reason": "Sepsis criteria met - immediate intervention required"
        },
        {
            "vitals": {"bp_sys": 85, "bp_dia": 55, "hr": 125, "temp": 36.2, "spo2": 90, "pain": 8},
            "symptoms": "Severe abdominal pain, distension, no bowel sounds",
            "label": "emergent",
            "confidence": 0.91,
            "reason": "Signs of acute abdomen, possible bowel perforation"
        },
        {
            "vitals": {"bp_sys": 175, "bp_dia": 110, "hr": 95, "temp": 37.0, "spo2": 92, "pain": 9},
            "symptoms": "Sudden severe back pain, pulsatile abdominal mass",
            "label": "emergent",
            "confidence": 0.93,
            "reason": "Possible aortic aneurysm rupture"
        },
    ]
    
    # URGENT CASES (Medium confidence)
    urgent_scenarios = [
        {
            "vitals": {"bp_sys": 145, "bp_dia": 92, "hr": 88, "temp": 37.8, "spo2": 96, "pain": 6},
            "symptoms": "Productive cough for 3 days, fever, shortness of breath on exertion",
            "label": "urgent",
            "confidence": 0.82,
            "reason": "Likely pneumonia - needs imaging and antibiotics soon"
        },
        {
            "vitals": {"bp_sys": 138, "bp_dia": 88, "hr": 92, "temp": 37.1, "spo2": 97, "pain": 5},
            "symptoms": "Leg pain and swelling after long flight, calf tenderness",
            "label": "urgent",
            "confidence": 0.79,
            "reason": "Wells score suggests DVT - needs ultrasound within hours"
        },
        {
            "vitals": {"bp_sys": 155, "bp_dia": 95, "hr": 98, "temp": 38.2, "spo2": 96, "pain": 7},
            "symptoms": "Right lower quadrant abdominal pain, nausea, rebound tenderness",
            "label": "urgent",
            "confidence": 0.84,
            "reason": "Appendicitis likely - surgical evaluation needed"
        },
        {
            "vitals": {"bp_sys": 142, "bp_dia": 90, "hr": 85, "temp": 37.5, "spo2": 97, "pain": 6},
            "symptoms": "Severe headache with neck stiffness and photophobia",
            "label": "urgent",
            "confidence": 0.81,
            "reason": "Possible meningitis - lumbar puncture indicated"
        },
        {
            "vitals": {"bp_sys": 150, "bp_dia": 88, "hr": 95, "temp": 37.3, "spo2": 95, "pain": 7},
            "symptoms": "Sudden onset severe flank pain, hematuria",
            "label": "urgent",
            "confidence": 0.83,
            "reason": "Likely kidney stone - pain management and imaging needed"
        },
    ]
    
    # AMBIGUOUS CASES (Low confidence - should be flagged)
    ambiguous_scenarios = [
        {
            "vitals": {"bp_sys": 145, "bp_dia": 90, "hr": 98, "temp": 37.1, "spo2": 97, "pain": 5},
            "symptoms": "Mild chest discomfort, some sweating, no radiation, improves with rest",
            "label": "urgent",
            "confidence": 0.68,
            "reason": "Atypical chest pain - could be cardiac or musculoskeletal, needs ECG"
        },
        {
            "vitals": {"bp_sys": 135, "bp_dia": 85, "hr": 92, "temp": 37.0, "spo2": 98, "pain": 4},
            "symptoms": "Vague abdominal discomfort, intermittent, no fever, elderly patient",
            "label": "urgent",
            "confidence": 0.65,
            "reason": "Non-specific presentation in elderly - could be serious, needs evaluation"
        },
        {
            "vitals": {"bp_sys": 152, "bp_dia": 92, "hr": 105, "temp": 37.2, "spo2": 97, "pain": 6},
            "symptoms": "Palpitations, dizziness, anxiety symptoms, history of panic disorder",
            "label": "non-urgent",
            "confidence": 0.62,
            "reason": "Symptoms overlap panic attack and cardiac arrhythmia - needs senior review"
        },
        {
            "vitals": {"bp_sys": 140, "bp_dia": 88, "hr": 90, "temp": 37.4, "spo2": 96, "pain": 5},
            "symptoms": "Headache with some visual changes, but patient has migraine history",
            "label": "non-urgent",
            "confidence": 0.67,
            "reason": "Could be typical migraine or something serious - borderline"
        },
        {
            "vitals": {"bp_sys": 148, "bp_dia": 90, "hr": 88, "temp": 37.0, "spo2": 97, "pain": 4},
            "symptoms": "Shortness of breath, but patient is obese with COPD history",
            "label": "urgent",
            "confidence": 0.64,
            "reason": "Multiple confounding factors - difficult to assess acuity"
        },
    ]
    
    # NON-URGENT CASES (High confidence)
    non_urgent_scenarios = [
        {
            "vitals": {"bp_sys": 125, "bp_dia": 80, "hr": 75, "temp": 37.0, "spo2": 98, "pain": 3},
            "symptoms": "Minor cut on finger from cooking, bleeding controlled, no signs of infection",
            "label": "non-urgent",
            "confidence": 0.89,
            "reason": "Simple laceration - can wait for routine wound care"
        },
        {
            "vitals": {"bp_sys": 130, "bp_dia": 82, "hr": 78, "temp": 37.2, "spo2": 98, "pain": 2},
            "symptoms": "Mild sore throat for 2 days, no fever, able to swallow",
            "label": "non-urgent",
            "confidence": 0.87,
            "reason": "Viral pharyngitis likely - supportive care sufficient"
        },
        {
            "vitals": {"bp_sys": 122, "bp_dia": 78, "hr": 72, "temp": 37.1, "spo2": 99, "pain": 3},
            "symptoms": "Ankle sprain from sports 2 days ago, walking with limp, some swelling",
            "label": "non-urgent",
            "confidence": 0.88,
            "reason": "Minor musculoskeletal injury - RICE protocol and reassessment"
        },
        {
            "vitals": {"bp_sys": 128, "bp_dia": 80, "hr": 76, "temp": 37.0, "spo2": 98, "pain": 2},
            "symptoms": "Mild headache, well-hydrated, no neurological symptoms",
            "label": "non-urgent",
            "confidence": 0.86,
            "reason": "Tension headache - simple analgesia appropriate"
        },
        {
            "vitals": {"bp_sys": 132, "bp_dia": 84, "hr": 80, "temp": 37.3, "spo2": 98, "pain": 3},
            "symptoms": "Rash on arm for 3 days, itchy but no systemic symptoms",
            "label": "non-urgent",
            "confidence": 0.85,
            "reason": "Dermatological issue - can be managed in outpatient setting"
        },
    ]
    
    # Combine all
    all_scenarios = (
        emergent_scenarios * 2 +  # 10 emergent cases
        urgent_scenarios * 2 +    # 10 urgent cases
        ambiguous_scenarios * 2 + # 10 ambiguous cases
        non_urgent_scenarios * 2  # 10 non-urgent cases
    )
    
    # Create patient records
    for idx, scenario in enumerate(all_scenarios):
        patient = {
            "patient_id": f"PT-{1000 + idx}",
            "vitals": scenario["vitals"],
            "symptoms": scenario["symptoms"],
            "ground_truth": {
                "label": scenario["label"],
                "confidence": scenario["confidence"],
                "clinical_reasoning": scenario["reason"]
            }
        }
        patients.append(patient)
    
    return patients

# Generate and save
patients = generate_patients()

with open('synthetic_patients.json', 'w') as f:
    json.dump(patients, f, indent=2)

print(f"Generated {len(patients)} synthetic patient records")
print(f"Emergent: {sum(1 for p in patients if p['ground_truth']['label'] == 'emergent')}")
print(f"Urgent: {sum(1 for p in patients if p['ground_truth']['label'] == 'urgent')}")
print(f"Non-urgent: {sum(1 for p in patients if p['ground_truth']['label'] == 'non-urgent')}")
print(f"Flagged (confidence < 0.70): {sum(1 for p in patients if p['ground_truth']['confidence'] < 0.70)}")