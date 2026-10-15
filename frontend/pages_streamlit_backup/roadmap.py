import sys
from pathlib import Path

import streamlit as st

from streamlit_agraph import agraph, Node, Edge, Config


# ========================================
# Add project root to Python path
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ========================================
# Backend imports
# ========================================

from backend.services.rag import answer_question

from backend.services.roadmap_generator import (
    generate_roadmap
)


# ========================================
# Page title
# ========================================

st.title("🗺️ Learning Roadmap")


# ========================================
# Check whether a node is unlocked
# ========================================

def is_node_unlocked(node):

    prerequisites = node.get(
        "prerequisites",
        []
    )

    if not prerequisites:
        return True

    completed_nodes = (
        st.session_state.completed_nodes
    )

    return all(
        prerequisite in completed_nodes
        for prerequisite in prerequisites
    )


# ========================================
# Find node by ID
# ========================================

def find_node_by_id(roadmap, node_id):

    for phase in roadmap.get(
        "phases",
        []
    ):

        for node in phase.get(
            "nodes",
            []
        ):

            if node.get("id") == node_id:
                return node

    return None


# ========================================
# Roadmap graph
# ========================================

def display_roadmap_graph(roadmap):

    nodes = []
    edges = []

    phase_x_positions = [
        150,
        550,
        950
    ]

    row_y_positions = [
        150,
        350,
        550
    ]

    # ------------------------------------
    # Create nodes
    # ------------------------------------

    for phase_index, phase in enumerate(
        roadmap.get("phases", [])
    ):

        if phase_index >= len(
            phase_x_positions
        ):
            break

        x_position = phase_x_positions[
            phase_index
        ]

        for node_index, node in enumerate(
            phase.get("nodes", [])
        ):

            y_position = row_y_positions[
                node_index % len(row_y_positions)
            ]

            node_id = node.get(
                "id",
                f"node_{phase_index}_{node_index}"
            )

            label = node.get(
                "title",
                "Untitled Topic"
            )

            # --------------------------------
            # Node state
            # --------------------------------

            unlocked = is_node_unlocked(
                node
            )

            completed = (
                node_id
                in st.session_state.completed_nodes
            )

            # --------------------------------
            # Node label
            # --------------------------------

            if completed:

                label = "✓ " + label

            elif not unlocked:

                label = "🔒 " + label

            elif node.get("checkpoint"):

                label = "★ " + label

            # --------------------------------
            # Node size
            # --------------------------------

            node_size = 30

            if completed:
                node_size = 35

            # --------------------------------
            # Create node
            # --------------------------------

            nodes.append(
                Node(
                    id=node_id,
                    label=label,
                    size=node_size,
                    shape="box",
                    borderWidth=2,
                    x=x_position,
                    y=y_position,
                    fixed=True,
                    physics=False,
                    font={
                        "size": 15
                    }
                )
            )

    # ------------------------------------
    # Create connections
    # ------------------------------------

    for connection in roadmap.get(
        "connections",
        []
    ):

        edges.append(
            Edge(
                source=connection["from"],
                target=connection["to"],
                label=""
            )
        )

    # ------------------------------------
    # Graph configuration
    # ------------------------------------

    config = Config(
        width=1100,
        height=700,
        directed=True,
        physics=False,
        hierarchical=False
    )

    selected_node = agraph(
        nodes=nodes,
        edges=edges,
        config=config
    )

    return selected_node


# ========================================
# Check document
# ========================================

if not st.session_state.current_document_id:

    st.info(
        "📤 Please upload a study document first."
    )

    st.stop()


# ========================================
# Generate roadmap
# ========================================

if st.session_state.current_pages:

    if st.button(
        "Generate Learning Roadmap"
    ):

        with st.spinner(
            "Generating your learning roadmap..."
        ):

            document_text = "\n\n".join(
                f"Page {page['page']}:\n{page['text']}"
                for page in st.session_state.current_pages
            )

            roadmap = generate_roadmap(
                document_text
            )

        st.session_state.roadmap = roadmap

        # Reset progress for new roadmap
        st.session_state.completed_nodes = set()

        # Reset quizzes for new roadmap
        st.session_state.topic_quizzes = {}

        st.session_state.quiz_scores = {}

        st.success(
            "Learning roadmap generated!"
        )


# ========================================
# Display generated roadmap
# ========================================

