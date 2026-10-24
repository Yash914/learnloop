import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from src.quiz_engine import get_questions, record_attempt, get_stats
from src.recommender import recommend_topic

st.set_page_config(page_title="LearnLoop", page_icon="🎯", layout="wide")

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Nunito:wght@400;500;600;700;800;900&display=swap');
:root { --paper:#fff9ed; --ink:#283b32; --muted:#66766a; --sage:#dce8d5; --sage-dark:#3f654d; --coral:#e98268; --line:#e5dfd0; }
html, body, [class*="css"] { font-family:'Nunito',sans-serif; color:var(--ink); }
.stApp { background:var(--paper); color:var(--ink); }
.block-container { padding-top:1.35rem; padding-bottom:3rem; max-width:1120px; }
h1,h2,h3 { color:var(--ink) !important; letter-spacing:-.035em; }
h1,h2 { font-family:'Fraunces',Georgia,serif !important; }
h3 { font-family:'Nunito',sans-serif !important; font-weight:900 !important; }
p,span,label,li,.stMarkdown { color:var(--ink); }
[data-testid="stSidebar"] { background:#edf2e7; border-right:1px solid #dce5d5; }
[data-testid="stSidebar"] * { color:var(--ink); }
[data-testid="stSidebar"] h2 { font-size:1.65rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { background:transparent; border:0; border-radius:12px; padding:8px 10px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#dce8d5; }
.hero { padding:28px 32px 25px; border-radius:20px; background:#dce8d5; border:1px solid #cadbc4; color:var(--ink); margin:8px 0 22px; position:relative; overflow:hidden; }
.hero:after { content:"✳"; position:absolute; right:30px; top:-23px; font-size:8rem; color:#b6cfad; transform:rotate(14deg); }
.hero h1 { color:var(--ink) !important; font-size:clamp(2rem,4vw,3rem); line-height:1.08; margin:10px 0 9px; max-width:720px; }
.hero p { color:#506a57 !important; margin:0; font-size:1.02rem; max-width:700px; }
.eyebrow { color:#4f7355; font-family:'DM Mono',monospace; font-size:.76rem; letter-spacing:.08em; font-weight:500; text-transform:uppercase; }
.metric-card { background:#fffdf7; border:1px solid var(--line); border-radius:16px; padding:17px 19px; min-height:108px; box-shadow:0 3px 0 #e8e1d3; }
.metric-label { color:var(--muted) !important; font-family:'DM Mono',monospace; font-size:.73rem; letter-spacing:.04em; }
.metric-value { color:var(--ink) !important; font-family:'Fraunces',Georgia,serif; font-size:2rem; font-weight:600; margin-top:4px; }
.metric-hint { color:#798579 !important; font-size:.82rem; }
div[data-testid="stMetric"] { background:#fffdf7; padding:15px 17px; border:1px solid var(--line); border-radius:16px; box-shadow:0 3px 0 #e8e1d3; }
div[data-testid="stMetric"] label,div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:var(--ink) !important; }
div.stButton > button { border-radius:12px; border:1px solid #d8d2c3; background:#fffdf7; color:var(--ink); font-weight:800; padding:.62rem 1rem; transition:transform .15s ease,box-shadow .15s ease; box-shadow:0 3px 0 #e4dccb; }
div.stButton > button:hover { border-color:#a6b99d; color:var(--ink); transform:translateY(-1px); box-shadow:0 4px 0 #d8e2d1; }
div.stButton > button[kind="primary"] { background:var(--sage-dark); color:#fffdf7 !important; border-color:var(--sage-dark); box-shadow:0 3px 0 #2e4b39; }
div.stButton > button[kind="primary"]:hover { background:#345840; color:#fffdf7 !important; }
[data-testid="stRadio"] > label { color:var(--muted) !important; font-weight:800; }
[data-testid="stRadio"] [role="radiogroup"] { gap:8px; }
[data-testid="stRadio"] [role="radiogroup"] > label { background:#fffdf7 !important; border:1.5px solid #e3ddcf !important; border-radius:13px !important; padding:12px 15px !important; margin:0 !important; color:#283b32 !important; box-shadow:0 2px 0 #ece5d7; transition:background .15s ease,border-color .15s ease; }
[data-testid="stRadio"] [role="radiogroup"] > label:hover { background:#f1f5e9 !important; border-color:#9ab393 !important; }
[data-testid="stRadio"] [role="radiogroup"] > label p,[data-testid="stRadio"] [role="radiogroup"] > label span,[data-testid="stRadio"] [role="radiogroup"] > label div { color:#283b32 !important; opacity:1 !important; }
[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) { background:#e3eddc !important; border-color:#5f8764 !important; }
[data-testid="stSelectbox"] label,[data-testid="stSlider"] label { color:var(--ink) !important; font-weight:800; }
[data-baseweb="select"] > div { background:#fffdf7; border-color:#ded7c7; border-radius:11px; color:var(--ink); }
[data-testid="stProgressBar"] > div { background:#e8e2d5; border-radius:10px; }
[data-testid="stProgressBar"] > div > div { background:var(--coral); border-radius:10px; }
[data-testid="stAlert"] { border-radius:13px; }
hr { border-color:var(--line); }
div[data-testid="stPlotlyChart"],div[data-testid="stDataFrame"] { background:#fffdf7; border:1px solid var(--line); border-radius:14px; padding:8px; }
.small-muted { color:var(--muted) !important; font-size:.88rem; }
.kicker { color:#8c624d; font-family:'DM Mono',monospace; font-size:.76rem; text-transform:uppercase; letter-spacing:.07em; }
.question-card { background:#fffdf7; border:1px solid #e5dfd0; border-left:5px solid #e98268; border-radius:16px; padding:19px 22px; margin:12px 0 16px; box-shadow:0 3px 0 #ece5d7; }
.question-card p { color:#283b32 !important; font-size:1.22rem; font-weight:900; margin:6px 0 0; line-height:1.45; }
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_finished" not in st.session_state:
    st.session_state.quiz_finished = False

with st.sidebar:
    st.markdown("## ☕ LearnLoop")
    st.caption("your little corner to level up")
    page = st.radio("YOUR SPACE", ["Home", "Take a quiz", "My progress"], index=["Home", "Take a quiz", "My progress"].index(st.session_state.page))
    st.session_state.page = page
    st.divider()
    st.markdown("**The little loop**")
    st.markdown("📚 Learn a concept")
    st.markdown("⚡ Practice a little")
    st.markdown("🌱 Improve over time")
    st.caption("made for curious minds ♡")

stats = get_stats()
total_attempts = stats["attempts"]
accuracy = stats["accuracy"]
xp = total_attempts * 10
st.markdown(f"""
<div class="hero">
  <div style="font-size:.82rem;letter-spacing:1.6px;text-transform:uppercase;font-weight:700;">A LITTLE STUDY, A LITTLE EVERY DAY</div>
  <h1>Make room for a little progress.</h1>
  <p>Your cosy corner for Python, ML, databases, and the things you're curious about. No cramming required.</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.page == "Home":
    m1, m2, m3 = st.columns(3)
    for col, label, value, hint in [
        (m1, "⚡ TOTAL XP", str(xp), "10 XP per answered question"),
        (m2, "🧠 QUESTIONS ANSWERED", str(total_attempts), "Every attempt counts"),
        (m3, "🎯 OVERALL ACCURACY", f"{accuracy:.0f}%", "Based on saved attempts"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-hint">{hint}</div></div>', unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("What shall we learn today?")
        st.markdown("A few questions are enough to keep the gears turning. Pick a topic and have a go.")
        if st.button("Let’s do a little quiz  ↗", type="primary", use_container_width=True):
            st.session_state.page = "Take a quiz"
            st.rerun()
        st.write("")
        st.subheader("Pick up where curiosity takes you")
        cards = st.columns(3)
        for col, emoji, title, subtitle in [
            (cards[0], "🐍", "Python", "Programming basics"),
            (cards[1], "🧠", "Machine Learning", "Models & concepts"),
            (cards[2], "🗄️", "DBMS", "Data & SQL"),
        ]:
            with col:
                st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem">{emoji}</div><b>{title}</b><div class="metric-hint">{subtitle}</div></div>', unsafe_allow_html=True)
    with right:
        st.subheader("A nudge for next time 🌱")
        topic = recommend_topic()
        st.info(f"**{topic['topic']}**\n\n{topic['reason']}")
        st.caption("Recommendation uses your saved quiz history. With little history, LearnLoop starts with a beginner-friendly topic.")

elif st.session_state.page == "Take a quiz":
    st.subheader("Let’s set up a tiny challenge")
    subjects = ["Python", "Machine Learning", "DBMS", "Data Structures"]
    subject = st.selectbox("Choose a subject", subjects)
    topic_map = {
        "Python": ["Variables & Data Types", "Loops", "Functions"],
        "Machine Learning": ["Linear Regression", "Classification", "Model Evaluation"],
        "DBMS": ["SQL Basics", "Keys & Constraints", "Normalization"],
        "Data Structures": ["Arrays", "Stacks & Queues", "Trees"],
    }
    topic = st.selectbox("Choose a topic", topic_map[subject])
    difficulty = st.select_slider("Difficulty", options=["Beginner", "Intermediate", "Advanced"], value="Beginner")
    count = st.selectbox("Questions", [5, 8, 10], index=0)
    if st.button("Create my quiz ✨", type="primary"):
        for key in list(st.session_state.keys()):
            if key.startswith("feedback_"):
                del st.session_state[key]
        st.session_state.quiz_questions = get_questions(subject, topic, difficulty, count)
        st.session_state.quiz_subject = subject
        st.session_state.quiz_topic = topic
        st.session_state.quiz_difficulty = difficulty
        st.session_state.quiz_index = 0
        st.session_state.quiz_answers = {}
        st.session_state.quiz_finished = False
        st.rerun()

    questions = st.session_state.quiz_questions
    if questions and not st.session_state.quiz_finished:
        idx = st.session_state.quiz_index
        q = questions[idx]
        st.progress((idx + 1) / len(questions), text=f"A little challenge · {idx + 1} of {len(questions)}")
        st.markdown(f"### {q['question']}")
        choice = st.radio("Pick the answer that feels right", q["options"], index=None, key=f"answer_{idx}", label_visibility="collapsed")
        if st.button("Check my answer  ↗", type="primary", key=f"lock_{idx}", disabled=(choice is None or f"feedback_{idx}" in st.session_state)):
            st.session_state.quiz_answers[idx] = choice
            correct = choice == q["answer"]
            record_attempt(st.session_state.quiz_subject, st.session_state.quiz_topic, st.session_state.quiz_difficulty, correct)
            st.session_state[f"feedback_{idx}"] = (correct, q["explanation"])
            st.rerun()
        feedback = st.session_state.get(f"feedback_{idx}")
        if feedback:
            if feedback[0]:
                st.success("Lovely work! +10 XP 🌼")
            else:
                st.error(f"Not this time — the answer is: {q['answer']}")
            st.write(q["explanation"])
            if idx + 1 < len(questions):
                if st.button("On to the next one  →", type="primary", key=f"next_{idx}"):
                    st.session_state.quiz_index += 1
                    st.rerun()
            else:
                if st.button("See how I did  ✿", type="primary", key="finish"):
                    st.session_state.quiz_finished = True
                    st.rerun()

    if questions and st.session_state.quiz_finished:
        correct_n = sum(1 for i, q in enumerate(questions) if st.session_state.quiz_answers.get(i) == q["answer"])
        st.balloons()
        st.success("Quest complete!")
        st.metric("Your score", f"{correct_n}/{len(questions)}", f"{correct_n / len(questions):.0%}")
        st.markdown("### Keep the loop going")
        st.write("Your answers are saved locally and will influence your next topic recommendation.")
        if st.button("Try another quiz", type="primary"):
            for key in list(st.session_state.keys()):
                if key.startswith("feedback_"):
                    del st.session_state[key]
            st.session_state.quiz_questions = []
            st.session_state.quiz_finished = False
            st.session_state.quiz_answers = {}
            st.rerun()

elif st.session_state.page == "My progress":
    st.subheader("Your little progress garden 🌱")
    history = stats["history"]
    if history.empty:
        st.info("Your progress chart will appear after you answer your first question.")
    else:
        topic_df = history.groupby(["subject", "topic"], as_index=False).agg(
            attempts=("correct", "count"), accuracy=("correct", "mean")
        )
        topic_df["accuracy_pct"] = topic_df["accuracy"] * 100
        fig = px.bar(topic_df, x="topic", y="accuracy_pct", color="subject", range_y=[0, 100],
                     labels={"topic": "Topic", "accuracy_pct": "Accuracy (%)", "subject": "Subject"},
                     title="Accuracy by topic")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(topic_df[["subject", "topic", "attempts", "accuracy_pct"]].rename(
            columns={"subject": "Subject", "topic": "Topic", "attempts": "Attempts", "accuracy_pct": "Accuracy (%)"}
        ), use_container_width=True, hide_index=True)
        st.caption("Performance is based on the attempts recorded on this device.")
