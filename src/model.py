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


def evaluate_model(min_rows=20):
    """Evaluate correctness prediction with stratified out-of-fold predictions."""
    from collections import Counter
    from sklearn.base import clone
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.model_selection import StratifiedKFold, cross_val_predict

    conn = _connect()
    rows = conn.execute(
        "SELECT topic_accuracy_before, attempts_before, difficulty, correct FROM attempts"
    ).fetchall()
    conn.close()

    labels = [int(row[3]) for row in rows]
    counts = Counter(labels)
    if len(rows) < min_rows or len(counts) < 2:
        return {
            "ready": False,
            "message": "The evaluation is not ready yet. Collect at least 20 answered questions, including both correct and incorrect outcomes, before interpreting model metrics."
        }
    minority_count = min(counts.values())
    folds = min(5, minority_count)
    if folds < 2:
        return {
            "ready": False,
            "message": "There are too few examples in one outcome class for stratified cross-validation. Collect more correct and incorrect answers."
        }

    X = [[float(acc), int(attempts), DIFFICULTY.get(difficulty, 0)]
         for acc, attempts, difficulty, _ in rows]
    y = labels
    estimator = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=500, random_state=42)
    )
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    predicted = cross_val_predict(estimator, X, y, cv=cv, method="predict")
    majority_baseline = max(counts.values()) / len(y)
    return {
        "ready": True,
        "rows": len(y),
        "correct": counts.get(1, 0),
        "incorrect": counts.get(0, 0),
        "folds": folds,
        "accuracy": float(accuracy_score(y, predicted)),
        "precision": float(precision_score(y, predicted, zero_division=0)),
        "recall": float(recall_score(y, predicted, zero_division=0)),
        "f1": float(f1_score(y, predicted, zero_division=0)),
        "baseline_accuracy": float(majority_baseline),
    }
