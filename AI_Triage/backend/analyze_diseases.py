import pandas as pd

# Load current disease dataset
try:
    disease_df = pd.read_csv('disease_dataset.csv')
    print("=== CURRENT DISEASE DATASET ===")
    print(f"Total diseases: {len(disease_df)}")
    print("\nCurrent diseases and symptoms:")
    for idx, row in disease_df.iterrows():
        print(f"{idx+1:2d}. {row['disease']:20s} - Symptoms: {row['symptoms']}")
except Exception as e:
    print(f"Error reading disease dataset: {e}")
    disease_df = pd.DataFrame()

print("\n" + "="*60)
print("COMMON DISEASES MISSING FROM DATASET")
print("="*60)

# Common diseases that should be included
common_diseases = {
    "Cardiovascular": [
        ("Heart Failure", "shortness of breath fatigue swelling legs", "Cardiologist", "Echocardiogram and medication needed"),
        ("Arrhythmia", "palpitations dizziness chest pain", "Cardiologist", "ECG and Holter monitoring required"),
        ("Hypertension", "headache dizziness blurred vision", "Cardiologist", "Regular BP monitoring and medication"),
        ("Angina", "chest pain radiating to arm shortness of breath", "Cardiologist", "Stress test and angiography advised"),
    ],
    "Respiratory": [
        ("Pneumonia", "fever cough chest pain shortness of breath", "Pulmonologist", "Chest X-ray and antibiotics needed"),
        ("Bronchitis", "cough mucus production wheezing chest discomfort", "Pulmonologist", "Bronchodilators and rest recommended"),
        ("COPD", "chronic cough shortness of breath wheezing", "Pulmonologist", "Pulmonary function test and inhalers"),
        ("Tuberculosis", "cough fever night sweats weight loss", "Pulmonologist", "Sputum test and long-term antibiotics"),
    ],
    "Gastrointestinal": [
        ("Gastritis", "stomach pain nausea vomiting bloating", "Gastroenterologist", "Endoscopy and antacids recommended"),
        ("GERD", "heartburn acid reflux chest pain", "Gastroenterologist", "Lifestyle changes and PPIs advised"),
        ("Irritable Bowel Syndrome", "abdominal pain bloating diarrhea constipation", "Gastroenterologist", "Diet modification and stress management"),
        ("Appendicitis", "abdominal pain nausea fever loss of appetite", "Surgeon", "Emergency surgery required"),
    ],
    "Neurological": [
        ("Migraine", "severe headache nausea sensitivity to light", "Neurologist", "MRI and preventive medication"),
        ("Stroke", "facial drooping arm weakness speech difficulty", "Neurologist", "Immediate emergency care required"),
        ("Epilepsy", "seizures confusion temporary loss of awareness", "Neurologist", "EEG and anticonvulsant medication"),
        ("Multiple Sclerosis", "numbness weakness vision problems fatigue", "Neurologist", "MRI and immunomodulatory therapy"),
    ],
    "Musculoskeletal": [
        ("Osteoarthritis", "joint pain stiffness swelling", "Orthopedic", "X-ray and pain management"),
        ("Rheumatoid Arthritis", "joint pain swelling morning stiffness fatigue", "Rheumatologist", "Blood tests and DMARDs required"),
        ("Osteoporosis", "back pain loss of height bone fractures", "Orthopedic", "Bone density scan and calcium supplements"),
        ("Carpal Tunnel Syndrome", "hand numbness tingling weakness", "Orthopedic", "Nerve conduction study and wrist splint"),
    ],
    "Infectious Diseases": [
        ("Malaria", "fever chills sweating headache", "Infectious Disease Specialist", "Blood smear test and antimalarials"),
        ("Typhoid", "fever headache abdominal pain diarrhea", "Infectious Disease Specialist", "Blood culture and antibiotics"),
        ("COVID-19", "fever cough loss of taste shortness of breath", "General Physician", "PCR test and isolation"),
        ("Hepatitis", "jaundice fatigue abdominal pain dark urine", "Gastroenterologist", "Liver function tests and antiviral therapy"),
    ],
    "Endocrine": [
        ("Hypothyroidism", "fatigue weight gain depression cold intolerance", "Endocrinologist", "Thyroid function test and hormone replacement"),
        ("Hyperthyroidism", "weight loss anxiety rapid heartbeat heat intolerance", "Endocrinologist", "Thyroid scan and antithyroid medication"),
    ],
    "Dermatological": [
        ("Eczema", "itching redness dry skin rash", "Dermatologist", "Topical steroids and moisturizers"),
        ("Psoriasis", "red patches silvery scales itching", "Dermatologist", "Phototherapy and systemic treatment"),
        ("Acne", "pimples blackheads whiteheads oily skin", "Dermatologist", "Topical retinoids and antibiotics"),
    ],
    "Psychological": [
        ("Depression", "sadness loss of interest fatigue sleep changes", "Psychiatrist", "Therapy and antidepressant medication"),
        ("Anxiety Disorder", "excessive worry restlessness fatigue irritability", "Psychiatrist", "Cognitive behavioral therapy and medication"),
    ]
}

# Check which diseases are already in dataset
current_diseases = set(disease_df['disease'].str.lower().tolist()) if not disease_df.empty else set()

missing_diseases = []
for category, diseases in common_diseases.items():
    print(f"\n{category}:")
    for disease_name, symptoms, specialist, advice in diseases:
        if disease_name.lower() not in current_diseases:
            missing_diseases.append((disease_name, symptoms, specialist, advice))
            print(f"  - {disease_name}: {symptoms}")

print(f"\n=== SUMMARY ===")
print(f"Total missing diseases identified: {len(missing_diseases)}")
print(f"Current dataset has {len(current_diseases)} diseases")

# Save missing diseases to file
with open('missing_diseases.txt', 'w') as f:
    f.write("Missing Diseases Analysis\n")
    f.write("="*50 + "\n")
    f.write(f"Total missing: {len(missing_diseases)}\n")
    f.write(f"Current dataset: {len(current_diseases)} diseases\n\n")
    
    for category, diseases in common_diseases.items():
        category_missing = []
        for disease_name, symptoms, specialist, advice in diseases:
            if disease_name.lower() not in current_diseases:
                category_missing.append((disease_name, symptoms, specialist, advice))
        
        if category_missing:
            f.write(f"{category} ({len(category_missing)} missing):\n")
            for disease_name, symptoms, specialist, advice in category_missing:
                f.write(f"  - {disease_name}\n")
                f.write(f"    Symptoms: {symptoms}\n")
                f.write(f"    Specialist: {specialist}\n")
                f.write(f"    Advice: {advice}\n\n")

print("Missing diseases saved to 'missing_diseases.txt'")

# Also check symptom coverage in disease dataset
print("\n=== SYMPTOM COVERAGE IN DISEASE DATASET ===")
all_symptoms_in_diseases = set()
for symptoms in disease_df['symptoms']:
    all_symptoms_in_diseases.update(symptoms.lower().split())

print(f"Unique symptoms mentioned in disease combinations: {len(all_symptoms_in_diseases)}")
print("Sample symptoms:", list(all_symptoms_in_diseases)[:20])