import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.metrics.pairwise import cosine_similarity
from flask import Response, stream_with_context
import json
import time
import os
import joblib
import pandas as pd

# ================= APP =================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ================= PATH =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= ML LOAD =================
disease_model = joblib.load("disease_model.pkl")
disease_vectorizer = joblib.load("disease_vectorizer.pkl")

disease_data = pd.read_csv("disease_dataset.csv")

# ===== CLEAN DATASET =====
disease_data["symptoms"] = (
    disease_data["symptoms"]
    .astype(str)
    .str.lower()
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

disease_data["disease"] = disease_data["disease"].astype(str).str.strip()
disease_data["specialist"] = disease_data["specialist"].astype(str).str.lower().str.strip()
disease_data["advice"] = disease_data["advice"].astype(str).str.strip()

# ================= TRAINING DATA =================
training_data = pd.read_csv(
    os.path.join(BASE_DIR, "training_data.csv"),
    encoding="latin1"
)
training_data["text"] = training_data["text"].str.lower().str.strip()
training_data["doctor"] = training_data["doctor"].str.lower().str.strip()
training_data["risk"] = training_data["risk"].str.strip()

# ================= DOCTORS DATA =================
doctors_data = pd.read_csv(
    os.path.join(BASE_DIR, "doctors_ahmedabad.csv"),
    encoding="latin1"
)
doctors_data["specialization"] = doctors_data["specialization"].str.lower().str.strip()
 # ================= DISEASE SMART MATCH =================


def smart_match_disease(user_symptoms):
    user_symptoms = user_symptoms.lower().strip()

    # Vectorize input and dataset
    input_vec = disease_vectorizer.transform([user_symptoms])
    dataset_vec = disease_vectorizer.transform(disease_data["symptoms"])

    # Compute similarity
    similarity = cosine_similarity(input_vec, dataset_vec)
    best_index = similarity.argmax()

    return disease_data.iloc[best_index]

# ================= SPECIALIZATION MAP =================
SPECIALIZATION_MAP = {
   

    "general physician": "general physician",
    "self care": "general physician",
    "cardiologist": "cardiologist",
    "emergency / cardiologist": "cardiologist",
    "emergency": "emergency",
    "neurologist": "neurologist",
    "orthopedic": "orthopedic",
    "gynecologist": "gynecologist",
    "pulmonologist": "pulmonologist",
    "gastroenterologist": "gastroenterologist",
    "dermatologist": "dermatologist",
    "ent": "ent",
    "ent specialist": "ent",
    "pediatrician": "pediatrician",
    "psychiatrist": "psychiatrist",
    "nephrologist": "nephrologist",
    "dentist": "dentist"
}

# ================= DOCTOR MATCH HELPER =================
def get_doctors_by_specialization(doctor_text):
    doctor_text = doctor_text.lower().strip()

    specialization = "general physician"
    for key, value in SPECIALIZATION_MAP.items():
        if key in doctor_text:
            specialization = value
            break

    matched = doctors_data[
        doctors_data["specialization"].str.contains(specialization, na=False)
    ]

    doctors = []
    for _, row in matched.head(5).iterrows():
        doctors.append({
            "name": row["doctor_name"],
            "hospital": row["hospital"],
            "area": row["area"],
            "contact": str(row["contact"]),
            "experience": int(row["experience_years"]),
            "specialization": row["specialization"].title()
        })

    return doctors

# ================= MYSQL =================
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "health"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)
# ===== FIX MYSQL CONNECTION CLOSE ERROR =====

# ================= ML PREDICTION FUNCTION =================
def predict_from_symptoms(user_text):
    user_text = user_text.lower().strip()

    # Transform using trained vectorizer
    X = disease_vectorizer.transform([user_text])

    # Predict disease
    predicted_disease = disease_model.predict(X)[0]

    # Confidence score (if available)
    try:
        prob = disease_model.predict_proba(X).max() * 100
    except:
        prob = 75  # fallback if model doesn't support probability

    # Find dataset row for advice/specialist
    match = disease_data[disease_data["disease"] == predicted_disease]

    if not match.empty:
        row = match.iloc[0]
        specialist = row["specialist"]
        advice = row["advice"]
    else:
        specialist = "general physician"
        advice = "Consult a doctor for further evaluation."

    return {
        "disease": predicted_disease,
        "specialist": specialist,
        "advice": advice,
        "confidence": round(prob, 2)
    }
