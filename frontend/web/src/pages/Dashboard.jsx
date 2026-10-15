import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDocuments } from "../services/api";

function Dashboard() {
    const navigate = useNavigate();

    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadDocuments() {
            try {
                const data = await getDocuments();
                setDocuments(data);
            } catch (error) {
                console.error(error);
                setError(error.message);
            } finally {
                setLoading(false);
            }
        }

        loadDocuments();
    }, []);

    return (
        <main className="main-content">

            <header className="page-header">
                <p className="page-eyebrow">
                    study companion
                </p>

                <h1 className="page-title">
                    Your study sets
                </h1>

                <p className="page-description">
                    Everything you're learning, in one place.
                    Pick up where you left off or create a new
                    study set.
                </p>
            </header>

            <section>

                <div className="section-header">
                    <h2 className="section-title">
                        study sets
                    </h2>
                </div>

                {loading && (
                    <p className="dashboard-status">
                        loading study sets...
                    </p>
                )}

                {error && (
                    <p className="dashboard-error">
                        {error}
                    </p>
                )}

                {!loading &&
                    !error &&
                    documents.length === 0 && (
                        <div className="empty-dashboard">

                            <p>
                                No study material uploaded yet.
                            </p>

                            <button
                                className="new-study-set"
                                onClick={() =>
                                    navigate("/upload")
                                }
                            >
                                <span className="new-study-set-symbol">
                                    +
                                </span>
                                new study set
                            </button>

                        </div>
                    )}

                <div className="study-set-list">

                    {documents.map((document) => (

                        <article
                            key={document.id}
                            className="study-set"
                            onClick={() =>
                                navigate(
                                    `/study/${document.id}`
                                )
                            }
                        >

                            <div className="study-set-main">

                                <h3 className="study-set-title">
                                    {document.filename}
                                </h3>

                                <p className="study-set-description">
                                    {document.status === "completed"
                                        ? "Ready to study."
                                        : `Status: ${document.status}`}
                                </p>

                                <div className="study-set-meta">

                                    <span>
                                        {document.file_type?.toUpperCase()}
                                    </span>

                                    <span>
                                        {document.total_chunks || 0} chunks
                                    </span>

                                    <span>
                                        {document.status}
                                    </span>

                                </div>

                            </div>

                            <div className="study-set-progress">

                                <div className="progress-value">
                                    {document.status === "completed"
                                        ? "ready"
                                        : "processing"}
                                </div>

                                <div className="progress-track">

                                    <div
                                        className="progress-fill"
                                        style={{
                                            width:
                                                document.status ===
                                                "completed"
                                                    ? "100%"
                                                    : `${
                                                          document.total_chunks
                                                              ? (document.processed_chunks /
                                                                    document.total_chunks) *
                                                                100
                                                              : 0
                                                      }%`,
                                        }}
                                    />

                                </div>

                            </div>

                        </article>

                    ))}

                </div>

                {!loading && (
                    <button
                        className="new-study-set"
                        onClick={() => navigate("/upload")}
                    >
                        <span className="new-study-set-symbol">
                            +
                        </span>
                        new study set
                    </button>
                )}

            </section>

        </main>
    );
}

export default Dashboard;