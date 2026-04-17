import pandas as pd
import sys

print("Testing symptom endpoint logic...")

try:
    df = pd.read_csv('backend/training_data.csv', encoding='latin1')
    print(f"Read {len(df)} rows from training_data.csv")
    
    # New logic
    symptoms = df['text'].astype(str).str.lower().str.strip().unique().tolist()
    symptoms = [s for s in symptoms if s and s != 'nan']
    symptoms.sort()
    
    print(f"\nTotal unique symptom phrases: {len(symptoms)}")
    print("\nFirst 20 symptoms:")
    for i, s in enumerate(symptoms[:20]):
        print(f"  {i+1:2d}: '{s}'")
    
    print("\n--- Testing specific cases ---")
    test_cases = ['cold', 'fever', 'high fever', 'chest pain', 'shortness of breath']
    for test in test_cases:
        exact = test in symptoms
        partial = any(test in s for s in symptoms)
        print(f"  '{test}': exact={exact}, partial={partial}")
    
    # Check for symptoms with commas
    comma_symptoms = [s for s in symptoms if ',' in s]
    print(f"\nSymptoms with commas: {len(comma_symptoms)}")
    if comma_symptoms:
        print("Examples:", comma_symptoms[:5])
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()