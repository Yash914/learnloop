"""Quiz question bank and local SQLite attempt history.

The built-in question bank makes the app usable without an API key.
An LLM question generator can be added later behind the same get_questions() interface.
"""
import random
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "learnloop.db"

QUESTION_BANK = [
    {"subject":"Python","topic":"Variables & Data Types","difficulty":"Beginner","question":"Which Python type stores True or False?","options":["str","bool","int","list"],"answer":"bool","explanation":"The bool type represents the two Boolean values: True and False."},
    {"subject":"Python","topic":"Variables & Data Types","difficulty":"Beginner","question":"What is the result of type(3.5)?","options":["int","str","float","bool"],"answer":"float","explanation":"A number with a decimal point is a float in Python."},
    {"subject":"Python","topic":"Variables & Data Types","difficulty":"Beginner","question":"Which symbol starts a single-line comment in Python?","options":["//","#","<!--","/*"],"answer":"#","explanation":"Python uses # to begin a single-line comment."},
    {"subject":"Python","topic":"Loops","difficulty":"Beginner","question":"How many times does range(3) iterate in a for loop?","options":["2","3","4","It never iterates"],"answer":"3","explanation":"range(3) produces 0, 1, and 2: three values."},
    {"subject":"Python","topic":"Loops","difficulty":"Intermediate","question":"Which keyword skips to the next loop iteration?","options":["stop","pass","continue","break"],"answer":"continue","explanation":"continue skips the remaining body and starts the next iteration."},
    {"subject":"Python","topic":"Functions","difficulty":"Beginner","question":"Which keyword defines a function in Python?","options":["function","def","fun","define"],"answer":"def","explanation":"A Python function is declared using the def keyword."},
    {"subject":"Machine Learning","topic":"Linear Regression","difficulty":"Beginner","question":"What does linear regression commonly predict?","options":["A continuous numeric value","Only image labels","Clusters without labels","A database schema"],"answer":"A continuous numeric value","explanation":"Linear regression models a relationship between features and a continuous target."},
    {"subject":"Machine Learning","topic":"Linear Regression","difficulty":"Beginner","question":"In y = mx + c, what does m represent?","options":["The intercept","The slope","The predicted class","The error count"],"answer":"The slope","explanation":"m is the slope, describing how much y changes for a one-unit increase in x."},
    {"subject":"Machine Learning","topic":"Linear Regression","difficulty":"Intermediate","question":"Which metric is the average of squared prediction errors?","options":["Accuracy","Recall","Mean Squared Error","R-squared only"],"answer":"Mean Squared Error","explanation":"MSE averages the squared differences between actual and predicted values."},
    {"subject":"Machine Learning","topic":"Classification","difficulty":"Beginner","question":"Which is an example of binary classification?","options":["Predicting tomorrow's temperature","Grouping customers without labels","Spam or not spam","Predicting house price"],"answer":"Spam or not spam","explanation":"Binary classification assigns each example to one of two classes."},
    {"subject":"Machine Learning","topic":"Classification","difficulty":"Intermediate","question":"What does a model's precision measure?","options":["Correct positives among predicted positives","Correct predictions among all samples","Actual positives found","Average squared error"],"answer":"Correct positives among predicted positives","explanation":"Precision = TP / (TP + FP). It tells us how many predicted positives were truly positive."},
    {"subject":"Machine Learning","topic":"Model Evaluation","difficulty":"Beginner","question":"Why keep a test set?","options":["To train on it repeatedly","To estimate performance on unseen data","To increase missing values","To select column names"],"answer":"To estimate performance on unseen data","explanation":"A held-out test set helps estimate how well a model generalizes."},
    {"subject":"DBMS","topic":"SQL Basics","difficulty":"Beginner","question":"Which SQL command retrieves data from a table?","options":["FETCH ALL","SELECT","PULL","OPEN"],"answer":"SELECT","explanation":"SELECT is used to query data from one or more tables."},
    {"subject":"DBMS","topic":"SQL Basics","difficulty":"Beginner","question":"Which clause filters rows before grouping?","options":["ORDER BY","HAVING","WHERE","GROUP BY"],"answer":"WHERE","explanation":"WHERE filters individual rows; HAVING filters groups after aggregation."},
    {"subject":"DBMS","topic":"Keys & Constraints","difficulty":"Beginner","question":"What does a primary key do?","options":["Allows duplicate row identifiers","Uniquely identifies each row","Sorts every column","Encrypts the table"],"answer":"Uniquely identifies each row","explanation":"A primary key uniquely identifies each record and cannot be NULL."},
    {"subject":"DBMS","topic":"Normalization","difficulty":"Intermediate","question":"A main goal of database normalization is to reduce what?","options":["Data redundancy and update anomalies","All primary keys","Query language syntax","The number of users"],"answer":"Data redundancy and update anomalies","explanation":"Normalization structures tables to reduce duplication and insertion, update, and deletion anomalies."},
    {"subject":"Data Structures","topic":"Arrays","difficulty":"Beginner","question":"In a typical array, elements are stored using what kind of indexing?","options":["Random labels only","Positions or indices","SQL keys only","File names"],"answer":"Positions or indices","explanation":"Array elements are accessed by their position, commonly using zero-based indices."},
    {"subject":"Data Structures","topic":"Stacks & Queues","difficulty":"Beginner","question":"Which principle does a stack follow?","options":["FIFO","LIFO","Random access only","Smallest first"],"answer":"LIFO","explanation":"Last In, First Out: the most recently added item is removed first."},
    {"subject":"Data Structures","topic":"Stacks & Queues","difficulty":"Beginner","question":"Which principle does a queue follow?","options":["LIFO","FIFO","Largest first","Sorted order always"],"answer":"FIFO","explanation":"First In, First Out: the earliest added item is removed first."},
    {"subject":"Data Structures","topic":"Trees","difficulty":"Intermediate","question":"What is the topmost node of a tree called?","options":["Leaf","Edge","Root","Branch"],"answer":"Root","explanation":"The root is the topmost node from which the tree structure begins."}
]

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            topic_accuracy_before REAL NOT NULL,
            attempts_before INTEGER NOT NULL,
            correct INTEGER NOT NULL,
            question_text TEXT DEFAULT '',
            session_id TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(attempts)").fetchall()}
    if "question_text" not in columns:
        conn.execute("ALTER TABLE attempts ADD COLUMN question_text TEXT DEFAULT ''")
    if "session_id" not in columns:
        conn.execute("ALTER TABLE attempts ADD COLUMN session_id TEXT DEFAULT ''")
    conn.commit()
    return conn

