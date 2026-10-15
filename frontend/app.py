import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))




st.set_page_config(
    page_title="AI Study Companion",
    page_icon="📚",
    layout="wide"
)


if "current_document_id" not in st.session_state:
    st.session_state.current_document_id = None

if "current_filename" not in st.session_state:
    st.session_state.current_filename = None

if "current_file_key" not in st.session_state:
    st.session_state.current_file_key = None

if "current_pages" not in st.session_state:
    st.session_state.current_pages = None

if "roadmap" not in st.session_state:
    st.session_state.roadmap = None

if "completed_nodes" not in st.session_state:
    st.session_state.completed_nodes = set()

if "topic_quizzes" not in st.session_state:
    st.session_state.topic_quizzes = {}

if "quiz_scores" not in st.session_state:
    st.session_state.quiz_scores = {}

st

st.title("📚 AI Study Companion")

st.write(
    "Upload your study material and turn it into "
    "summaries, roadmaps, quizzes and flashcards."
)

st.info(
    "Use the pages in the sidebar to get started."
)