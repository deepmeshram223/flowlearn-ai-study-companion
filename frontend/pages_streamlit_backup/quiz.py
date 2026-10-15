import sys
from pathlib import Path
import json
import re

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.rag import answer_question


st.title("🧠 Quiz")


# ========================================
# Check document
# ========================================

if not st.session_state.current_document_id:

    st.info(
        "📤 Please upload a study document first."
    )

    st.stop()


# ========================================
# Check roadmap
# ========================================

if not st.session_state.roadmap:

    st.info(
        "🗺️ Please generate a learning roadmap first."
    )

    st.stop()


# ========================================
# Get all roadmap nodes
# ========================================

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


# ========================================
# Select topic
# ========================================

st.subheader("📚 Select a Topic")

topic_options = {}

for node in all_nodes:

    node_id = node.get("id")
    title = node.get(
        "title",
        "Untitled Topic"
    )

    topic_options[title] = node_id


selected_title = st.selectbox(
    "Choose a topic for your quiz",
    list(topic_options.keys())
)


selected_node_id = topic_options[
    selected_title
]


# ========================================
# Find selected node
# ========================================

selected_node = None

for node in all_nodes:

    if node.get("id") == selected_node_id:

        selected_node = node
        break


if not selected_node:
    st.error("Unable to find selected topic.")
    st.stop()


# ========================================
# Check if topic is unlocked
# ========================================

prerequisites = selected_node.get(
    "prerequisites",
    []
)

is_unlocked = all(
    prerequisite
    in st.session_state.completed_nodes
    for prerequisite in prerequisites
)


if prerequisites:

    st.write("### 🔗 Prerequisites")

    for prerequisite in prerequisites:

        prerequisite_node = next(
            (
                node
                for node in all_nodes
                if node.get("id") == prerequisite
            ),
            None
        )

        if prerequisite_node:

            prerequisite_title = (
                prerequisite_node.get(
                    "title",
                    prerequisite
                )
            )

            if prerequisite in st.session_state.completed_nodes:

                st.write(
                    f"✅ {prerequisite_title}"
                )

            else:

                st.write(
                    f"🔒 {prerequisite_title}"
                )


if not is_unlocked:

    st.warning(
        "🔒 Complete the prerequisites for this topic before taking the quiz."
    )

    st.stop()


# ========================================
# Topic information
# ========================================

st.divider()

st.subheader(
    f"📘 {selected_node.get('title', 'Topic')}"
)

st.write(
    selected_node.get(
        "description",
        "No description available."
    )
)


# ========================================
# Generate Quiz
# ========================================

if st.button(
    "✨ Generate Quiz",
    key=f"generate_quiz_{selected_node_id}"
):

    with st.spinner(
        "Generating quiz from your study material..."
    ):

        topic_title = selected_node.get(
            "title",
            "this topic"
        )

        topic_description = selected_node.get(
            "description",
            ""
        )

        quiz_prompt = f"""
Create a 5-question multiple-choice quiz
about the topic "{topic_title}".

Use ONLY the uploaded study material.

Topic description:
{topic_description}

For each question provide:

- question
- 4 options
- correct answer
- short explanation

Return ONLY valid JSON in exactly this format:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": "Option A",
            "explanation": "Why this answer is correct."
        }}
    ]
}}

Create exactly 5 questions.
"""

        quiz_result = answer_question(
            quiz_prompt,
            document_id=(
                st.session_state.current_document_id
            ),
            limit=5
        )

        raw_quiz = quiz_result["answer"]

        # Remove markdown code fences
        raw_quiz = re.sub(
            r"```json|```",
            "",
            raw_quiz
        ).strip()

        try:

            quiz_data = json.loads(
                raw_quiz
            )

            questions = quiz_data.get(
                "questions",
                []
            )

            if len(questions) != 5:

                st.error(
                    "The AI did not generate exactly 5 questions. "
                    "Please generate the quiz again."
                )

            else:

                st.session_state.topic_quizzes[
                    selected_node_id
                ] = quiz_data

                st.session_state.quiz_scores.pop(
                    selected_node_id,
                    None
                )

                # Clear old answers
                for index in range(5):

                    st.session_state.pop(
                        f"answer_{selected_node_id}_{index}",
                        None
                    )

                st.session_state.pop(
                    f"quiz_submitted_{selected_node_id}",
                    None
                )

                st.success(
                    "Quiz generated!"
                )

        except json.JSONDecodeError:

            st.error(
                "The AI returned an invalid quiz format. "
                "Please generate the quiz again."
            )


# ========================================
# Display Quiz
# ========================================

if selected_node_id not in st.session_state.topic_quizzes:

    st.info(
        "Click **Generate Quiz** to create a quiz for this topic."
    )

    st.stop()


quiz_data = st.session_state.topic_quizzes[
    selected_node_id
]

questions = quiz_data.get(
    "questions",
    []
)


st.divider()

st.subheader("📝 Test Yourself")


# ========================================
# Quiz submission
# ========================================

for index, question in enumerate(
    questions
):

    st.markdown(
        f"### Question {index + 1}"
    )

    st.write(
        question.get(
            "question",
            "Question unavailable."
        )
    )

    options = question.get(
        "options",
        []
    )

    st.radio(
        "Choose your answer:",
        options,
        key=f"answer_{selected_node_id}_{index}",
        index=None
    )


# ========================================
# Submit Quiz
# ========================================

if st.button(
    "📊 Submit Quiz",
    key=f"submit_quiz_{selected_node_id}"
):

    score = 0

    unanswered = 0

    for index, question in enumerate(
        questions
    ):

        user_answer = st.session_state.get(
            f"answer_{selected_node_id}_{index}"
        )

        correct_answer = question.get(
            "answer"
        )

        if not user_answer:

            unanswered += 1

        elif user_answer == correct_answer:

            score += 1


    st.session_state.quiz_scores[
        selected_node_id
    ] = score

    st.session_state[
        f"quiz_submitted_{selected_node_id}"
    ] = True


# ========================================
# Show Results
# ========================================

if st.session_state.get(
    f"quiz_submitted_{selected_node_id}",
    False
):

    score = st.session_state.quiz_scores[
        selected_node_id
    ]

    total = len(questions)

    st.divider()

    st.subheader("🏆 Quiz Result")

    st.write(
        f"### Score: {score} / {total}"
    )

    if total > 0:

        st.progress(
            score / total
        )


    # ====================================
    # Review answers
    # ====================================

    st.subheader("📋 Review")

    for index, question in enumerate(
        questions
    ):

        user_answer = st.session_state.get(
            f"answer_{selected_node_id}_{index}"
        )

        correct_answer = question.get(
            "answer"
        )

        explanation = question.get(
            "explanation",
            ""
        )

        st.markdown(
            f"**{index + 1}. "
            f"{question.get('question', '')}**"
        )

        if user_answer == correct_answer:

            st.success(
                f"✅ Your answer: {user_answer}"
            )

        elif user_answer:

            st.error(
                f"❌ Your answer: {user_answer}"
            )

            st.info(
                f"Correct answer: {correct_answer}"
            )

        else:

            st.warning(
                "⚠️ You did not answer this question."
            )

            st.info(
                f"Correct answer: {correct_answer}"
            )

        if explanation:

            st.caption(
                f"💡 {explanation}"
            )