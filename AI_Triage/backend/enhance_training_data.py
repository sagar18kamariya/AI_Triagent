import pandas as pd
import csv

# Read current training data
df = pd.read_csv('training_data.csv')
print(f"Current training data: {len(df)} rows")

# Define additional symptoms with their metadata
# Format: (symptom, severity_score, risk, doctor, advice)
additional_symptoms = [
    # Fever & Temperature
    ("chills", 3, "MEDIUM", "General Physician", "Keep warm and monitor temperature"),
    ("sweating", 2, "LOW", "General Physician", "Stay hydrated and rest"),
    ("night sweats", 4, "MEDIUM", "General Physician", "May indicate infection, consult doctor"),
    
    # Respiratory
    ("wheezing", 5, "MEDIUM", "Pulmonologist", "Bronchodilator may be needed"),
    ("sputum", 3, "LOW", "General Physician", "Note color and consult if persists"),
    ("hemoptysis", 9, "HIGH", "Pulmonologist", "Immediate medical attention required"),
    ("nasal congestion", 2, "LOW", "ENT Specialist", "Steam inhalation and decongestants"),
    ("sinus pain", 4, "MEDIUM", "ENT Specialist", "Sinus evaluation and antibiotics if infected"),
    ("postnasal drip", 3, "LOW", "ENT Specialist", "Antihistamines may help"),
    
    # Cardiovascular
    ("palpitations", 6, "MEDIUM", "Cardiologist", "ECG and heart evaluation recommended"),
    ("irregular heartbeat", 7, "MEDIUM", "Cardiologist", "Cardiac monitoring required"),
    ("slow pulse", 5, "MEDIUM", "Cardiologist", "Check for bradycardia"),
    ("heart murmur", 6, "MEDIUM", "Cardiologist", "Echocardiogram advised"),
    ("edema", 5, "MEDIUM", "Cardiologist", "Diuretics and salt restriction"),
    ("swollen ankles", 4, "MEDIUM", "Cardiologist", "Elevate legs and reduce salt"),
    ("leg swelling", 5, "MEDIUM", "Cardiologist", "Check for heart or kidney issues"),
    ("hypertension", 6, "MEDIUM", "Cardiologist", "Regular BP monitoring and medication"),
    ("hypotension", 4, "MEDIUM", "Cardiologist", "Increase fluid and salt intake"),
    
    # Gastrointestinal
    ("abdominal pain", 5, "MEDIUM", "Gastroenterologist", "Ultrasound and evaluation needed"),
    ("nausea", 4, "MEDIUM", "Gastroenterologist", "Anti-emetics and small meals"),
    ("constipation", 3, "LOW", "Gastroenterologist", "Increase fiber and water intake"),
    ("bloating", 3, "LOW", "Gastroenterologist", "Diet modification and probiotics"),
    ("heartburn", 4, "MEDIUM", "Gastroenterologist", "Antacids and avoid spicy food"),
    ("acid reflux", 4, "MEDIUM", "Gastroenterologist", "PPIs and elevation of head while sleeping"),
    ("indigestion", 3, "LOW", "Gastroenterologist", "Small frequent meals and avoid fatty food"),
    ("loss of appetite", 4, "MEDIUM", "Gastroenterologist", "Nutritional supplements may be needed"),
    ("weight loss", 6, "MEDIUM", "General Physician", "Comprehensive evaluation for underlying cause"),
    ("weight gain", 4, "MEDIUM", "Endocrinologist", "Thyroid and hormonal evaluation"),
    ("blood in stool", 8, "HIGH", "Gastroenterologist", "Colonoscopy required immediately"),
    ("black stool", 7, "HIGH", "Gastroenterologist", "Possible GI bleeding, urgent evaluation"),
    ("jaundice", 7, "HIGH", "Gastroenterologist", "Liver function tests and ultrasound"),
    ("yellow eyes", 7, "HIGH", "Gastroenterologist", "Liver evaluation required"),
    
    # Neurological
    ("dizziness", 4, "MEDIUM", "Neurologist", "Vestibular evaluation and balance tests"),
    ("vertigo", 5, "MEDIUM", "Neurologist", "Epley maneuver and vestibular suppressants"),
    ("lightheadedness", 4, "MEDIUM", "Neurologist", "Check blood pressure and hydration"),
    ("tremor", 5, "MEDIUM", "Neurologist", "Neurological examination needed"),
    ("numbness", 5, "MEDIUM", "Neurologist", "Nerve conduction study advised"),
    ("tingling", 4, "MEDIUM", "Neurologist", "Check for neuropathy or compression"),
    ("weakness", 6, "MEDIUM", "Neurologist", "Muscle strength evaluation required"),
    ("paralysis", 10, "HIGH", "Neurologist", "Emergency medical attention needed"),
    ("memory loss", 6, "MEDIUM", "Neurologist", "Cognitive assessment and MRI"),
    ("confusion", 7, "HIGH", "Neurologist", "Urgent neurological evaluation"),
    ("difficulty speaking", 8, "HIGH", "Neurologist", "Possible stroke, emergency care"),
    ("vision problems", 6, "MEDIUM", "Ophthalmologist", "Eye examination required"),
    ("blurred vision", 5, "MEDIUM", "Ophthalmologist", "Refraction test and eye check"),
    ("double vision", 7, "HIGH", "Ophthalmologist", "Neurological and ophthalmological evaluation"),
    ("hearing loss", 6, "MEDIUM", "ENT Specialist", "Audiometry and ENT consultation"),
    ("tinnitus", 4, "MEDIUM", "ENT Specialist", "Hearing evaluation and sound therapy"),
    
    # Musculoskeletal
    ("muscle weakness", 5, "MEDIUM", "Orthopedic", "EMG and nerve conduction studies"),
    ("stiffness", 4, "MEDIUM", "Orthopedic", "Physical therapy and stretching"),
    ("swelling", 4, "MEDIUM", "Orthopedic", "RICE therapy and anti-inflammatories"),
    ("redness", 4, "MEDIUM", "Orthopedic", "Possible infection, medical evaluation"),
    ("limited mobility", 5, "MEDIUM", "Orthopedic", "Physical therapy and joint evaluation"),
    ("fracture", 8, "HIGH", "Orthopedic", "X-ray and immobilization required"),
    ("sprain", 6, "MEDIUM", "Orthopedic", "RICE therapy and possible bracing"),
    
    # Dermatological
    ("hives", 4, "MEDIUM", "Dermatologist", "Antihistamines and identify allergens"),
    ("redness", 3, "LOW", "Dermatologist", "Topical steroids and avoid irritants"),
    ("blisters", 5, "MEDIUM", "Dermatologist", "Keep clean and avoid popping"),
    ("ulcers", 6, "MEDIUM", "Dermatologist", "Wound care and possible antibiotics"),
    ("sores", 5, "MEDIUM", "Dermatologist", "Keep clean and monitor for infection"),
    ("dry skin", 2, "LOW", "Dermatologist", "Moisturize regularly"),
    ("oily skin", 2, "LOW", "Dermatologist", "Proper cleansing and oil control"),
    ("hair loss", 4, "MEDIUM", "Dermatologist", "Check for nutritional deficiencies"),
    ("nail changes", 4, "MEDIUM", "Dermatologist", "May indicate systemic disease"),
    ("skin discoloration", 5, "MEDIUM", "Dermatologist", "Biopsy may be needed"),
    
    # Genitourinary
    ("painful urination", 6, "MEDIUM", "Nephrologist", "Urine culture and antibiotics"),
    ("urgency", 4, "MEDIUM", "Nephrologist", "Bladder training and evaluation"),
    ("blood in urine", 8, "HIGH", "Nephrologist", "Immediate urological evaluation"),
    ("cloudy urine", 5, "MEDIUM", "Nephrologist", "Urine test for infection"),
    ("kidney pain", 7, "HIGH", "Nephrologist", "Ultrasound and renal function tests"),
    ("flank pain", 7, "HIGH", "Nephrologist", "Possible kidney stone, imaging needed"),
    ("testicular pain", 7, "HIGH", "Urologist", "Ultrasound and urgent evaluation"),
    ("penile discharge", 6, "MEDIUM", "Urologist", "STD testing and antibiotics"),
    ("vaginal discharge", 5, "MEDIUM", "Gynecologist", "Pelvic exam and culture"),
    ("vaginal itching", 4, "MEDIUM", "Gynecologist", "Antifungal treatment may be needed"),
    ("pelvic pain", 6, "MEDIUM", "Gynecologist", "Pelvic ultrasound and evaluation"),
    ("menstrual cramps", 4, "MEDIUM", "Gynecologist", "NSAIDs and heat therapy"),
    ("heavy bleeding", 7, "HIGH", "Gynecologist", "Hormonal evaluation and possible D&C"),
    ("missed period", 5, "MEDIUM", "Gynecologist", "Pregnancy test and hormonal workup"),
    
    # Psychological
    ("depression", 6, "MEDIUM", "Psychiatrist", "Therapy and antidepressant evaluation"),
    ("insomnia", 4, "MEDIUM", "Psychiatrist", "Sleep hygiene and cognitive therapy"),
    ("fatigue", 5, "MEDIUM", "General Physician", "Comprehensive evaluation for cause"),
    ("lethargy", 5, "MEDIUM", "General Physician", "Check thyroid and vitamin levels"),
    ("mood swings", 5, "MEDIUM", "Psychiatrist", "Hormonal and psychological evaluation"),
    ("irritability", 4, "MEDIUM", "Psychiatrist", "Stress management and therapy"),
    ("lack of concentration", 5, "MEDIUM", "Psychiatrist", "Cognitive assessment needed"),
    ("suicidal thoughts", 10, "HIGH", "Psychiatrist", "Immediate crisis intervention required"),
    
    # General
    ("malaise", 4, "MEDIUM", "General Physician", "General health checkup recommended"),
    ("loss of energy", 5, "MEDIUM", "General Physician", "Check for anemia and thyroid issues"),
    ("dehydration", 6, "MEDIUM", "General Physician", "IV fluids and electrolyte replacement"),
    ("thirst", 3, "LOW", "General Physician", "Increase fluid intake"),
    ("excessive hunger", 5, "MEDIUM", "Endocrinologist", "Check blood sugar and thyroid"),
    ("excessive thirst", 6, "MEDIUM", "Endocrinologist", "Diabetes screening required"),
    ("frequent infections", 6, "MEDIUM", "Immunologist", "Immune system evaluation"),
    ("slow healing", 5, "MEDIUM", "General Physician", "Check diabetes and nutritional status"),
    ("bruising easily", 5, "MEDIUM", "Hematologist", "Coagulation profile and platelet count"),
]