def get_available_topics(subject):
    return sorted({q["topic"] for q in QUESTION_BANK if q["subject"] == subject})

def get_available_difficulties(subject, topic):
    order = ["Beginner", "Intermediate", "Advanced"]
    available = {q["difficulty"] for q in QUESTION_BANK
                 if q["subject"] == subject and q["topic"] == topic}
    return [level for level in order if level in available]

def get_available_question_count(subject, topic, difficulty):
    return len({q["question"] for q in QUESTION_BANK
                if q["subject"] == subject and q["topic"] == topic
                and q["difficulty"] == difficulty})

def get_questions(subject, topic, difficulty, count=5, exclude_questions=None):
    """Return unique questions for the exact selected topic and difficulty."""
    excluded = set(exclude_questions or [])
    candidates = [q.copy() for q in QUESTION_BANK
                  if q["subject"] == subject and q["topic"] == topic
                  and q["difficulty"] == difficulty
                  and q["question"] not in excluded]
    random.shuffle(candidates)
    return candidates[:max(0, min(int(count), len(candidates)))]

def record_attempt(subject, topic, difficulty, correct, question_text="", session_id=""):
    conn = _connect()
    rows = conn.execute(
        "SELECT correct FROM attempts WHERE subject=? AND topic=? ORDER BY id",
        (subject, topic)
    ).fetchall()
    attempts_before = len(rows)
    topic_accuracy_before = (sum(row[0] for row in rows) / attempts_before) if attempts_before else 0.5
    conn.execute(
        """INSERT INTO attempts
        (subject, topic, difficulty, topic_accuracy_before, attempts_before, correct, question_text, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (subject, topic, difficulty, float(topic_accuracy_before), attempts_before, int(bool(correct)), question_text, session_id)
    )
    conn.commit()
    conn.close()

def get_stats():
    conn = _connect()
    rows = conn.execute(
        "SELECT id, subject, topic, difficulty, correct, created_at, question_text, session_id FROM attempts ORDER BY id"
    ).fetchall()
    conn.close()
    import pandas as pd
    history = pd.DataFrame(rows, columns=["id", "subject", "topic", "difficulty", "correct", "created_at", "question_text", "session_id"])
    attempts = len(history)
    accuracy = float(history["correct"].mean() * 100) if attempts else 0.0
    return {"attempts": attempts, "accuracy": accuracy, "history": history}