# ================= HOME =================
@app.route("/")
def home():
    return "AI Health Backend Running"

# ================= SIGNUP =================
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    contact = data.get("contact")
    email = data.get("email")
    password = data.get("password")
    age = data.get("age")
    gender = data.get("gender")

    if not all([name, contact, email, password]):
        return jsonify({"message": "All fields required"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"message": "Email already exists"}), 400

    password_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (name, contact, email, password_hash, age, gender) VALUES (%s,%s,%s,%s,%s,%s)",
        (name, contact, email, password_hash, age, gender)
    )
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Signup successful"})

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"message": "Invalid password"}), 401

    return jsonify({
        "message": "Login successful",
        "name": user["name"],
        "email": user["email"],
        "contact": user["contact"],
        "age": user.get("age"),
        "gender": user.get("gender"),
        "user_id": user["id"]
    })
@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    try:
        import pandas as pd

        df = pd.read_csv('training_data.csv', encoding='latin1')

        # Get all unique symptom phrases from the 'text' column
        symptoms = df['text'].astype(str).str.lower().str.strip().unique().tolist()
        
        # Remove any empty strings
        symptoms = [s for s in symptoms if s and s != 'nan']
        
        # Sort alphabetically for better UX
        symptoms.sort()
        
        return jsonify(symptoms)

    except Exception as e:
        print(f"Error in /symptoms endpoint: {e}")
        return jsonify({"error": str(e)}), 500
# ================= MULTI SYMPTOM PARSER =================
def extract_symptoms(user_text):

    user_text = user_text.lower()

    separators = [",", " and ", "&", " with ", ";"]

    for sep in separators:
        user_text = user_text.replace(sep, "|")

    # First split by separators
    symptoms = [s.strip() for s in user_text.split("|") if len(s.strip()) > 2]
    
    # If we only got one symptom and it contains spaces, we need to check
    # if it contains known multi-word symptoms
    if len(symptoms) == 1 and " " in symptoms[0]:
        single_symptom = symptoms[0]
        
        # Common multi-word symptoms in order of length (longest first)
        common_multiword_symptoms = [
            "shortness of breath", "chest pain", "stomach pain", "abdominal pain",
            "night sweats", "weight loss", "blurred vision", "sensitivity to light",
            "dry skin", "red patches", "silvery scales", "loss of appetite",
            "high fever", "low fever", "mild fever", "severe headache"
        ]
        
        # Check if the single symptom is actually multiple symptoms concatenated
        # Try to extract known multi-word symptoms first
        extracted_symptoms = []
        remaining_text = single_symptom
        
        # Sort by length (longest first) to match "shortness of breath" before "chest pain"
        for multiword in sorted(common_multiword_symptoms, key=len, reverse=True):
            if multiword in remaining_text:
                extracted_symptoms.append(multiword)
                # Remove the matched symptom from remaining text
                remaining_text = remaining_text.replace(multiword, " ").strip()
        
        # If we found any multi-word symptoms, add the remaining words as individual symptoms
        if extracted_symptoms:
            # Add any remaining words (single-word symptoms)
            remaining_words = [w.strip() for w in remaining_text.split() if len(w.strip()) > 2]
            symptoms = extracted_symptoms + remaining_words
        else:
            # No multi-word symptoms found, check if we should split by spaces
            word_count = len(single_symptom.split())
            if word_count > 2:
                # If it's a long phrase with multiple words, split it
                words = [w.strip() for w in single_symptom.split() if len(w.strip()) > 2]
                symptoms = words
    
    # Also handle cases where user might have typed symptoms with just spaces
    # but we still want to split them (e.g., "fever cough headache")
    # This is already covered above, but keep as fallback
    if len(symptoms) == 1 and " " in symptoms[0] and len(symptoms[0].split()) > 2:
        # If it's a long phrase with multiple words, split it
        words = [w.strip() for w in symptoms[0].split() if len(w.strip()) > 2]
        symptoms = words

    return list(set(symptoms))
