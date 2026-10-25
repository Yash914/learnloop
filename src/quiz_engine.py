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

    {"subject":"Python","topic":"Variables & Data Types","difficulty":"Intermediate","question":"What is printed by print(bool([]), bool([0]))?","options":["True True","False True","False False","True False"],"answer":"False True","explanation":"An empty list is falsy; a non-empty list is truthy even if it contains 0."},
    {"subject":"Python","topic":"Variables & Data Types","difficulty":"Advanced","question":"What is the main risk of using a list as a function's default argument?","options":["It is copied on every call","The same list can be shared across calls","Lists cannot be default values","The function becomes recursive"],"answer":"The same list can be shared across calls","explanation":"Default values are evaluated once when the function is defined, so mutations can persist between calls."},
    {"subject":"Python","topic":"Loops","difficulty":"Intermediate","question":"What is the sum of the values produced by range(1, 4)?","options":["3","6","7","10"],"answer":"6","explanation":"range(1, 4) produces 1, 2, and 3; their sum is 6."},
    {"subject":"Python","topic":"Loops","difficulty":"Advanced","question":"A break statement inside a nested loop exits which loop?","options":["Every enclosing loop","Only the nearest enclosing loop","The program entirely","No loop"],"answer":"Only the nearest enclosing loop","explanation":"break exits the innermost loop containing it. A flag or return can stop a wider search."},
    {"subject":"Python","topic":"Functions","difficulty":"Intermediate","question":"What does a Python function return if it reaches its end without a return statement?","options":["0","False","None","An empty list"],"answer":"None","explanation":"Python implicitly returns None when no return value is specified."},
    {"subject":"Python","topic":"Functions","difficulty":"Advanced","question":"What is a practical benefit of a generator using yield?","options":["It sorts every value","It produces values lazily and can save memory","It guarantees parallel execution","It suppresses errors"],"answer":"It produces values lazily and can save memory","explanation":"Generators yield values as needed rather than constructing an entire sequence in memory."},
    {"subject":"Machine Learning","topic":"Linear Regression","difficulty":"Intermediate","question":"What does a residual represent in regression?","options":["Actual target minus predicted target","The learning rate","Number of classes","Feature count"],"answer":"Actual target minus predicted target","explanation":"Residuals are observed values minus model predictions."},
    {"subject":"Machine Learning","topic":"Linear Regression","difficulty":"Advanced","question":"Training error is very low but test error is high. What is the most likely issue?","options":["Underfitting","Overfitting","Perfect generalisation","Data normalisation"],"answer":"Overfitting","explanation":"The model fits training data well but generalises poorly to unseen examples."},
    {"subject":"Machine Learning","topic":"Classification","difficulty":"Intermediate","question":"A model predicts 40 cases as positive, of which 30 are truly positive. What is precision?","options":["25%","30%","75%","100%"],"answer":"75%","explanation":"Precision = true positives / predicted positives = 30/40 = 75%."},
    {"subject":"Machine Learning","topic":"Classification","difficulty":"Advanced","question":"In a high-risk screening task, why may recall matter more than precision?","options":["False negatives may be costly","Recall measures squared error","Precision cannot be measured","Recall always equals accuracy"],"answer":"False negatives may be costly","explanation":"High recall means finding a larger share of actual positive cases."},
    {"subject":"Machine Learning","topic":"Model Evaluation","difficulty":"Intermediate","question":"Why can accuracy be misleading when 99% of examples belong to one class?","options":["A majority-class-only model can still score 99%","Accuracy cannot use labels","Accuracy is always zero","The dataset cannot be split"],"answer":"A majority-class-only model can still score 99%","explanation":"Inspect precision, recall, F1-score and the confusion matrix for imbalanced data."},
    {"subject":"Machine Learning","topic":"Model Evaluation","difficulty":"Advanced","question":"What is data leakage in machine learning?","options":["Random noise in features","Training or evaluation uses information unavailable at prediction time","Removing duplicate rows","Using a validation set"],"answer":"Training or evaluation uses information unavailable at prediction time","explanation":"Leakage makes reported performance look better than real-world performance."},
    {"subject":"DBMS","topic":"SQL Basics","difficulty":"Intermediate","question":"Which clause filters grouped results using an aggregate such as COUNT(*)?","options":["WHERE","HAVING","ORDER BY","LIMIT"],"answer":"HAVING","explanation":"HAVING filters groups after GROUP BY; WHERE filters individual rows before grouping."},
    {"subject":"DBMS","topic":"SQL Basics","difficulty":"Advanced","question":"What happens to an unmatched row on either side of an INNER JOIN?","options":["It is returned with NULLs","It is excluded","It duplicates all rows","The query always errors"],"answer":"It is excluded","explanation":"An INNER JOIN returns only rows that satisfy the join condition."},
    {"subject":"DBMS","topic":"Keys & Constraints","difficulty":"Intermediate","question":"Which constraint enforces uniqueness for a column or combination of columns?","options":["UNIQUE","DEFAULT","CHECK only","ORDER BY"],"answer":"UNIQUE","explanation":"A UNIQUE constraint prevents duplicate key values; NULL behaviour varies by DBMS."},
    {"subject":"DBMS","topic":"Keys & Constraints","difficulty":"Advanced","question":"What does referential integrity prevent for a foreign key?","options":["All NULL values","References to missing parent keys, subject to constraint rules","All joins","Duplicate table names"],"answer":"References to missing parent keys, subject to constraint rules","explanation":"Foreign-key constraints maintain valid relationships between related tables."},
    {"subject":"DBMS","topic":"Normalization","difficulty":"Beginner","question":"Which normal form requires each field to contain an atomic value and avoids repeating groups?","options":["1NF","2NF","3NF","BCNF only"],"answer":"1NF","explanation":"First Normal Form requires atomic values and no repeating groups."},
    {"subject":"DBMS","topic":"Normalization","difficulty":"Advanced","question":"StudentName depends on StudentID, while a table's composite key is (StudentID, CourseID). What dependency is shown?","options":["Partial functional dependency","Transitive dependency only","No dependency","Multivalued index"],"answer":"Partial functional dependency","explanation":"The attribute depends on only part of the composite key, which is a 2NF issue."},
    {"subject":"Data Structures","topic":"Arrays","difficulty":"Intermediate","question":"What is the typical time complexity of accessing an array element by index?","options":["O(1)","O(log n)","O(n)","O(n log n)"],"answer":"O(1)","explanation":"Array indexing gives direct access in constant time."},
    {"subject":"Data Structures","topic":"Arrays","difficulty":"Advanced","question":"Why can inserting at index 0 in a contiguous array take O(n) time?","options":["The array must be sorted","Existing elements may need to shift","Indexing is always O(n)","Arrays cannot resize"],"answer":"Existing elements may need to shift","explanation":"Elements can need to move right to create a free position."},
    {"subject":"Data Structures","topic":"Stacks & Queues","difficulty":"Intermediate","question":"Which data structure is commonly used to manage function calls?","options":["Queue","Stack","Graph","Hash table"],"answer":"Stack","explanation":"Function calls and local execution contexts are commonly managed with a call stack."},
    {"subject":"Data Structures","topic":"Stacks & Queues","difficulty":"Advanced","question":"Which structure is commonly used by breadth-first search?","options":["Stack","Queue","Binary search tree","Set only"],"answer":"Queue","explanation":"A queue processes discovered vertices in first-in-first-out order."},
    {"subject":"Data Structures","topic":"Trees","difficulty":"Beginner","question":"What is the maximum number of children of a node in a binary tree?","options":["1","2","3","Unlimited"],"answer":"2","explanation":"A binary-tree node has at most two children."},
    {"subject":"Data Structures","topic":"Trees","difficulty":"Advanced","question":"What is the worst-case search time in a highly unbalanced binary search tree with n nodes?","options":["O(1)","O(log n) guaranteed","O(n)","O(n log n) always"],"answer":"O(n)","explanation":"An unbalanced tree can degenerate into a chain, requiring linear search."}

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
