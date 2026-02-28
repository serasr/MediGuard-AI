import json
import pickle
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler

# Load synthetic patients
with open('../data/synthetic_patients.json', 'r') as f:
    patients = json.load(f)

# Extract features and labels
def extract_features(patient):
    v = patient['vitals']
    # Create feature vector from vitals
    features = [
        v['bp_sys'],
        v['bp_dia'],
        v['hr'],
        v['temp'],
        v['spo2'],
        v['pain'],
        # Derived features
        v['bp_sys'] - v['bp_dia'],  # pulse pressure
        v['hr'] / v['bp_sys'] if v['bp_sys'] > 0 else 0,  # shock index
    ]
    return features

X = np.array([extract_features(p) for p in patients])
y = np.array([p['ground_truth']['label'] for p in patients])

# Encode labels
label_map = {'non-urgent': 0, 'urgent': 1, 'emergent': 2}
y_encoded = np.array([label_map[label] for label in y])

# Train model with calibration (gives us confidence scores)
base_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    random_state=42
)

# Wrap with calibration for confidence scores
model = CalibratedClassifierCV(base_model, method='sigmoid', cv=5)

# Fit
model.fit(X, y_encoded)

# Create scaler
scaler = StandardScaler()
scaler.fit(X)

# Save model and scaler
with open('triage_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open('label_map.json', 'w') as f:
    json.dump(label_map, f)

print("Model trained and saved!")

# Test on a few examples
reverse_map = {v: k for k, v in label_map.items()}
print("\nTesting on sample patients:")
for i in range(5):
    features = extract_features(patients[i])
    pred_proba = model.predict_proba([features])[0]
    pred_class = model.predict([features])[0]
    confidence = max(pred_proba)
    
    print(f"\nPatient {i+1}: {patients[i]['symptoms'][:50]}...")
    print(f"  True: {patients[i]['ground_truth']['label']}")
    print(f"  Predicted: {reverse_map[pred_class]} (confidence: {confidence:.2f})")
    print(f"  Flagged: {'YES' if confidence < 0.70 else 'NO'}")