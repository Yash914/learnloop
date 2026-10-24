"""Optional Logistic Regression baseline trained on real saved quiz attempts.

The model is only fitted when enough recorded attempts and both outcome classes exist.
It estimates the chance of a correct answer from prior topic accuracy, previous attempts,
and difficulty. Until then, the app uses its transparent history-based recommender.
"""
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from src.quiz_engine import _connect

DIFFICULTY = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}

def train_correctness_model(min_rows=20):
    conn = _connect()
    rows = conn.execute(
        "SELECT topic_accuracy_before, attempts_before, difficulty, correct FROM attempts"
    ).fetchall()
    conn.close()

    if len(rows) < min_rows or len({int(row[3]) for row in rows}) < 2:
        return None

    X = [[float(acc), int(attempts), DIFFICULTY.get(difficulty, 0)]
         for acc, attempts, difficulty, _ in rows]
    y = [int(row[3]) for row in rows]
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=42))
    model.fit(X, y)
    return model

def predict_correctness(topic_accuracy, attempts_before, difficulty):
    model = train_correctness_model()
    if model is None:
        return None
    features = [[float(topic_accuracy), int(attempts_before), DIFFICULTY.get(difficulty, 0)]]
    return float(model.predict_proba(features)[0][1])