# ================= MULTI SYMPTOM PREDICTION =================
def predict_from_multiple_symptoms(user_text):

    user_text = user_text.lower().strip()
    
    if not user_text:
        return None

    # Extract symptoms using the improved function
    user_symptoms = extract_symptoms(user_text)
    
    if not user_symptoms:
        return None

    # ===== 1. DIRECT PHRASE MATCH (exact or substring) =====
    for _, row in disease_data.iterrows():
        symptoms_phrase = row["symptoms"].lower().strip()

        # Exact match or substring match in either direction
        if (symptoms_phrase == user_text or
            user_text in symptoms_phrase or
            symptoms_phrase in user_text):
            return {
                "disease": row["disease"],
                "specialist": row["specialist"],
                "advice": row["advice"],
                "confidence": 100
            }

    # ===== 2. IMPROVED SYMPTOM PHRASE MATCHING =====
    best_row = None
    best_score = 0

    # Convert user symptoms to lowercase set for matching
    user_symptoms_set = set(user_symptoms)
    
    for _, row in disease_data.iterrows():
        dataset_symptoms_phrase = row["symptoms"].lower().strip()
        
        # Extract symptoms from dataset entry (some entries have multiple symptoms)
        dataset_symptoms = extract_symptoms(dataset_symptoms_phrase)
        dataset_symptoms_set = set(dataset_symptoms)
        
        # Count exact symptom matches
        exact_matches = len(user_symptoms_set.intersection(dataset_symptoms_set))
        
        # Count partial matches (substring matches)
        partial_matches = 0
        for user_symptom in user_symptoms_set:
            for dataset_symptom in dataset_symptoms_set:
                if user_symptom in dataset_symptom or dataset_symptom in user_symptom:
                    partial_matches += 1
                    break  # Count each user symptom only once
        
        # Calculate scores
        if len(user_symptoms_set) > 0:
            # Exact match score (higher weight)
            exact_score = exact_matches / len(user_symptoms_set)
            
            # Partial match score (lower weight)
            partial_score = (partial_matches - exact_matches) / len(user_symptoms_set) * 0.5
            
            # Dataset coverage score (how many of dataset symptoms are matched)
            dataset_coverage = exact_matches / max(len(dataset_symptoms_set), 1)
            
            # Combined score with weights
            score = (exact_score * 0.7) + (partial_score * 0.2) + (dataset_coverage * 0.1)
            
            # Boost score if we have multiple exact matches
            if exact_matches >= 2:
                score *= 1.2  # 20% boost for multiple matches
        else:
            score = 0

        if score > best_score:
            best_score = score
            best_row = row

    if best_row is None:
        return None

    return {
        "disease": best_row["disease"],
        "specialist": best_row["specialist"],
        "advice": best_row["advice"],
        "confidence": round(min(best_score * 100, 100), 2)
    }
