import sys
from pathlib import Path

import streamlit as st


# ----------------------------------------
# Add project root to Python path
# ----------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ----------------------------------------
# Backend imports
# ----------------------------------------

from backend.services.document_processor import (
    save_uploaded_file,
    process_document,
    process_and_store_document
)

from backend.services.summary_generator import (
    generate_document_summary
)


# ----------------------------------------
# Page
# ----------------------------------------

st.title("📤 Upload Study Material")

st.write(
    "Upload your PDF, DOCX, PPTX or TXT study material."
)


# ----------------------------------------
# File uploader
# ----------------------------------------

uploaded_file = st.file_uploader(
    "Choose a study document",
    type=[
        "pdf",
        "docx",
        "pptx",
        "txt"
    ]
)


# ----------------------------------------
# Process uploaded file
# ----------------------------------------

if uploaded_file:

    file_key = (
        uploaded_file.name,
        uploaded_file.size
    )

    if file_key != st.session_state.current_file_key:

        with st.spinner(
            "Processing document..."
        ):

            file_path = save_uploaded_file(
                uploaded_file
            )

            pages = process_document(
                file_path
            )

            storage_result = (
                process_and_store_document(
                    file_path,
                    pages
                )
            )


        # --------------------------------
        # Store document information
        # --------------------------------

        st.session_state.current_file_key = (
            file_key
        )

        st.session_state.current_document_id = (
            storage_result["document_id"]
        )

        st.session_state.current_filename = (
            uploaded_file.name
        )

        st.session_state.current_pages = pages


        # --------------------------------
        # Reset learning progress
        # --------------------------------

        st.session_state.roadmap = None

        st.session_state.completed_nodes = set()

        st.session_state.topic_quizzes = {}

        st.session_state.quiz_scores = {}


        # --------------------------------
        # Success messages
        # --------------------------------

        st.success(
            "File uploaded and processed!"
        )

        st.success(
            f"Extracted {len(pages)} sections."
        )

        st.success(
            f"Stored {storage_result['chunks']} "
            "chunks in PostgreSQL."
        )


# ========================================
# Current Document
# ========================================

if st.session_state.current_document_id:

    st.divider()

    st.subheader("📄 Current Document")

    st.info(
        f"Filename: "
        f"{st.session_state.current_filename}\n\n"
        f"Document ID: "
        f"{st.session_state.current_document_id}"
    )


# ========================================
# Generate Summary
# ========================================

if st.session_state.current_document_id:

    st.divider()

    st.subheader("📝 Document Summary")

    st.write(
        "Generate an AI summary of your uploaded "
        "study material."
    )

    if st.button(
        "✨ Generate Summary",
        key="generate_summary"
    ):

        with st.spinner(
            "Generating summary..."
        ):

            summary_result = (
                generate_document_summary(
                    st.session_state.current_document_id
                )
            )

        # --------------------------------
        # Display summary
        # --------------------------------

        st.markdown("### 📖 Summary")

        st.markdown(
            summary_result["summary"]
        )

        # --------------------------------
        # Display sources
        # --------------------------------

        st.markdown("### 📚 Sources")

        displayed_sources = set()

        for source in summary_result["sources"]:

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