import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.rag import answer_question


st.title("📊 Study Dashboard")


# ========================================
# Check document
# ========================================

if not st.session_state.current_document_id:

    st.info(
        "📤 Please upload a study document first."
    )

    st.stop()


# ========================================
# Document Information
# ========================================

st.header("📄 Current Document")

st.info(
    f"Filename: {st.session_state.current_filename}\n\n"
    f"Document ID: {st.session_state.current_document_id}"
)


# ========================================
# Extracted Text
# ========================================

st.divider()

st.header("📖 Extracted Text")

if st.session_state.current_pages:

    for page in st.session_state.current_pages:

        with st.expander(
            f"Page / Section {page['page']}"
        ):

            st.write(
                page["text"]
            )


# ========================================
# Question Answering
# ========================================

st.divider()

st.header("💬 Ask Your Study Material")

question = st.text_area(
    "Enter your question",
    placeholder=(
        "Example: What is CPU scheduling?"
    )
)


if st.button("🔍 Ask Question"):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching your study material..."
        ):

            answer_result = answer_question(
                question,
                document_id=(
                    st.session_state.current_document_id
                ),
                limit=5
            )

        st.subheader("Answer")

        st.markdown(
            answer_result["answer"]
        )

        st.subheader("📚 Sources")

        displayed_sources = set()

        for source in answer_result["sources"]:

            source_key = (
                source["filename"],
                source["page_number"]
            )

            if source_key not in displayed_sources:

                displayed_sources.add(
                    source_key
                )

                st.write(
                    f"📄 {source['filename']} "
                    f"— Page {source['page_number']}"
                )