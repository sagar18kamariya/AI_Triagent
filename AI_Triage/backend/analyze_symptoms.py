import pandas as pd
import re

# Load training data
df = pd.read_csv('training_data.csv')
symptoms = df['text'].str.lower().str.strip().tolist()
unique_symptoms = set(symptoms)

print("=== CURRENT SYMPTOM ANALYSIS ===")
print(f"Total entries: {len(symptoms)}")
print(f"Unique symptoms: {len(unique_symptoms)}")
print()

# Common medical symptoms that should be covered
common_symptoms_categories = {
    "Fever & Temperature": [
        "fever", "high fever", "low grade fever", "chills", "sweating",
        "night sweats", "fever with rash", "intermittent fever"
    ],
    "Respiratory": [
        "cough", "dry cough", "productive cough", "shortness of breath",
        "wheezing", "chest tightness", "sputum", "hemoptysis", "nasal congestion",
        "sneezing", "runny nose", "sinus pain", "postnasal drip"
    ],
    "Cardiovascular": [
        "chest pain", "palpitations", "irregular heartbeat", "slow pulse",
        "fast heartbeat", "heart murmur", "edema", "swollen ankles",
        "leg swelling", "hypertension", "hypotension"
    ],
    "Gastrointestinal": [
        "abdominal pain", "nausea", "vomiting", "diarrhea", "constipation",
        "bloating", "gas", "heartburn", "acid reflux", "indigestion",
        "loss of appetite", "weight loss", "weight gain", "blood in stool",
        "black stool", "jaundice", "yellow eyes"
    ],
    "Neurological": [
        "headache", "migraine", "dizziness", "vertigo", "lightheadedness",
        "fainting", "seizure", "tremor", "numbness", "tingling",
        "weakness", "paralysis", "memory loss", "confusion",
        "difficulty speaking", "vision problems", "blurred vision",
        "double vision", "hearing loss", "tinnitus"
    ],
    "Musculoskeletal": [
        "joint pain", "back pain", "neck pain", "muscle pain",
        "muscle weakness", "stiffness", "swelling", "redness",
        "limited mobility", "fracture", "sprain"
    ],
    "Dermatological": [
        "rash", "itching", "hives", "redness", "swelling",
        "blisters", "ulcers", "sores", "dry skin", "oily skin",
        "hair loss", "nail changes", "skin discoloration"
    ],
    "Genitourinary": [
        "painful urination", "frequent urination", "urgency",
        "blood in urine", "cloudy urine", "kidney pain",
        "flank pain", "testicular pain", "penile discharge",
        "vaginal discharge", "vaginal itching", "pelvic pain",
        "menstrual cramps", "heavy bleeding", "missed period"
    ],
    "Psychological": [
        "anxiety", "depression", "stress", "panic attacks",
        "insomnia", "fatigue", "lethargy", "mood swings",
        "irritability", "lack of concentration", "suicidal thoughts"
    ],
    "General": [
        "fatigue", "weakness", "malaise", "loss of energy",
        "dehydration", "thirst", "excessive hunger", "excessive thirst",
        "frequent infections", "slow healing", "bruising easily"
    ]
}

print("=== MISSING SYMPTOMS ANALYSIS ===")
missing_by_category = {}
all_missing = []

for category, symptom_list in common_symptoms_categories.items():
    missing = []
    for symptom in symptom_list:
        # Check if symptom exists (exact or partial match)
        found = False
        for existing in unique_symptoms:
            if symptom in existing or existing in symptom:
                found = True
                break
        if not found:
            missing.append(symptom)
            all_missing.append(symptom)
    
    if missing:
        missing_by_category[category] = missing
        print(f"\n{category} - Missing {len(missing)} symptoms:")
        for m in missing[:10]:  # Show first 10
            print(f"  - {m}")
        if len(missing) > 10:
            print(f"  ... and {len(missing)-10} more")

print(f"\n=== SUMMARY ===")
print(f"Total missing symptoms identified: {len(all_missing)}")

# Also check disease dataset
print("\n=== DISEASE DATASET ANALYSIS ===")
try:
    disease_df = pd.read_csv('disease_dataset.csv')
    print(f"Total diseases: {len(disease_df)}")
    print("Current diseases:")
    for idx, row in disease_df.iterrows():
        print(f"  {idx+1}. {row['disease']} - Symptoms: {row['symptoms']}")
except Exception as e:
    print(f"Error reading disease dataset: {e}")

# Save missing symptoms to file for reference
with open('missing_symptoms.txt', 'w') as f:
    f.write("Missing Symptoms Analysis\n")
    f.write("="*50 + "\n")
    f.write(f"Total missing: {len(all_missing)}\n\n")
    for category, missing in missing_by_category.items():
        f.write(f"{category}:\n")
        for symptom in missing:
            f.write(f"  - {symptom}\n")
        f.write("\n")

print(f"\nMissing symptoms saved to 'missing_symptoms.txt'")