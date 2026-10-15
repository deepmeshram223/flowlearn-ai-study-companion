import { useState } from "react";
import { useParams } from "react-router-dom";
import { generateRoadmap } from "../services/api";
import "./RoadmapPage.css";

function RoadmapPage() {
    const { documentId } = useParams();

    const [roadmap, setRoadmap] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleGenerate() {
        setLoading(true);
        setError("");

        try {
            const result = await generateRoadmap(documentId);

            setRoadmap(result);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <main className="roadmap-page">

            <div className="roadmap-header">

                <p className="eyebrow">
                    flowlearn
                </p>

                <h1>
                    Learning Roadmap
                </h1>

                <p className="roadmap-description">
                    Build a structured learning path from your
                    study material.
                </p>

                <button
                    className="generate-roadmap-button"
                    onClick={handleGenerate}
                    disabled={loading}
                >
                    {loading
                        ? "generating..."
                        : "generate roadmap"}
                </button>

                {error && (
                    <p className="roadmap-error">
                        {error}
                    </p>
                )}

            </div>

            {roadmap && (
                <section className="roadmap-result">

                    <h2>
                        {roadmap.title}
                    </h2>

                    <p>
                        {roadmap.description}
                    </p>

                    {roadmap.phases.map((phase) => (
                        <div
                            className="roadmap-phase"
                            key={phase.id}
                        >

                            <h3>
                                {phase.title}
                            </h3>

                            <div className="roadmap-nodes">

                                {phase.nodes.map((node) => (
                                    <div
                                        className="roadmap-node"
                                        key={node.id}
                                    >

                                        <span className="node-id">
                                            {node.id}
                                        </span>

                                        <div>
                                            <h4>
                                                {node.title}
                                            </h4>

                                            <p>
                                                {node.description}
                                            </p>

                                            <span className="node-meta">
                                                {node.difficulty}
                                                {" · "}
                                                {node.estimated_minutes}
                                                {" min"}
                                            </span>
                                        </div>

                                    </div>
                                ))}

                            </div>

                        </div>
                    ))}

                </section>
            )}

        </main>
    );
}

export default RoadmapPage;