if st.session_state.roadmap:

    st.subheader(
        "Interactive Learning Roadmap"
    )

    # ------------------------------------
    # Roadmap progress
    # ------------------------------------

    all_nodes = []

    for phase in st.session_state.roadmap.get(
        "phases",
        []
    ):

        for node in phase.get(
            "nodes",
            []
        ):

            all_nodes.append(node)

    total_nodes = len(all_nodes)

    completed_count = len(
        st.session_state.completed_nodes
        & {
            node["id"]
            for node in all_nodes
        }
    )

    if total_nodes > 0:

        progress = (
            completed_count / total_nodes
        )

        st.write(
            f"**Roadmap Progress: "
            f"{completed_count} / "
            f"{total_nodes} topics completed**"
        )

        st.progress(progress)

    # ------------------------------------
    # Phase headers
    # ------------------------------------

    phases = st.session_state.roadmap.get(
        "phases",
        []
    )

    if phases:

        phase_columns = st.columns(
            len(phases)
        )

        for index, phase in enumerate(
            phases
        ):

            with phase_columns[index]:

                st.markdown(
                    f"### {phase.get('title', 'Phase')}"
                )

                st.caption(
                    phase.get(
                        "description",
                        ""
                    )
                )

    # ------------------------------------
    # Roadmap graph
    # ------------------------------------

    selected_node = display_roadmap_graph(
        st.session_state.roadmap
    )

    # ------------------------------------
    # Selected node information
    # ------------------------------------

    if selected_node:

        selected_data = find_node_by_id(
            st.session_state.roadmap,
            selected_node
        )

        if selected_data:

            st.divider()

            st.subheader(
                f"📘 {selected_data.get('title', 'Topic')}"
            )

            # --------------------------------
            # Topic status
            # --------------------------------

            node_id = selected_data["id"]

            is_completed = (
                node_id
                in st.session_state.completed_nodes
            )

            is_unlocked = is_node_unlocked(
                selected_data
            )

            if is_completed:

                st.success(
                    "✓ Completed"
                )

            elif is_unlocked:

                st.success(
                    "🔓 Available"
                )

            else:

                st.warning(
                    "🔒 Locked"
                )

            # --------------------------------
            # Completion checkbox
            # --------------------------------

            if is_unlocked or is_completed:

                completed = st.checkbox(
                    "Mark this topic as completed",
                    value=is_completed,
                    key=f"completed_{node_id}"
                )

                if completed:

                    st.session_state.completed_nodes.add(
                        node_id
                    )

                else:

                    st.session_state.completed_nodes.discard(
                        node_id
                    )

            else:

                st.info(
                    "Complete the prerequisites "
                    "below to unlock this topic."
                )

            # --------------------------------
            # Description
            # --------------------------------

            st.write(
                selected_data.get(
                    "description",
                    "No description available."
                )
            )

            # --------------------------------
            # Difficulty / Time
            # --------------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.caption(
                    f"🎯 Difficulty: "
                    f"{selected_data.get('difficulty', 'N/A')}"
                )

            with col2:

                st.caption(
                    f"⏱️ Estimated time: "
                    f"{selected_data.get('estimated_minutes', 'N/A')} minutes"
                )

            # --------------------------------
            # Prerequisites
            # --------------------------------

            prerequisites = selected_data.get(
                "prerequisites",
                []
            )

            if prerequisites:

                st.markdown(
                    "### 🔗 Prerequisites"
                )

                for prerequisite in prerequisites:

                    prerequisite_node = find_node_by_id(
                        st.session_state.roadmap,
                        prerequisite
                    )

                    if prerequisite_node:

                        prerequisite_title = (
                            prerequisite_node.get(
                                "title",
                                prerequisite
                            )
                        )

                        if prerequisite in (
                            st.session_state.completed_nodes
                        ):

                            st.write(
                                f"✅ {prerequisite_title}"
                            )

                        else:

                            st.write(
                                f"🔒 {prerequisite_title}"
                            )

            # --------------------------------
            # Source pages
            # --------------------------------

            source_pages = selected_data.get(
                "source_pages",
                []
            )

            if source_pages:

                st.markdown(
                    "### 📚 Source Pages"
                )

                st.write(
                    ", ".join(
                        str(page)
                        for page in source_pages
                    )
                )

            # --------------------------------
            # Study This Topic
            # --------------------------------

            if is_unlocked:

                st.markdown(
                    "### 📖 Study This Topic"
                )

                if st.button(
                    "Teach Me This Topic",
                    key=f"study_{node_id}"
                ):

                    with st.spinner(
                        "AI is teaching you this topic..."
                    ):

                        topic_title = selected_data.get(
                            "title",
                            "this topic"
                        )

                        topic_description = selected_data.get(
                            "description",
                            ""
                        )

                        study_question = f"""
Teach me the topic "{topic_title}" using only the uploaded study material.

Topic description:
{topic_description}

Explain:

1. What this topic means
2. The important concepts I need to understand
3. How the concepts work
4. Important examples from the study material
5. Key points I should remember

Keep the explanation clear and suitable for a student.
"""

                        topic_result = answer_question(
                            study_question,
                            document_id=(
                                st.session_state.current_document_id
                            ),
                            limit=5
                        )

                    st.markdown(
                        "#### 🤖 AI Explanation"
                    )

                    st.markdown(
                        topic_result["answer"]
                    )

                    st.markdown(
                        "#### 📚 Sources"
                    )

                    displayed_sources = set()

                    for source in topic_result["sources"]:

                        source_key = (
                            source["filename"],
                            source["page_number"]
                        )

                        if source_key not in displayed_sources:

                            displayed_sources.add(
                                source_key
                            )

                            st.write(
                                f"📄 {source['filename']} — "
                                f"Page {source['page_number']}"
                            )

            else:

                st.info(
                    "🔒 Unlock this topic to study it."
                )