# ================= TRIAGE =================
@app.route("/triage", methods=["POST"])
def triage():

    data = request.get_json(silent=True) or {}
    text = data.get("message", "").lower().strip()
    user_id = data.get("user_id")

    def generate():

        if not text:
            yield json.dumps({
                "mode": "chat",
                "message": "Please enter symptoms."
            }) + "\n"
            return

        # Check for vitals system message
        if text.startswith("system log: patient vitals"):
            yield json.dumps({
                "type": "result",
                "data": {
                    "mode": "chat",
                    "advice": "Vitals successfully integrated into your session. Please describe the symptoms you are experiencing so I can complete your triage."
                }
            }) + "\n"
            return
            
        # Step 1: Start response
        yield json.dumps({
            "type": "start",
            "message": "Analyzing symptoms..."
        }) + "\n"

        time.sleep(0.5)

        # Step 2: Prediction
        result = predict_from_multiple_symptoms(text)

        if result is None:
            yield json.dumps({
                "type": "error",
                "message": "Unable to detect symptoms."
            }) + "\n"
            return

        yield json.dumps({
            "type": "progress",
            "message": "Matching disease..."
        }) + "\n"

        time.sleep(0.5)

        # Step 3: Doctor recommendation
        recommended_doctors = get_doctors_by_specialization(result["specialist"])

        yield json.dumps({
            "type": "progress",
            "message": "Finding doctors..."
        }) + "\n"

        time.sleep(0.5)

        # Step 4: Final result
        final_data = {
            "mode": "medical",
            "symptoms": extract_symptoms(text),
            "disease": result["disease"],
            "risk": "Predicted",
            "doctor": result["specialist"].title(),
            "severity": 85,
            "advice": result["advice"],
            "recommended_doctors": recommended_doctors
        }

        yield json.dumps({
            "type": "result",
            "data": final_data
        }) + "\n"

        # Step 5: Save history
        if user_id:
            try:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    """
                    INSERT INTO history
                    (user_id, symptoms, severity, risk, doctor, advice)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        user_id,
                        text,
                        85,
                        "Predicted",
                        result["specialist"],
                        result["advice"]
                    )
                )
                mysql.connection.commit()
                cursor.close()
            except Exception as e:
                print("History save error:", e)

    return Response(stream_with_context(generate()), content_type="application/x-ndjson")
# ================= DISEASE PREDICTION =================
@app.route("/predict_disease", methods=["POST"])
def predict_disease():
    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", "")

    if isinstance(symptoms, list):
        symptoms = " ".join(symptoms)

    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400

    result = predict_from_symptoms(symptoms)

    recommended_doctors = get_doctors_by_specialization(result["specialist"])

    return jsonify({
        "predicted_disease": result["disease"],
        "confidence": result["confidence"],
        "specialist": result["specialist"],
        "advice": result["advice"],
        "recommended_doctors": recommended_doctors
    })
# ================= HISTORY =================
@app.route("/history/<int:user_id>")
def history(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT symptoms, severity, risk, doctor, advice, created_at
        FROM history
        WHERE user_id=%s
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)


@app.route("/recommend", methods=["POST"])
def recommend_doctors():
    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", "")
    
    if isinstance(symptoms, list):
        symptoms = " ".join(symptoms)
        
    symptoms = symptoms.lower().strip()
    
    if not symptoms:
        return jsonify([])

    # 1. Try to find exact match in training data
    matches = training_data[training_data["text"] == symptoms]
    
    doctor_type = None
    
    if not matches.empty:
        doctor_type = matches.iloc[0]["doctor"]
    else:
        # 2. Key-word based mapping (Simple NLP)
        # We define a fallback map for common symptoms -> specialists
        SYMPTOM_KEYWORD_MAP = {
            "heart": "cardiologist", "chest": "cardiologist", "breath": "cardiologist", "palpitation": "cardiologist",
            "head": "neurologist", "dizzy": "neurologist", "faint": "neurologist", "seizure": "neurologist", "stroke": "neurologist",
            "bone": "orthopedic", "joint": "orthopedic", "fracture": "orthopedic", "knee": "orthopedic", "back": "orthopedic",
            "skin": "dermatologist", "rash": "dermatologist", "itch": "dermatologist", "acne": "dermatologist",
            "stomach": "gastroenterologist", "abdominal": "gastroenterologist", "vomit": "gastroenterologist", "diarrhea": "gastroenterologist",
            "throat": "ent", "ear": "ent", "nose": "ent", "cold": "general physician", "flu": "general physician", "fever": "general physician",
            "lung": "pulmonologist", "cough": "pulmonologist", "asthma": "pulmonologist",
            "tooth": "dentist", "gum": "dentist",
            "child": "pediatrician", "baby": "pediatrician",
            "mood": "psychiatrist", "anxiety": "psychiatrist", "depression": "psychiatrist",
            "kidney": "nephrologist", "urine": "nephrologist"
        }
        
        for keyword, specialist in SYMPTOM_KEYWORD_MAP.items():
            if keyword in symptoms:
                doctor_type = specialist
                break
        
        # 3. If still no match, check if the symptom string itself contains a specialist name
        if not doctor_type:
            for key, value in SPECIALIZATION_MAP.items():
                if key in symptoms:
                    doctor_type = value
                    break

    # Default if nothing found: General Physician
    if not doctor_type:
        doctor_type = "general physician"

    # 4. Get doctors by specialization
    recommended = get_doctors_by_specialization(doctor_type)
    
    # 5. If specific specialization yielded no results, return some random doctors instead of empty
    # so the frontend shows *some* real data instead of static mocks
    if not recommended:
        # Fallback to general physicians or just any top doctors
        recommended = get_doctors_by_specialization("general physician")
        if not recommended: # If even that fails, specific hardcoded fallback or random sample from DB
             # Just sample 3 random rows from doctors_data
            sample = doctors_data.sample(3)
            for _, row in sample.iterrows():
                recommended.append({
                    "name": row["doctor_name"],
                    "hospital": row["hospital"],
                    "area": row["area"],
                    "contact": str(row["contact"]),
                    "experience": int(row["experience_years"]),
                    "specialization": row["specialization"].title()
                })

    # 6. Enhance with mock live data (availability, score)
    import random
    for doc in recommended:
        doc["matchScore"] = random.randint(85, 99)
        doc["availability"] = random.choice(["Available Now", "In Surgery (1h)", "On Call", "Available in 30m"])
        doc["rating"] = round(random.uniform(4.5, 5.0), 1)
        doc["id"] = str(random.randint(1000, 9999))

    return jsonify(recommended)

# ================= QUEUE =================
@app.route("/queue", methods=["GET"])
def get_queue():
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT 
            h.id, 
            u.name, 
            u.contact, 
            u.age,
            u.gender,
            h.symptoms, 
            h.severity, 
            h.risk, 
            h.doctor, 
            h.created_at
        FROM history h
        JOIN users u ON h.user_id = u.id
        ORDER BY h.created_at DESC
        LIMIT 50
        """
    )
    rows = cursor.fetchall()
    cursor.close()

    queue_data = []
    for row in rows:
        # Parse symptoms string if it looks like a list or keep as is
        # The history table might store symptoms as raw string from user input
        symptoms_list = [s.strip() for s in row["symptoms"].split(',')] if row["symptoms"] else []

        queue_data.append({
            "id": str(row["id"]),
            "name": row["name"],
            # Use real age/gender if available, otherwise fallback to defaults
            "age": row.get("age") or 30, 
            "gender": row.get("gender") or "Unknown", 
            "severity": row["risk"].lower().strip() if row["risk"] else "medium",
            "symptoms": symptoms_list,
            "vitals": { # Mock vitals for now as we don't track them yet
                "heartRate": 80,
                "temperature": 98.6,
                "bloodPressure": "120/80",
                "oxygenLevel": 98,
            },
            "timestamp": row["created_at"]
        })

    return jsonify(queue_data)

import tempfile
from vitals_analyzer import process_vitals_video

# ================= VITALS ANALYSIS =================
@app.route("/analyze_vitals", methods=["POST"])
def analyze_vitals():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400
        
    video_file = request.files["video"]
    if video_file.filename == "":
        return jsonify({"error": "Empty video file"}), 400
        
    # Save temporarily
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "temp_vitals.webm")
    
    try:
        video_file.save(temp_path)
        
        # Analyze
        results = process_vitals_video(temp_path)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return jsonify(results)
    except Exception as e:
        print(f"Error in vitals analysis: {e}")
        return jsonify({"error": str(e)}), 500

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
