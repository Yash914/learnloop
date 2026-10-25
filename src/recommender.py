"""Personalized topic recommendations using quiz history and Logistic Regression."""
from src.quiz_engine import QUESTION_BANK, _connect
from src.model import train_correctness_model

DIFFICULTY_SCORE = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}


def recommend_topic():
    # Keep the available subject/topic combinations from the built-in question bank.
    topics = {}
    for question in QUESTION_BANK:
        key = (question["subject"], question["topic"])
        topics.setdefault(key, question["difficulty"])

    conn = _connect()
    rows = conn.execute(
        "SELECT subject, topic, AVG(correct), COUNT(*) "
        "FROM attempts GROUP BY subject, topic"
    ).fetchall()
    conn.close()

    if not rows:
        return {
            "subject": "Machine Learning",
            "topic": "Linear Regression",
            "reason": (
                "Start with a beginner-friendly topic. As you answer quizzes, "
                "LearnLoop will use your saved performance to personalize recommendations."
            ),
        }

    history = {
        (subject, topic): (float(accuracy), int(count))
        for subject, topic, accuracy, count in rows
    }

    # Fit once per recommendation request. The model is available only after
    # enough saved attempts exist and both correct and incorrect answers occur.
    model = train_correctness_model()
    ranked = []

    for (subject, topic), difficulty in topics.items():
        accuracy, count = history.get((subject, topic), (0.5, 0))

        if model is not None:
            features = [[accuracy, count, DIFFICULTY_SCORE.get(difficulty, 0)]]
            probability_correct = float(model.predict_proba(features)[0][1])
            # Prioritize topics with lower predicted success, with a smaller
            # historical-accuracy component and a bonus for unattempted topics.
            score = (
                0.7 * (1.0 - probability_correct)
                + 0.3 * (1.0 - accuracy)
                + 0.15 / (count + 1)
            )
            if count == 0:
                reason = (
                    "You haven't practised this topic yet. The model estimates "
                    f"a {probability_correct:.0%} chance of a correct answer, "
                    "so it is a useful topic to explore."
                )
            else:
                reason = (
                    f"Your historical accuracy is {accuracy:.0%}; the Logistic "
                    f"Regression model estimates a {probability_correct:.0%} "
                    "chance of a correct answer. More practice may help."
                )
        elif count > 0:
            # Fallback until there is sufficient data to train Logistic Regression.
            score = (1.0 - accuracy) + 0.15 / (count + 1)
            reason = (
                f"Your accuracy here is {accuracy:.0%}. A little more practice "
                "could help. Logistic Regression recommendations become "
                "available after enough quiz history is collected."
            )
        else:
            score = 0.55
            reason = (
                "You haven't practised this topic yet, so it's a good chance "
                "to explore something new."
            )

        ranked.append((score, subject, topic, reason))

    ranked.sort(reverse=True)
    _, subject, topic, reason = ranked[0]
    return {"subject": subject, "topic": topic, "reason": reason}
