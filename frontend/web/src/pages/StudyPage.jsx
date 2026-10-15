import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getDocuments } from "../services/api";
import "./StudyPage.css";

function StudyPage() {
    const navigate = useNavigate();
    const { documentId } = useParams();

    const [document, setDocument] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadDocument() {
            try {
                const documents = await getDocuments();

                const currentDocument = documents.find(
                    (item) => item.id === Number(documentId)
                );

                if (!currentDocument) {
                    throw new Error("Study set not found.");
                }

                setDocument(currentDocument);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        }

        loadDocument();
    }, [documentId]);

    const modes = [
        {
            name: "tutor",
            description: "Ask questions about your material",
            path: `/study/${documentId}/tutor`,
        },
        {
            name: "flashcards",
            description: "Review concepts and remember more",
            path: `/study/${documentId}/flashcards`,
        },
        {
            name: "quiz",
            description: "Test yourself with questions",
            path: `/study/${documentId}/quiz`,
        },
        {
            name: "written test",
            description: "Practice explaining answers",
            path: `/study/${documentId}/test`,
        },
        {
            name: "notes",
            description: "Review your study notes",
            path: `/study/${documentId}/notes`,
        },
        {
            name: "roadmap",
            description: "Follow your learning path",
            path: `/study/${documentId}/roadmap`,
        },
    ];

    return (
        <main className="study-page">

            <button
                className="back-link"
                onClick={() => navigate("/")}
            >
                ← study sets
            </button>

            {/* Loading */}

            {loading && (
                <p className="study-status">
                    loading study set...
                </p>
            )}

            {/* Error */}

            {error && (
                <p className="study-error">
                    {error}
                </p>
            )}

            {/* Study Set */}

            {document && (
                <>
                    <header className="study-header">

                        <h1>
                            {document.filename}
                        </h1>

                        <p>
                            {document.file_type?.toUpperCase()} ·{" "}
                            {document.total_chunks || 0} chunks ·{" "}
                            {document.status}
                        </p>

                    </header>

                    {/* Navigation */}

                    <nav className="study-tabs">

                        {modes.map((mode) => (
                            <button
                                key={mode.name}
                                className="study-tab"
                                onClick={() =>
                                    navigate(mode.path)
                                }
                            >
                                {mode.name}
                            </button>
                        ))}

                    </nav>

                    {/* Continue */}

                    <section className="continue-section">

                        <p className="section-label">
                            continue studying
                        </p>

                        <div className="continue-topic">

                            <div>

                                <h2>
                                    Continue with your material
                                </h2>

                                <p className="continue-description">
                                    Ask questions about your uploaded
                                    study material with the AI tutor.
                                </p>

                            </div>

                        </div>

                        <button
                            className="continue-button"
                            onClick={() =>
                                navigate(
                                    `/study/${documentId}/tutor`
                                )
                            }
                        >
                            continue
                        </button>

                    </section>

                    {/* Study Modes */}

                    <section className="modes-section">

                        <p className="section-label">
                            study modes
                        </p>

                        <div className="mode-grid">

                            {modes.map((mode) => (

                                <button
                                    key={mode.name}
                                    className="mode-card"
                                    onClick={() =>
                                        navigate(mode.path)
                                    }
                                >

                                    <span className="mode-name">
                                        {mode.name}
                                    </span>

                                    <span className="mode-description">
                                        {mode.description}
                                    </span>

                                </button>

                            ))}

                        </div>

                    </section>
                </>
            )}

        </main>
    );
}

export default StudyPage;