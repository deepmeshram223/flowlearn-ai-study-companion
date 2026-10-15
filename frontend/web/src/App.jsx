import { Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import UploadPage from "./pages/UploadPage";
import StudyPage from "./pages/StudyPage";
import TutorPage from "./pages/TutorPage";
import RoadmapPage from "./pages/RoadmapPage";
import "./App.css";

function Placeholder({ title }) {
    return (
        <main className="main-content">
            <p className="page-eyebrow">flowlearn</p>

            <h1 className="page-title">
                {title}
            </h1>

            <p className="page-description">
                This study mode is coming next.
            </p>
        </main>
    );
}

function App() {
    return (
        <div className="app">

            <Sidebar />

            <div className="app-shell">

                <Routes>

                    <Route
                        path="/"
                        element={<Dashboard />}
                    />

                    <Route
                        path="/upload"
                        element={<UploadPage />}
                    />

                    <Route
                        path="/study/:documentId"
                        element={<StudyPage />}
                    />

                    <Route
                        path="/study/:documentId/tutor"
                        element={
                            <TutorPage />
                        }
                    />

                    <Route
                        path="/study/:documentId/flashcards"
                        element={
                            <Placeholder title="Flashcards" />
                        }
                    />

                    <Route
                        path="/study/:documentId/quiz"
                        element={
                            <Placeholder title="Quiz" />
                        }
                    />

                    <Route
                        path="/study/:documentId/test"
                        element={
                            <Placeholder title="Written Test" />
                        }
                    />

                    <Route
                        path="/study/:documentId/notes"
                        element={
                            <Placeholder title="Notes" />
                        }
                    />

                    <Route
    path="/study/:documentId/roadmap"
    element={<RoadmapPage />}
/>

                </Routes>

            </div>

        </div>
    );
}

export default App;