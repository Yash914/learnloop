import sys
import uuid
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from src.quiz_engine import (
    get_available_difficulties, get_available_question_count, get_available_topics,
    get_questions, get_stats, record_attempt,
)
from src.recommender import recommend_topic
from src.model import evaluate_model

st.set_page_config(page_title="LearnLoop | Learning Analytics", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--bg:#f5f7fb;--panel:#fff;--ink:#172033;--muted:#68748a;--line:#e2e8f0;--accent:#5b5bd6;--accent-soft:#eeefff;--green:#167d64;--amber:#a65b12}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg);color:var(--ink)}
.block-container{max-width:1280px;padding-top:1.5rem;padding-bottom:3rem}
/* Force readable contrast for Streamlit widgets regardless of the user's theme */
.stMarkdown,.stMarkdown p,.stMarkdown li,.stText,.stCaption,.stCaption p,
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"],[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stRadio"] label,[data-testid="stCheckbox"] label,
[data-testid="stSelectbox"] label,[data-testid="stMultiSelect"] label,
[data-testid="stNumberInput"] label,[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,[data-testid="stSlider"] label,
[data-testid="stFileUploader"] label {color:var(--ink)!important}
.stCaption,.stCaption p,small,.muted{color:var(--muted)!important}
[data-testid="stRadio"] [role="radiogroup"] label,
[data-testid="stCheckbox"] label{background:transparent}
[data-baseweb="select"] *,[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea{color:var(--ink)!important}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,
[data-baseweb="textarea"]>div{background:#fff!important}
[data-testid="stDataFrame"],[data-testid="stTable"]{color:var(--ink)!important}
[data-testid="stAlert"] p{color:var(--ink)!important}
.stProgress [data-testid="stMarkdownContainer"]{color:var(--ink)!important}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em;color:var(--ink)!important}
h1{font-size:2.25rem!important} h2{font-size:1.55rem!important} h3{font-size:1.15rem!important}
p,li,label{color:var(--ink)}
[data-testid="stSidebar"]{background:#151d31;border-right:1px solid #27324a}
[data-testid="stSidebar"],[data-testid="stSidebar"] *{color:#e8edf8!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label,
[data-testid="stSidebar"] [data-testid="stRadio"] label *,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *{color:#e8edf8!important}
[data-testid="stHeader"]{background:#f5f7fb!important}
[data-testid="stHeader"] *{color:#172033!important}
.js-plotly-plot .plotly text{fill:#526079!important}
.js-plotly-plot .plotly .xtick text,.js-plotly-plot .plotly .ytick text,
.js-plotly-plot .plotly .gtitle,.js-plotly-plot .plotly .legend text{fill:#526079!important}

[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:9px 11px;border-radius:9px}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:#26314b}
[data-testid="stSidebar"] hr{border-color:#34405a}
.brand{font-family:'Space Grotesk',sans-serif;font-size:1.65rem;font-weight:700;letter-spacing:-.04em;color:#fff}
.brand span{color:#a7a7ff}
.eyebrow{font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:.11em;font-size:.72rem;color:var(--accent);font-weight:500}
.page-head{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin:5px 0 22px}
.page-head p{color:var(--muted);margin-top:5px}
.tag{display:inline-block;border:1px solid var(--line);background:#fff;color:var(--muted);padding:6px 10px;border-radius:7px;font-size:.75rem;font-family:'DM Mono',monospace}
.metric{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:17px 19px;min-height:116px}
.metric .label{font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-size:.69rem}
.metric .value{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;color:var(--ink);margin-top:8px}
.metric .hint{font-size:.8rem;color:var(--muted);margin-top:2px}
.panel{background:white;border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.callout{background:var(--accent-soft);border:1px solid #d8d9ff;border-radius:11px;padding:16px 18px}
.question{background:#fff;border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;padding:20px 22px;margin:12px 0 18px}
.question .meta{font-family:'DM Mono',monospace;color:var(--accent);font-size:.72rem;text-transform:uppercase;letter-spacing:.08em}
.question .text{font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:1.3rem;line-height:1.5;margin-top:8px}
div.stButton>button{border-radius:8px;border:1px solid #d4dbea;background:#fff;color:var(--ink);font-weight:600;padding:.62rem 1rem}
div.stButton>button[kind="primary"]{background:var(--accent);border-color:var(--accent);color:white}
div.stButton>button[kind="primary"]:hover{background:#4848bd;border-color:#4848bd;color:white}
[data-baseweb="select"]>div{border-radius:8px;border-color:#d4dbea;background:white}
[data-testid="stMetric"]{background:white;border:1px solid var(--line);border-radius:12px;padding:12px}
div[data-testid="stPlotlyChart"],div[data-testid="stDataFrame"]{background:white;border:1px solid var(--line);border-radius:12px;padding:8px}
[data-testid="stAlert"]{border-radius:10px}
small,.muted{color:var(--muted)}
hr{border-color:var(--line)}
</style>
""", unsafe_allow_html=True)

for key, default in {
    "page": "Overview", "quiz_questions": [], "quiz_index": 0, "quiz_answers": {},
    "quiz_finished": False, "quiz_session_id": None, "seen_questions": set(),
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.markdown('<div class="brand">Learn<span>Loop</span></div>', unsafe_allow_html=True)
    st.caption("Adaptive practice · measurable progress")
    st.divider()
    page = st.radio("WORKSPACE", ["Overview", "Practice", "Learning analytics", "Model insights"],
                    index=["Overview", "Practice", "Learning analytics", "Model insights"].index(st.session_state.page))
    st.session_state.page = page
    st.divider()
    st.caption("MINI PROJECT · MACHINE LEARNING")
    st.caption("Recommendations use your saved practice history.")

stats = get_stats()
history = stats["history"]
attempts = stats["attempts"]
accuracy = stats["accuracy"]
correct_n = int(history["correct"].sum()) if attempts else 0
topics_seen = int(history["topic"].nunique()) if attempts else 0
topic_stats = (history.groupby(["subject", "topic"], as_index=False)
               .agg(attempts=("correct", "size"), accuracy=("correct", "mean"))
               if attempts else pd.DataFrame(columns=["subject", "topic", "attempts", "accuracy"]))
if not topic_stats.empty:
    topic_stats["accuracy_pct"] = topic_stats["accuracy"] * 100
    topic_stats["topic_label"] = topic_stats["topic"] + " · " + topic_stats["subject"]

def metric_card(label, value, hint):
    st.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div><div class="hint">{hint}</div></div>', unsafe_allow_html=True)

def page_header(title, subtitle, tag):
    st.markdown(f'<div class="page-head"><div><div class="eyebrow">LEARNLOOP / {tag}</div><h1>{title}</h1><p>{subtitle}</p></div><div class="tag">LOCAL DATA · SQLITE</div></div>', unsafe_allow_html=True)

if page == "Overview":
    page_header("Learning workspace", "A clear view of what you know, where you are improving, and what to practise next.", "OVERVIEW")
    cols = st.columns(4)
    with cols[0]: metric_card("Questions answered", f"{attempts}", "Saved attempts across all sessions")
    with cols[1]: metric_card("Overall accuracy", f"{accuracy:.1f}%", "Correct answers / total attempts")
    with cols[2]: metric_card("Topics practised", f"{topics_seen}", "Distinct subject-topic pairs")
    with cols[3]: metric_card("Correct answers", f"{correct_n}", "Questions answered correctly")
    st.write("")
    left, right = st.columns([1.45, 1])
    with left:
        st.subheader("Performance by topic")
        if topic_stats.empty:
            st.info("Answer some questions to populate topic-level performance.")
        else:
            chart = px.bar(topic_stats.sort_values("accuracy_pct"), x="accuracy_pct", y="topic_label",
                           orientation="h", color="accuracy_pct", color_continuous_scale=["#e4e7f3", "#5b5bd6"],
                           range_x=[0, 100], labels={"accuracy_pct":"Accuracy (%)","topic_label":"Topic"},
                           hover_data={"attempts":True,"accuracy_pct":":.1f","topic_label":True})
            chart.update_layout(height=max(300, 42*len(topic_stats)), margin=dict(l=10,r=10,t=15,b=10),
                                plot_bgcolor="white",paper_bgcolor="white",font=dict(color="#526079"),coloraxis_showscale=False,
                                xaxis=dict(showgrid=True,gridcolor="#edf0f5"),yaxis=dict(showgrid=False))
            st.plotly_chart(chart,use_container_width=True)
            st.caption("Read alongside the attempt count: a percentage based on one answer is not yet a reliable mastery estimate.")
    with right:
        st.subheader("Recommended next topic")
        rec = recommend_topic()
        st.markdown(f'<div class="callout"><div class="eyebrow">PERSONALISED PRACTICE</div><h3>{rec["topic"]}</h3><p>{rec["reason"]}</p></div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Start practice", type="primary", use_container_width=True):
            st.session_state.page = "Practice"
            st.rerun()
        st.subheader("Recent activity")
        if history.empty:
            st.caption("No saved attempts yet.")
        else:
            recent = history.tail(6).iloc[::-1].copy()
            recent["Result"] = recent["correct"].map({1:"Correct",0:"Incorrect"})
            recent["When"] = pd.to_datetime(recent["created_at"], errors="coerce").dt.strftime("%d %b, %H:%M")
            st.dataframe(recent[["When","subject","topic","difficulty","Result"]].rename(
                columns={"subject":"Subject","topic":"Topic","difficulty":"Level"}), hide_index=True, use_container_width=True)

elif page == "Practice":
    page_header("Practice session", "Choose a topic and difficulty. LearnLoop never silently swaps your selected level.", "PRACTICE")
    subjects = ["Python", "Machine Learning", "DBMS", "Data Structures"]
    subject = st.selectbox("Subject", subjects)
    topics = get_available_topics(subject)
    topic = st.selectbox("Topic", topics)
    levels = get_available_difficulties(subject, topic)
    difficulty = st.selectbox("Difficulty", levels, index=0)
    available = get_available_question_count(subject, topic, difficulty)
    st.caption(f"{available} unique questions currently available for this topic and level.")
    count = st.selectbox("Questions in this session", [3, 5, 8, 10], index=1)
    if count > available:
        st.warning(f"Only {available} questions are available for this exact selection. The session will contain {available}; no question will be duplicated.")
    if st.button("Start session", type="primary", disabled=(available == 0)):
        for key in list(st.session_state.keys()):
            if key.startswith("feedback_") or key.startswith("answer_") or key.startswith("lock_") or key.startswith("next_"):
                del st.session_state[key]
        excluded = st.session_state.seen_questions
        questions = get_questions(subject, topic, difficulty, count, exclude_questions=excluded)
        if not questions:
            # If the learner has seen the entire bank, start a new review cycle, still without within-session repeats.
            questions = get_questions(subject, topic, difficulty, count)
            st.session_state.seen_questions = set()
        st.session_state.quiz_questions = questions
        st.session_state.quiz_subject = subject
        st.session_state.quiz_topic = topic
        st.session_state.quiz_difficulty = difficulty
        st.session_state.quiz_index = 0
        st.session_state.quiz_answers = {}
        st.session_state.quiz_finished = False
        st.session_state.quiz_session_id = str(uuid.uuid4())
        st.session_state.page = "Practice"
        st.rerun()

    questions = st.session_state.quiz_questions
    if questions and not st.session_state.quiz_finished:
        idx = st.session_state.quiz_index
        q = questions[idx]
        st.progress((idx + 1) / len(questions), text=f"Question {idx + 1} of {len(questions)}")
        st.markdown(f'<div class="question"><div class="meta">{st.session_state.quiz_subject} / {st.session_state.quiz_topic} / {st.session_state.quiz_difficulty}</div><div class="text">{q["question"]}</div></div>', unsafe_allow_html=True)
        choice = st.radio("Select one answer", q["options"], index=None, key=f"answer_{idx}", label_visibility="collapsed")
        if st.button("Check answer", type="primary", key=f"lock_{idx}", disabled=(choice is None or f"feedback_{idx}" in st.session_state)):
            st.session_state.quiz_answers[idx] = choice
            correct = choice == q["answer"]
            record_attempt(st.session_state.quiz_subject, st.session_state.quiz_topic,
                           st.session_state.quiz_difficulty, correct, q["question"], st.session_state.quiz_session_id)
            st.session_state.seen_questions.add(q["question"])
            st.session_state[f"feedback_{idx}"] = (correct, q["explanation"])
            st.rerun()
        feedback = st.session_state.get(f"feedback_{idx}")
        if feedback:
            if feedback[0]:
                st.success("Correct answer")
            else:
                st.error(f"Correct answer: {q['answer']}")
            st.write(feedback[1])
            if idx + 1 < len(questions):
                if st.button("Next question", type="primary", key=f"next_{idx}"):
                    st.session_state.quiz_index += 1
                    st.rerun()
            elif st.button("Complete session", type="primary", key="finish"):
                st.session_state.quiz_finished = True
                st.rerun()
    if questions and st.session_state.quiz_finished:
        correct_count = sum(st.session_state.quiz_answers.get(i) == q["answer"] for i,q in enumerate(questions))
        pct = correct_count / len(questions) * 100
        st.subheader("Session summary")
        cols = st.columns(3)
        with cols[0]: metric_card("Correct", f"{correct_count}/{len(questions)}", "Answers correct this session")
        with cols[1]: metric_card("Session accuracy", f"{pct:.1f}%", "For this session only")
        with cols[2]: metric_card("Difficulty", st.session_state.quiz_difficulty, st.session_state.quiz_topic)
        st.write("")
        st.caption("Your answers were saved locally and are now included in your learning history.")
        if st.button("Start another session", type="primary"):
            st.session_state.quiz_questions = []
            st.session_state.quiz_finished = False
            st.session_state.quiz_answers = {}
            st.rerun()

elif page == "Learning analytics":
    page_header("Learning analytics", "Inspect accuracy, topic coverage, difficulty performance and changes over time.", "ANALYTICS")
    if history.empty:
        st.info("Your analytics will appear after your first answered question.")
    else:
        dates = pd.to_datetime(history["created_at"], errors="coerce")
        daily = history.assign(date=dates.dt.date).dropna(subset=["date"]).groupby("date",as_index=False).agg(
            attempts=("correct","size"), accuracy=("correct","mean"))
        daily["accuracy_pct"] = daily["accuracy"]*100
        left,right=st.columns([1.5,1])
        with left:
            st.subheader("Accuracy over time")
            if daily.empty:
                st.caption("Timestamps are not available for the existing history.")
            else:
                fig=px.line(daily,x="date",y="accuracy_pct",markers=True,range_y=[0,100],
                            labels={"date":"Date","accuracy_pct":"Accuracy (%)"})
                fig.update_traces(line=dict(color="#5b5bd6",width=3),marker=dict(size=8))
                fig.update_layout(height=320,margin=dict(l=10,r=10,t=10,b=10),plot_bgcolor="white",paper_bgcolor="white",
                                  xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#edf0f5"))
                st.plotly_chart(fig,use_container_width=True)
        with right:
            st.subheader("Accuracy by difficulty")
            diff=history.groupby("difficulty",as_index=False).agg(attempts=("correct","size"),accuracy=("correct","mean"))
            diff["accuracy_pct"]=diff["accuracy"]*100
            diff["difficulty"]=pd.Categorical(diff["difficulty"],["Beginner","Intermediate","Advanced"],ordered=True)
            diff=diff.sort_values("difficulty")
            fig=px.bar(diff,x="difficulty",y="accuracy_pct",range_y=[0,100],text="attempts",
                       labels={"difficulty":"Difficulty","accuracy_pct":"Accuracy (%)","attempts":"Attempts"},
                       color_discrete_sequence=["#5b5bd6"])
            fig.update_traces(texttemplate="%{text} attempts",textposition="outside")
            fig.update_layout(height=320,margin=dict(l=10,r=10,t=10,b=20),plot_bgcolor="white",paper_bgcolor="white",
                              yaxis=dict(gridcolor="#edf0f5"))
            st.plotly_chart(fig,use_container_width=True)
        st.subheader("Topic mastery table")
        mastery=topic_stats[["subject","topic","attempts","accuracy_pct"]].copy()
        mastery["accuracy_pct"]=mastery["accuracy_pct"].round(1)
        mastery["signal"]=mastery.apply(lambda r:"Limited evidence" if r["attempts"]<5 else ("Needs practice" if r["accuracy_pct"]<65 else ("Developing" if r["accuracy_pct"]<80 else "Strong")),axis=1)
        st.dataframe(mastery.rename(columns={"subject":"Subject","topic":"Topic","attempts":"Attempts","accuracy_pct":"Accuracy (%)","signal":"Interpretation"}),hide_index=True,use_container_width=True)
        st.caption("Interpretation is a simple practice heuristic, not a formal psychometric mastery score. Fewer than five attempts are labelled limited evidence.")
        st.subheader("Recent answers")
        recent=history.tail(20).iloc[::-1].copy()
        recent["Result"]=recent["correct"].map({1:"Correct",0:"Incorrect"})
        recent["Date"]=pd.to_datetime(recent["created_at"],errors="coerce").dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(recent[["Date","subject","topic","difficulty","question_text","Result"]].rename(
            columns={"subject":"Subject","topic":"Topic","difficulty":"Level","question_text":"Question"}),hide_index=True,use_container_width=True)

elif page == "Model insights":
    page_header("Model insights", "See what the recommendation model has learned, how it is evaluated, and when its evidence is insufficient.", "MODEL")
    st.subheader("Recommendation pipeline")
    st.markdown('<div class="panel"><b>1 · Capture</b> — each answer is stored in SQLite with subject, topic, difficulty and outcome.<br><br><b>2 · Features</b> — historical topic accuracy, number of prior attempts and difficulty level.<br><br><b>3 · Model</b> — Logistic Regression estimates probability of a correct answer when enough labelled history exists.<br><br><b>4 · Recommendation</b> — topics with lower estimated success and weaker historical accuracy are prioritised; unseen topics receive an exploration bonus.</div>',unsafe_allow_html=True)
    st.write("")
    evaluation=evaluate_model()
    if not evaluation.get("ready"):
        st.warning(evaluation.get("message","Not enough data to evaluate the model."))
        st.caption(f"Current saved attempts: {attempts}. Evaluation requires at least 20 usable records and both correct and incorrect outcomes.")
    else:
        cols=st.columns(4)
        for col,label,key in zip(cols,["Cross-validated accuracy","Precision","Recall","F1-score"],["accuracy","precision","recall","f1"]):
            with col: metric_card(label,f'{evaluation[key]*100:.1f}%',"Stratified cross-validation")
        st.write("")
        st.markdown(f'<div class="panel"><b>Evaluation setup</b><br>{evaluation["folds"]}-fold stratified cross-validation; metrics are calculated on held-out folds, not the fitted training predictions.<br><br><b>Majority-class baseline accuracy:</b> {evaluation["baseline_accuracy"]*100:.1f}%<br><b>Records:</b> {evaluation["rows"]} · <b>Correct:</b> {evaluation["correct"]} · <b>Incorrect:</b> {evaluation["incorrect"]}</div>',unsafe_allow_html=True)
        st.caption("These metrics describe predicting correctness from logged features; they are not a benchmark of quiz difficulty or learning gain. Results can be unstable on a small history.")
    st.subheader("Current data coverage")
    coverage=history.groupby(["subject","difficulty"],as_index=False).agg(attempts=("correct","size"),accuracy=("correct","mean")) if attempts else pd.DataFrame()
    if coverage.empty:
        st.info("No model training data yet.")
    else:
        coverage["accuracy_pct"]=(coverage["accuracy"]*100).round(1)
        st.dataframe(coverage[["subject","difficulty","attempts","accuracy_pct"]].rename(columns={"subject":"Subject","difficulty":"Difficulty","attempts":"Attempts","accuracy_pct":"Accuracy (%)"}),hide_index=True,use_container_width=True)
