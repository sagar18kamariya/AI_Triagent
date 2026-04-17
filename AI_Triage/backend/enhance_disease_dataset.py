import pandas as pd

# Read current disease dataset
df = pd.read_csv('disease_dataset.csv')
print(f"Current disease dataset: {len(df)} diseases")

# Additional diseases to add (from our analysis)
additional_diseases = [
    # Cardiovascular
    ("chest pain palpitations dizziness", "Heart Failure", "Cardiologist", "Echocardiogram and medication needed"),
    ("palpitations dizziness chest pain", "Arrhythmia", "Cardiologist", "ECG and Holter monitoring required"),
    ("headache dizziness blurred vision", "Hypertension", "Cardiologist", "Regular BP monitoring and medication"),
    ("chest pain radiating to arm shortness of breath", "Angina", "Cardiologist", "Stress test and angiography advised"),
    
    # Respiratory
    ("fever cough chest pain shortness of breath", "Pneumonia", "Pulmonologist", "Chest X-ray and antibiotics needed"),
    ("cough mucus production wheezing chest discomfort", "Bronchitis", "Pulmonologist", "Bronchodilators and rest recommended"),
    ("chronic cough shortness of breath wheezing", "COPD", "Pulmonologist", "Pulmonary function test and inhalers"),
    ("cough fever night sweats weight loss", "Tuberculosis", "Pulmonologist", "Sputum test and long-term antibiotics"),
    
    # Gastrointestinal
    ("stomach pain nausea vomiting bloating", "Gastritis", "Gastroenterologist", "Endoscopy and antacids recommended"),
    ("heartburn acid reflux chest pain", "GERD", "Gastroenterologist", "Lifestyle changes and PPIs advised"),
    ("abdominal pain bloating diarrhea constipation", "Irritable Bowel Syndrome", "Gastroenterologist", "Diet modification and stress management"),
    ("abdominal pain nausea fever loss of appetite", "Appendicitis", "Surgeon", "Emergency surgery required"),
    
    # Neurological
    ("severe headache nausea sensitivity to light", "Migraine", "Neurologist", "MRI and preventive medication"),
    ("facial drooping arm weakness speech difficulty", "Stroke", "Neurologist", "Immediate emergency care required"),
    ("seizures confusion temporary loss of awareness", "Epilepsy", "Neurologist", "EEG and anticonvulsant medication"),
    ("numbness weakness vision problems fatigue", "Multiple Sclerosis", "Neurologist", "MRI and immunomodulatory therapy"),
    
    # Musculoskeletal
    ("joint pain stiffness swelling", "Osteoarthritis", "Orthopedic", "X-ray and pain management"),
    ("joint pain swelling morning stiffness fatigue", "Rheumatoid Arthritis", "Rheumatologist", "Blood tests and DMARDs required"),
    ("back pain loss of height bone fractures", "Osteoporosis", "Orthopedic", "Bone density scan and calcium supplements"),
    ("hand numbness tingling weakness", "Carpal Tunnel Syndrome", "Orthopedic", "Nerve conduction study and wrist splint"),
    
    # Infectious Diseases
    ("fever chills sweating headache", "Malaria", "Infectious Disease Specialist", "Blood smear test and antimalarials"),
    ("fever headache abdominal pain diarrhea", "Typhoid", "Infectious Disease Specialist", "Blood culture and antibiotics"),
    ("fever cough loss of taste shortness of breath", "COVID-19", "General Physician", "PCR test and isolation"),
    ("jaundice fatigue abdominal pain dark urine", "Hepatitis", "Gastroenterologist", "Liver function tests and antiviral therapy"),
    
    # Endocrine
    ("fatigue weight gain depression cold intolerance", "Hypothyroidism", "Endocrinologist", "Thyroid function test and hormone replacement"),
    ("weight loss anxiety rapid heartbeat heat intolerance", "Hyperthyroidism", "Endocrinologist", "Thyroid scan and antithyroid medication"),
    
    # Dermatological
    ("itching redness dry skin rash", "Eczema", "Dermatologist", "Topical steroids and moisturizers"),
    ("red patches silvery scales itching", "Psoriasis", "Dermatologist", "Phototherapy and systemic treatment"),
    ("pimples blackheads whiteheads oily skin", "Acne", "Dermatologist", "Topical retinoids and antibiotics"),
    
    # Psychological
    ("sadness loss of interest fatigue sleep changes", "Depression", "Psychiatrist", "Therapy and antidepressant medication"),
    ("excessive worry restlessness fatigue irritability", "Anxiety Disorder", "Psychiatrist", "Cognitive behavioral therapy and medication"),
    
    # Additional common conditions
    ("frequent urination excessive thirst weight loss", "Diabetes Type 1", "Endocrinologist", "Insulin therapy and glucose monitoring"),
    ("blurred vision frequent urination fatigue", "Diabetes Type 2", "Endocrinologist", "Oral medications and diet control"),
    ("red eyes itching discharge", "Conjunctivitis", "Ophthalmologist", "Antibiotic eye drops and hygiene"),
    ("ear pain fever hearing loss", "Otitis Media", "ENT Specialist", "Antibiotics and pain relief"),
    ("sore throat fever swollen lymph nodes", "Strep Throat", "ENT Specialist", "Antibiotics and throat culture"),
    ("abdominal pain diarrhea blood in stool", "Ulcerative Colitis", "Gastroenterologist", "Colonoscopy and immunosuppressants"),
    ("abdominal pain diarrhea weight loss", "Crohn's Disease", "Gastroenterologist", "Endoscopy and biological therapy"),
    ("chest pain fever cough", "Pericarditis", "Cardiologist", "Echocardiogram and anti-inflammatories"),
    ("joint pain fever rash", "Lyme Disease", "Infectious Disease Specialist", "Antibiotics and tick bite prevention"),
    ("headache stiff neck fever", "Meningitis", "Neurologist", "Emergency lumbar puncture and antibiotics"),
]

# Create DataFrame for new diseases
new_rows = []
for symptoms, disease, specialist, advice in additional_diseases:
    new_rows.append({
        'symptoms': symptoms,
        'disease': disease,
        'specialist': specialist,
        'advice': advice
    })

# Convert to DataFrame
new_df = pd.DataFrame(new_rows)

# Combine with existing data
enhanced_df = pd.concat([df, new_df], ignore_index=True)

# Remove any duplicates based on disease name
enhanced_df = enhanced_df.drop_duplicates(subset=['disease'], keep='first')

# Save to new file
enhanced_df.to_csv('disease_dataset_enhanced.csv', index=False)

# Also create a backup of original
df.to_csv('disease_dataset_backup.csv', index=False)

print(f"Enhanced disease dataset: {len(enhanced_df)} diseases (added {len(enhanced_df) - len(df)} new diseases)")
print(f"Original: {len(df)} diseases, Enhanced: {len(enhanced_df)} diseases")
print("\nBackup saved as 'disease_dataset_backup.csv'")

# Show sample of new diseases
print("\nSample of newly added diseases:")
for i in range(min(10, len(new_df))):
    row = new_df.iloc[i]
    print(f"{row['disease']:25s} - Symptoms: {row['symptoms'][:50]}...")

# Now replace the original file
enhanced_df.to_csv('disease_dataset.csv', index=False)
print(f"\nOriginal 'disease_dataset.csv' updated with {len(enhanced_df)} diseases")

# Verify the update
verify_df = pd.read_csv('disease_dataset.csv')
print(f"Verification: disease_dataset.csv now has {len(verify_df)} diseases")