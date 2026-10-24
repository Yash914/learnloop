# 🎯 LearnLoop

**A Personalized Quiz Recommendation System Using Machine Learning**

LearnLoop is a small, gamified learning app for practising technical subjects. It gives instant feedback, stores quiz attempts locally, tracks progress, and recommends topics based on performance.

## Features

- Interactive Streamlit UI with subject/topic/difficulty selection
- Multiple-choice quizzes with explanations
- XP-style progress dashboard and topic accuracy charts
- Local SQLite storage for quiz attempts
- History-based topic recommendations that prioritise weaker or unpractised topics
- An optional Logistic Regression baseline that can be trained after enough real quiz attempts have been collected
- Built-in questions, so no API key is required to run the first version

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

3. Install packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:
   ```bash
   streamlit run app.py
   ```

## Project structure

```text
learnloop/
├── app.py
├── requirements.txt
├── src/
│   ├── quiz_engine.py
│   ├── recommender.py
│   └── model.py
├── assets/
├── data/
└── README.md
```

## Machine learning plan

The current prototype uses a transparent performance-based recommender. The Logistic Regression module is an early baseline for predicting answer correctness using prior topic accuracy, number of previous attempts, and question difficulty. It only trains when at least 20 real attempts and both correct/incorrect outcomes exist; before that, it returns no prediction.

For a credible evaluation, collect more interactions and evaluate using a time-aware or held-out split. Avoid claiming model accuracy before that evaluation. The first version uses a verified-by-us static question bank; LLM-generated questions can be integrated later through the same question-generation interface, with output validation and answer review.

## Current status

Early prototype — local use, static question bank, SQLite history. User accounts, cloud sync, and LLM question generation are not implemented yet.
