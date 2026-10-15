import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { askQuestion } from "../services/api";
import "./TutorPage.css";

function TutorPage() {
    const { documentId } = useParams();
    const navigate = useNavigate();

    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    async function handleSubmit(event) {
        event.preventDefault();

        const trimmedQuestion = question.trim();

        if (!trimmedQuestion || loading) {
            return;
        }

        setMessages((previous) => [
            ...previous,
            {
                role: "user",
                content: trimmedQuestion,
            },
        ]);

        setQuestion("");
        setLoading(true);

        try {
            const result = await askQuestion(
                trimmedQuestion,
                documentId
            );

            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content: result.answer,
                    sources: result.sources || [],
                },
            ]);
        } catch (error) {
            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content:
                        error.message ||
                        "Something went wrong while generating the answer.",
                },
            ]);
        } finally {
            setLoading(false);
        }
    }

    return (
        <main className="tutor-page">

            <button
                className="tutor-back"
                onClick={() => navigate(`/study/${documentId}`)}
            >
                ← study set
            </button>

            <header className="tutor-header">
                <p className="tutor-eyebrow">
                    flowlearn / tutor
                </p>

                <h1>Ask your material.</h1>

                <p>
                    Ask questions and get answers grounded in
                    your uploaded study material.
                </p>
            </header>

            <section className="chat-area">

                {messages.length === 0 && (
                    <div className="tutor-empty">

                        <p className="empty-label">
                            try asking
                        </p>

                        <button
    className="suggested-question"
    onClick={() =>
        setQuestion(
            "What are the main concepts covered in this material?"
        )
    }
>
    What are the main concepts covered in this material?
</button>

<button
    className="suggested-question"
    onClick={() =>
        setQuestion(
            "Explain this topic in simple terms."
        )
    }
>
    Explain this topic in simple terms.
</button>

<button
    className="suggested-question"
    onClick={() =>
        setQuestion(
            "What are the important points I should remember?"
        )
    }
>
    What are the important points I should remember?
</button>

                    </div>
                )}

                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`message ${message.role}`}
                    >

                        <div className="message-role">
                            {message.role === "user"
                                ? "you"
                                : "tutor"}
                        </div>

                        <div className="message-content">
                            {message.content}
                        </div>

                        {message.sources &&
                            message.sources.length > 0 && (
                                <div className="message-sources">

                                    <span>
                                        sources
                                    </span>

                                    {message.sources.map(
    (source, sourceIndex) => (
        <div
            key={sourceIndex}
            className="source"
        >
            <span>
                {source.filename}
            </span>

            <span>
                page {source.page_number}
            </span>
        </div>
    )
)}
                                </div>
                            )}

                    </div>
                ))}

                {loading && (
                    <div className="message assistant">

                        <div className="message-role">
                            tutor
                        </div>

                        <div className="thinking">
                            thinking...
                        </div>

                    </div>
                )}

            </section>

            <form
                className="tutor-input-area"
                onSubmit={handleSubmit}
            >

               <textarea
    value={question}
    onChange={(event) =>
        setQuestion(event.target.value)
    }
    onKeyDown={(event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();

            if (
                question.trim() &&
                !loading
            ) {
                handleSubmit(event);
            }
        }
    }}
    placeholder="Ask anything about your study material..."
    rows={3}
    disabled={loading}
/>

                <div className="input-footer">

                    <span>
                        grounded in your material
                    </span>

                    <button
                        type="submit"
                        disabled={
                            loading ||
                            !question.trim()
                        }
                    >
                        {loading ? "thinking..." : "ask"}
                    </button>

                </div>

            </form>

        </main>
    );
}

export default TutorPage;