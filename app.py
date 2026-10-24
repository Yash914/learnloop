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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f6f7fb; }
.block-container { padding-top: 1.4rem; max-width: 1180px; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: #172033; }
.hero { padding: 28px 30px; border-radius: 22px; background: linear-gradient(115deg,#262a59,#5144a5 68%,#7568dd); color: white; margin-bottom: 18px; }
.hero h1 { color: white; font-size: 2.35rem; margin: 0; }
.hero p { color: #e4e5ff; margin: 8px 0 0 0; font-size: 1rem; }
.metric-card { background: white; border: 1px solid #eaecf4; border-radius: 18px; padding: 18px 20px; min-height: 110px; box-shadow: 0 4px 18px #20274a08; }
.metric-label { color: #69718a; font-size: .9rem; }
.metric-value { color: #202746; font-family: 'Space Grotesk'; font-size: 1.8rem; font-weight: 700; margin-top: 4px; }
.metric-hint { color: #7d8499; font-size: .8rem; }
div.stButton > button { border-radius: 12px; border: 0; font-weight: 700; padding: .65rem 1rem; }
div.stButton > button[kind="primary"] { background: #6255d9; color: white; }
div[data-testid="stMetric"] { background: white; padding: 15px; border: 1px solid #eaecf4; border-radius: 16px; }
div[role="radiogroup"] label { background: white; border: 1px solid #e4e7f0; padding: 12px 14px; border-radius: 12px; margin-bottom: 7px; }
.small-muted { color: #747c91; font-size: .88rem; }
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
    st.markdown("## 🎯 LearnLoop")
    st.caption("Small steps. Daily progress.")
    page = st.radio("YOUR SPACE", ["Home", "Take a quiz", "My progress"], index=["Home", "Take a quiz", "My progress"].index(st.session_state.page))
    st.session_state.page = page
    st.divider()
    st.markdown("**Your learning loop**")
    st.markdown("📚 Learn a concept")
    st.markdown("⚡ Practice a little")
    st.markdown("🌱 Improve over time")
    st.caption("Mini-project · ML-powered recommendations")

stats = get_stats()
total_attempts = stats["attempts"]
accuracy = stats["accuracy"]
xp = total_attempts * 10
st.markdown(f"""
<div class="hero">
  <div style="font-size:.82rem;letter-spacing:1.6px;text-transform:uppercase;font-weight:700;">YOUR DAILY LEARNING SPACE</div>
  <h1>Make progress, one question at a time.</h1>
  <p>Practice technical concepts, earn XP, and let your results guide what you learn next.</p>
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
        st.subheader("Ready for today's quest?")
        st.markdown("Pick a subject and start with a short quiz. Your results will help LearnLoop choose what you should practise next.")
        if st.button("Start a quiz  →", type="primary", use_container_width=True):
            st.session_state.page = "Take a quiz"
            st.rerun()
        st.write("")
        st.subheader("Explore subjects")
        cards = st.columns(3)
        for col, emoji, title, subtitle in [
            (cards[0], "🐍", "Python", "Programming basics"),
            (cards[1], "🧠", "Machine Learning", "Models & concepts"),
            (cards[2], "🗄️", "DBMS", "Data & SQL"),
        ]:
            with col:
                st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem">{emoji}</div><b>{title}</b><div class="metric-hint">{subtitle}</div></div>', unsafe_allow_html=True)
    with right:
        st.subheader("✨ Your next recommended topic")
        topic = recommend_topic()
        st.info(f"**{topic['topic']}**\n\n{topic['reason']}")
        st.caption("Recommendation uses your saved quiz history. With little history, LearnLoop starts with a beginner-friendly topic.")

elif st.session_state.page == "Take a quiz":
    st.subheader("🧩 Build your quiz")
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
        st.progress((idx + 1) / len(questions), text=f"Question {idx + 1} of {len(questions)}")
        st.markdown(f"### {q['question']}")
        choice = st.radio("Choose one answer", q["options"], index=None, key=f"answer_{idx}", label_visibility="collapsed")
        if st.button("Lock in answer", type="primary", key=f"lock_{idx}", disabled=choice is None):
            st.session_state.quiz_answers[idx] = choice
            correct = choice == q["answer"]
            record_attempt(st.session_state.quiz_subject, st.session_state.quiz_topic, st.session_state.quiz_difficulty, correct)
            st.session_state[f"feedback_{idx}"] = (correct, q["explanation"])
            st.rerun()
        feedback = st.session_state.get(f"feedback_{idx}")
        if feedback:
            if feedback[0]:
                st.success("Correct! +10 XP")
            else:
                st.error(f"Not quite. Correct answer: {q['answer']}")
            st.write(q["explanation"])
            if idx + 1 < len(questions):
                if st.button("Next question →", type="primary", key=f"next_{idx}"):
                    st.session_state.quiz_index += 1
                    st.rerun()
            else:
                if st.button("Finish quiz 🏁", type="primary", key="finish"):
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
            st.session_state.quiz_questions = []
            st.session_state.quiz_finished = False
            st.session_state.quiz_answers = {}
            st.rerun()

elif st.session_state.page == "My progress":
    st.subheader("📈 Your learning progress")
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
