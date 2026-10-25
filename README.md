# LearnLoop

**A Personalized Quiz Recommendation System Using Machine Learning**

LearnLoop is a Streamlit mini-project for technical practice and data-driven topic recommendations. It records quiz outcomes locally, provides explanations, analyses performance, and uses a Logistic Regression baseline to estimate the probability of answering correctly when enough data exists.

## Features

- Four subjects: Python, Machine Learning, DBMS, and Data Structures
- Topic and difficulty selection based on the question bank's actual coverage
- No silent difficulty fallback and no duplicate questions within a quiz
- Question history stored in SQLite, including outcome, difficulty, timestamp, and question text
- Analytics for topic accuracy, accuracy over time, difficulty-level performance, and recent answers
- Topic recommendations based on historical accuracy, practice count, and an optional Logistic Regression estimate
- Model insights page with stratified cross-validation metrics and a majority-class baseline
- No API key required

## Tech stack

Python · Streamlit · Pandas · Plotly · SQLite · scikit-learn

## Run locally

Python 3.10 or newer is recommended.

1. Clone the repository:
   ```bash
   git clone https://github.com/Yash914/learnloop.git
   cd learnloop
   ```

2. Create and activate a virtual environment (skip creation if you already have one):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the app:
   ```bash
   python -m streamlit run app.py
   ```

## Project structure

```text
learnloop/
├── app.py                 # Streamlit pages and visual analytics
├── requirements.txt
├── src/
│   ├── quiz_engine.py     # Question bank, selection, SQLite history
│   ├── recommender.py     # History-based topic recommendation
│   └── model.py           # Logistic Regression and cross-validation evaluation
└── README.md
```

## How the ML component works

The Logistic Regression baseline uses three features captured before each answer: historical accuracy for that topic, number of previous attempts, and difficulty encoded as Beginner=0, Intermediate=1, Advanced=2. Its target is whether the answer was correct.

The app waits for at least 20 recorded attempts and both outcome classes before fitting/evaluating. The Model Insights page uses stratified cross-validation to produce out-of-fold predictions and reports accuracy, precision, recall, F1-score, plus a majority-class baseline. Small histories can produce unstable metrics, so the page shows a warning until the minimum conditions are met. These metrics evaluate answer-correctness prediction, not learning gains or the intrinsic quality of questions.

Topic recommendations prioritise topics with lower historical performance and exploration of unpractised topics. When the model can be trained, its predicted correctness probability contributes to the ranking; otherwise, the recommender falls back to transparent history-based scoring.

## Important limitations

- The question bank is static and still a small educational prototype; question coverage varies by topic and difficulty. The app displays available counts and never silently substitutes another level.
- Attempts are stored in a local SQLite database on the machine running the app. There are no accounts or cloud sync.
- Cross-validation is a useful initial check, but a larger dataset and a time-aware or external held-out evaluation are needed before making strong claims about predictive performance.
- The recommender is an educational prototype, not a validated measure of mastery.

## Current status

Improved prototype focused on reliable question selection, interpretable analytics, and transparent model evaluation. Future work could add a larger reviewed question bank, adaptive difficulty policies, tests, and a temporal evaluation dataset.
