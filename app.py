import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from src.quiz_engine import get_questions, record_attempt, get_stats
from src.recommender import recommend_topic

st.set_page_config(page_title="LearnLoop", layout="wide")

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#f1efff;--paper:#fff;--ink:#201b3b;--muted:#77718f;--purple:#6547f5;--purple-dark:#4930ce;--lime:#dfff70;--pink:#ff719b;--line:#ded9f5}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp{background:radial-gradient(ellipse at 85% 0%,#e2dcff 0%,transparent 35%),var(--bg);color:var(--ink)}
.block-container{max-width:1160px;padding-top:1.2rem;padding-bottom:3rem}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;color:var(--ink)!important;letter-spacing:-.04em;font-weight:700!important}
p,span,label,li{color:var(--ink)}
[data-testid="stSidebar"]{background:#211b42;border-right:0}
[data-testid="stSidebar"] *{color:#f8f6ff}
[data-testid="stSidebar"] h2{font-size:1.8rem}
[data-testid="stSidebar"] [data-testid="stRadio"] label{background:transparent;border:1px solid transparent;border-radius:12px;padding:9px 12px}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:#39305f}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label p,[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label span{color:#f8f6ff!important}
[data-testid="stSidebar"] hr{border-color:#49416d}
.hero{display:flex;align-items:center;justify-content:space-between;gap:22px;padding:32px 34px;border-radius:26px;background:linear-gradient(115deg,#6547f5 0%,#7858ff 65%,#8e72ff 100%);border:0;color:#fff;margin:8px 0 24px;position:relative;overflow:hidden;box-shadow:0 8px 0 #d7d0fb}
.hero:after{content:"";position:absolute;right:45px;top:-70px;width:260px;height:260px;border-radius:50%;background:rgba(223,255,112,.18)}
.hero-copy{max-width:760px;position:relative;z-index:1}
.hero .eyebrow{color:var(--lime);font-family:'DM Mono',monospace;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase}
.hero h1{color:white!important;font-size:clamp(2.1rem,4.2vw,3.25rem);line-height:1.05;margin:12px 0;max-width:720px}
.hero p{color:#f0ecff!important;margin:0;font-size:1.02rem;line-height:1.6;max-width:650px}
.hero-art{width:160px;min-width:125px;height:150px;object-fit:contain;position:relative;z-index:1;filter:drop-shadow(0 8px 0 rgba(40,24,100,.12))}
.metric-card{background:var(--paper);border:1px solid var(--line);border-radius:19px;padding:18px 20px;min-height:112px;box-shadow:0 5px 0 #e0daf8;transition:transform .16s,box-shadow .16s}
.metric-card:hover{transform:translateY(-3px);box-shadow:0 8px 0 #d6cff6}
.metric-label{color:var(--muted)!important;font-family:'DM Mono',monospace;font-size:.7rem;letter-spacing:.055em}
.metric-value{color:var(--ink)!important;font-family:'Space Grotesk',sans-serif;font-size:2.25rem;font-weight:700;margin-top:5px}
.metric-hint{color:var(--muted)!important;font-size:.82rem}
div[data-testid="stMetric"]{background:white;padding:17px 19px;border:1px solid var(--line);border-radius:18px;box-shadow:0 5px 0 #e0daf8}
div[data-testid="stMetric"] label,div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:var(--ink)!important}
div.stButton>button{border-radius:13px;border:1px solid #d8d1f6;background:white;color:var(--ink);font-weight:800;padding:.68rem 1rem;box-shadow:0 4px 0 #ded8f6;transition:transform .15s,box-shadow .15s}
div.stButton>button:hover{border-color:var(--purple);color:var(--purple-dark);transform:translateY(-2px);box-shadow:0 6px 0 #d5cdfa}
div.stButton>button[kind="primary"]{background:var(--lime);border-color:var(--lime);color:#282344!important;box-shadow:0 4px 0 #b7d84c}
div.stButton>button[kind="primary"]:hover{background:#d2f55d;color:#201b3b!important;box-shadow:0 6px 0 #b7d84c}
[data-testid="stRadio"]>label{color:var(--muted)!important;font-weight:800}
[data-testid="stRadio"] [role="radiogroup"]{gap:10px}
[data-testid="stRadio"] [role="radiogroup"]>label{background:#fff!important;border:1.5px solid #ded9f5!important;border-radius:14px!important;padding:13px 16px!important;margin:0!important;color:var(--ink)!important;box-shadow:0 3px 0 #e8e3fb;transition:background .15s,border-color .15s,transform .15s}
[data-testid="stRadio"] [role="radiogroup"]>label:hover{background:#f6f3ff!important;border-color:#9c8bff!important;transform:translateY(-1px)}
[data-testid="stRadio"] [role="radiogroup"]>label p,[data-testid="stRadio"] [role="radiogroup"]>label span,[data-testid="stRadio"] [role="radiogroup"]>label div{color:#201b3b!important;opacity:1!important}
[data-testid="stRadio"] [role="radiogroup"]>label:has(input:checked){background:#eeeaff!important;border-color:var(--purple)!important;box-shadow:0 3px 0 #d4cbff}
[data-testid="stSelectbox"] label,[data-testid="stSlider"] label{color:var(--ink)!important;font-weight:800}
[data-baseweb="select"]>div{background:#fff;border-color:#dcd6f5;border-radius:12px;color:var(--ink)}
[data-testid="stProgressBar"]>div{background:#ded8f8;border-radius:12px}
[data-testid="stProgressBar"]>div>div{background:var(--pink);border-radius:12px}
[data-testid="stAlert"]{border-radius:15px;border:1px solid #dcd5ff}
hr{border-color:var(--line)}
.eyebrow{font-family:'DM Mono',monospace;font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;color:var(--purple)}
.question-card{background:white;border:1px solid #ded9f5;border-left:6px solid var(--pink);border-radius:18px;padding:22px 24px;margin:13px 0 18px;box-shadow:0 5px 0 #e5e0fa}
.question-card .kicker{font-family:'DM Mono',monospace;font-size:.7rem;letter-spacing:.09em;text-transform:uppercase;color:#a83e68}
.question-card p{color:#201b3b!important;font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:700;margin:8px 0 0;line-height:1.45}
div[data-testid="stPlotlyChart"],div[data-testid="stDataFrame"]{background:white;border:1px solid var(--line);border-radius:16px;padding:8px}
.small-muted{color:var(--muted)!important;font-size:.88rem}
@media(max-width:700px){.hero{padding:22px}.hero-art{width:95px;min-width:80px;height:100px}.hero h1{font-size:2rem}}
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
    st.markdown("## LearnLoop")
    st.caption("A place to learn by doing.")
    page = st.radio("YOUR SPACE", ["Home", "Take a quiz", "My progress"], index=["Home", "Take a quiz", "My progress"].index(st.session_state.page))
    st.session_state.page = page
    st.divider()
    st.markdown("**Your routine**")
    st.markdown("Learn a concept")
    st.markdown("Practice a little")
    st.markdown("Improve over time")
    st.caption("Small practice. Real progress.")

stats = get_stats()
total_attempts = stats["attempts"]
accuracy = stats["accuracy"]
xp = total_attempts * 10
st.markdown(f"""
<div class="hero">
  <div class="hero-copy">
    <div class="eyebrow">YOUR FRIENDLY STUDY SPACE</div>
    <h1>Build knowledge, one question at a time.</h1>
    <p>A few focused questions today can make tomorrow’s concepts easier. Choose a topic and start where you are.</p>
  </div>
  <img class="hero-art" src="https://api.dicebear.com/9.x/notionists/svg?seed=LearnLoop&backgroundColor=c7b8ff&body=variant01&hair=variant01" alt="Illustrated learner with a notebook">
</div>
""", unsafe_allow_html=True)

if st.session_state.page == "Home":
    m1, m2, m3 = st.columns(3)
    for col, label, value, hint in [
        (m1, "TOTAL XP", str(xp), "10 XP per answered question"),
        (m2, "QUESTIONS ANSWERED", str(total_attempts), "Every attempt counts"),
        (m3, "OVERALL ACCURACY", f"{accuracy:.0f}%", "Based on saved attempts"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-hint">{hint}</div></div>', unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("A small session goes a long way.")
        st.markdown("A few questions are enough to keep the gears turning. Pick a topic and have a go.")
        if st.button("Start a practice session", type="primary", use_container_width=True):
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
        st.subheader("Your next topic")
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
    if st.button("Create my quiz", type="primary"):
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
        st.markdown(f'<div class="question-card"><div class="kicker">YOUR QUESTION</div><p>{q["question"]}</p></div>', unsafe_allow_html=True)
        choice = st.radio("Choose one answer", q["options"], index=None, key=f"answer_{idx}", label_visibility="collapsed")
        if st.button("Check answer", type="primary", key=f"lock_{idx}", disabled=(choice is None or f"feedback_{idx}" in st.session_state)):
            st.session_state.quiz_answers[idx] = choice
            correct = choice == q["answer"]
            record_attempt(st.session_state.quiz_subject, st.session_state.quiz_topic, st.session_state.quiz_difficulty, correct)
            st.session_state[f"feedback_{idx}"] = (correct, q["explanation"])
            st.rerun()
        feedback = st.session_state.get(f"feedback_{idx}")
        if feedback:
            if feedback[0]:
                st.success("Correct. +10 XP")
            else:
                st.error(f"Not quite. Correct answer: {q['answer']}")
            st.write(q["explanation"])
            if idx + 1 < len(questions):
                if st.button("Next question →", type="primary", key=f"next_{idx}"):
                    st.session_state.quiz_index += 1
                    st.rerun()
            else:
                if st.button("Finish quiz", type="primary", key="finish"):
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
    st.subheader("Your learning progress")
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
