import { useNavigate, useLocation } from "react-router-dom";
import "./Sidebar.css";

function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();

    const isHome = location.pathname === "/";
    const isUpload = location.pathname === "/upload";

    return (
        <header className="topbar">

            <div
                className="brand"
                onClick={() => navigate("/")}
            >
                <span className="brand-flow">flow</span>
                <span className="brand-learn">learn</span>
            </div>

            <nav className="topnav">

                <button
                    className={`nav-link ${isHome ? "active" : ""}`}
                    onClick={() => navigate("/")}
                >
                    study sets
                </button>

                <button
                    className={`nav-link ${isUpload ? "active" : ""}`}
                    onClick={() => navigate("/upload")}
                >
                    + new set
                </button>

            </nav>

            <div className="topbar-right">

                <button className="nav-link">
                    progress
                </button>

                <button className="nav-link">
                    settings
                </button>

            </div>

        </header>
    );
}

export default Sidebar;