# Create DataFrame for new symptoms
new_rows = []
for symptom, severity, risk, doctor, advice in additional_symptoms:
    new_rows.append({
        'text': symptom,
        'severity_score': severity,
        'risk': risk,
        'doctor': doctor,
        'advice': advice
    })

# Add some variations of common symptoms
symptom_variations = [
    ("mild fever", 2, "LOW", "General Physician", "Rest and monitor temperature"),
    ("high temperature", 4, "MEDIUM", "General Physician", "Antipyretics and doctor consultation"),
    ("persistent cough", 5, "MEDIUM", "Pulmonologist", "Chest X-ray recommended"),
    ("dry throat", 2, "LOW", "ENT Specialist", "Warm fluids and lozenges"),
    ("muscle cramps", 4, "MEDIUM", "Orthopedic", "Electrolyte replacement and stretching"),
    ("eye pain", 5, "MEDIUM", "Ophthalmologist", "Eye examination required"),
    ("ear pressure", 4, "MEDIUM", "ENT Specialist", "Decongestants and Valsalva maneuver"),
    ("balance problems", 6, "MEDIUM", "Neurologist", "Vestibular testing needed"),
]

for symptom, severity, risk, doctor, advice in symptom_variations:
    new_rows.append({
        'text': symptom,
        'severity_score': severity,
        'risk': risk,
        'doctor': doctor,
        'advice': advice
    })

# Convert to DataFrame
new_df = pd.DataFrame(new_rows)

# Combine with existing data
enhanced_df = pd.concat([df, new_df], ignore_index=True)

# Remove any duplicates
enhanced_df = enhanced_df.drop_duplicates(subset=['text'], keep='first')

# Save to new file
enhanced_df.to_csv('training_data_enhanced.csv', index=False)

print(f"Enhanced training data: {len(enhanced_df)} rows (added {len(enhanced_df) - len(df)} new symptoms)")
print(f"Original: {len(df)} rows, Enhanced: {len(enhanced_df)} rows")

# Also create a backup of original
df.to_csv('training_data_backup.csv', index=False)
print("Backup saved as 'training_data_backup.csv'")

# Show sample of new symptoms
print("\nSample of newly added symptoms:")
for i in range(min(10, len(new_df))):
    row = new_df.iloc[i]
    print(f"{row['text']:25s} - Severity: {row['severity_score']}, Risk: {row['risk']}, Doctor: {row['doctor']}")