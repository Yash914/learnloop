"""Topic recommendation using quiz history and an optional trained ML model."""
from src.quiz_engine import QUESTION_BANK, _connect

DIFFICULTY_SCORE = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}

def recommend_topic():
    topics = {}
    for q in QUESTION_BANK:
        key = (q["subject"], q["topic"])
        topics.setdefault(key, q["difficulty"])

    conn = _connect()
    rows = conn.execute(
        "SELECT subject, topic, AVG(correct), COUNT(*) FROM attempts GROUP BY subject, topic"
    ).fetchall()
    conn.close()

    if not rows:
        return {
            "subject": "Machine Learning",
            "topic": "Linear Regression",
            "reason": "Start with a beginner-friendly topic. Your recommendations will become more personal as you answer questions."
        }

    history = {(subject, topic): (float(acc), int(count))
               for subject, topic, acc, count in rows}

    # Prefer topics with lower accuracy; unseen topics get a gentle exploration bonus.
    ranked = []
    for (subject, topic), difficulty in topics.items():
        if (subject, topic) in history:
            accuracy, count = history[(subject, topic)]
            score = (1.0 - accuracy) + 0.15 / (count + 1)
            reason = f"Your accuracy here is {accuracy:.0%}. A little more practice could help."
        else:
            score = 0.55
            reason = "You haven't practised this topic yet, so it's a good chance to explore something new."
        ranked.append((score, subject, topic, reason))

    ranked.sort(reverse=True)
    _, subject, topic, reason = ranked[0]
    return {"subject": subject, "topic": topic, "reason": reason}
