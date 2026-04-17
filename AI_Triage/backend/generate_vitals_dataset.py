import pandas as pd
import random

# Load the base disease dataset
df = pd.read_csv('disease_dataset.csv')

dataset = []

# Rules for synthetic data generation
# heart_rate_range, possible_emotions, risk
disease_profiles = {
    'Heart Attack': {'hr': (110, 150), 'emotions': ['fear', 'sad', 'surprise'], 'risk': 'Critical'},
    'Heart Failure': {'hr': (100, 130), 'emotions': ['fear', 'sad'], 'risk': 'High'},
    'Arrhythmia': {'hr': (110, 160), 'emotions': ['fear', 'neutral'], 'risk': 'High'},
    'Angina': {'hr': (100, 140), 'emotions': ['fear', 'sad'], 'risk': 'High'},
    'Anxiety Disorder': {'hr': (100, 130), 'emotions': ['fear', 'sad'], 'risk': 'Medium'},
    'Hypertension': {'hr': (85, 110), 'emotions': ['neutral', 'angry'], 'risk': 'Medium'},
    'Hyperthyroidism': {'hr': (90, 120), 'emotions': ['neutral', 'fear'], 'risk': 'Medium'},
    'Asthma': {'hr': (90, 120), 'emotions': ['fear', 'sad'], 'risk': 'High'},
    'Pneumonia': {'hr': (90, 120), 'emotions': ['sad', 'neutral'], 'risk': 'High'},
    'COVID-19': {'hr': (80, 110), 'emotions': ['sad', 'neutral', 'fear'], 'risk': 'High'},
    'Depression': {'hr': (50, 75), 'emotions': ['sad', 'neutral'], 'risk': 'Medium'},
    'Hypothyroidism': {'hr': (50, 70), 'emotions': ['sad', 'neutral'], 'risk': 'Low'},
    'Stroke': {'hr': (60, 100), 'emotions': ['fear', 'sad', 'surprise'], 'risk': 'Critical'},
    'Appendicitis': {'hr': (90, 120), 'emotions': ['sad', 'fear'], 'risk': 'Critical'},
    'Migraine': {'hr': (60, 90), 'emotions': ['sad', 'disgust', 'angry'], 'risk': 'Medium'},
}

# General fallback for unmapped diseases
default_profile = {'hr': (60, 90), 'emotions': ['neutral', 'sad'], 'risk': 'Low'}

print("Generating synthetic vitals dataset...")

# Generate 5000 rows
for _ in range(5000):
    row_idx = random.randint(0, len(df)-1)
    base_row = df.iloc[row_idx]
    disease = base_row['disease']
    symptoms = base_row['symptoms']
    
    profile = disease_profiles.get(disease, default_profile)
    
    # Generate variance
    hr = random.randint(profile['hr'][0], profile['hr'][1])
    emotion = random.choice(profile['emotions'])
    risk = profile['risk']
    
    # Randomly drop some symptoms to simulate real-world input variance
    symptom_list = [s.strip() for s in symptoms.split()]
    if len(symptom_list) > 1 and random.random() > 0.5:
        symptom_list.pop(random.randint(0, len(symptom_list)-1))
    
    final_symptoms = " ".join(symptom_list)
    
    dataset.append({
        'heart_rate': hr,
        'emotion': emotion,
        'symptoms': final_symptoms,
        'disease': disease,
        'risk': risk,
        'specialist': base_row['specialist']
    })

synth_df = pd.DataFrame(dataset)
output_path = 'vitals_training_data.csv'
synth_df.to_csv(output_path, index=False)
print(f"Dataset '{output_path}' generated successfully with {len(synth_df)} rows!")
