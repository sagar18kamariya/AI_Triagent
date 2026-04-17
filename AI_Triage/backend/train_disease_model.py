import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# =============================
# LOAD DISEASE DATASET
# =============================
df = pd.read_csv("disease_dataset.csv")

X = df["symptoms"]
y = df["disease"]

# =============================
# TEXT VECTORIZATION
# =============================
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1,2)
)

X_vectorized = vectorizer.fit_transform(X)

# =============================
# TRAIN MODEL
# =============================
model = LogisticRegression(max_iter=1000)
model.fit(X_vectorized, y)

# =============================
# SAVE NEW MODEL (DIFFERENT NAME)
# =============================
joblib.dump(model, "disease_model.pkl")
joblib.dump(vectorizer, "disease_vectorizer.pkl")

print("[SUCCESS] Disease Model trained successfully")
print("[FILES] Files created: disease_model.pkl, disease_vectorizer.pkl")