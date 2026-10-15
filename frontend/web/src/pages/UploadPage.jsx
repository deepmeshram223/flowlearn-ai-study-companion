import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    uploadDocument,
    getDocumentStatus
} from "../services/api";

import "./UploadPage.css";


function UploadPage() {

    const navigate = useNavigate();

    const [selectedFile, setSelectedFile] = useState(null);

    const [uploading, setUploading] = useState(false);

    const [status, setStatus] = useState(null);

    const [error, setError] = useState("");

    const intervalRef = useRef(null);


    // --------------------------------------------------
    // Cleanup polling when page is removed
    // --------------------------------------------------

    useEffect(() => {

        return () => {

            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }

        };

    }, []);


    // --------------------------------------------------
    // File selection
    // --------------------------------------------------

    function handleFileChange(event) {

        const file = event.target.files?.[0];

        setError("");

        setStatus(null);

        if (!file) {
            setSelectedFile(null);
            return;
        }

        setSelectedFile(file);
    }


    // --------------------------------------------------
    // Start polling
    // --------------------------------------------------

    function startPolling(documentId) {

        intervalRef.current = setInterval(
            async () => {

                try {

                    const data =
                        await getDocumentStatus(
                            documentId
                        );

                    setStatus(data);


                    // ------------------------------
                    // Completed
                    // ------------------------------

                    if (
                        data.status ===
                        "completed"
                    ) {

                        clearInterval(
                            intervalRef.current
                        );

                        intervalRef.current =
                            null;

                        setUploading(false);

                        setTimeout(() => {

                            navigate(
                                `/study/${documentId}`
                            );

                        }, 1000);
                    }


                    // ------------------------------
                    // Failed
                    // ------------------------------

                    if (
                        data.status ===
                        "failed"
                    ) {

                        clearInterval(
                            intervalRef.current
                        );

                        intervalRef.current =
                            null;

                        setUploading(false);

                        setError(
                            data.error ||
                            "Document processing failed."
                        );
                    }

                } catch (pollError) {

                    console.error(
                        "Status polling error:",
                        pollError
                    );

                }

            },
            1000
        );
    }


    // --------------------------------------------------
    // Upload
    // --------------------------------------------------

    async function handleUpload() {

        if (!selectedFile) {

            setError(
                "Please select a file first."
            );

            return;
        }

        setUploading(true);

        setError("");

        setStatus(null);

        try {

            const result =
                await uploadDocument(
                    selectedFile
                );

            setStatus({
                document_id:
                    result.document_id,

                filename:
                    result.filename,

                status:
                    result.status,

                processing_stage:
                    "starting",

                current_page: 0,

                total_pages: 0,

                page_progress: 0,

                total_chunks: 0,

                processed_chunks: 0,

                progress: 0
            });


            startPolling(
                result.document_id
            );

        } catch (uploadError) {

            setUploading(false);

            setError(
                uploadError.message ||
                "Upload failed."
            );
        }
    }


    // --------------------------------------------------
    // Human-readable stage
    // --------------------------------------------------

    function getStageText() {

        if (!status) {
            return "Preparing...";
        }

        switch (
            status.processing_stage
        ) {

            case "starting":
                return "Starting...";

            case "extracting":
                return "Extracting text...";

            case "ocr":
                return "Reading scanned pages with OCR...";

            case "chunking":
                return "Creating study chunks...";

            case "embedding":
                return "Generating AI embeddings...";

            case "completed":
                return "Processing complete!";

            default:
                return "Processing document...";
        }
    }


    // --------------------------------------------------
    // Render
    // --------------------------------------------------

    return (

        <div className="upload-page">

            <div className="upload-container">

                <div className="upload-header">

                    <h1>
                        Upload Study Material
                    </h1>

                    <p>
                        Upload a PDF, DOCX, PPTX,
                        or TXT file to start studying.
                    </p>

                </div>


                {/* ---------------------------------- */}
                {/* File picker */}
                {/* ---------------------------------- */}

                <div className="upload-card">

                    <input
                        id="file-upload"
                        type="file"
                        accept=".pdf,.docx,.pptx,.txt"
                        onChange={
                            handleFileChange
                        }
                        disabled={uploading}
                    />

                    <label
                        htmlFor="file-upload"
                        className="file-picker"
                    >

                        <div className="upload-icon">
                            ↑
                        </div>

                        <strong>
                            {selectedFile
                                ? selectedFile.name
                                : "Choose a file"}
                        </strong>

                        <span>
                            PDF, DOCX, PPTX or TXT
                        </span>

                    </label>


                    {/* -------------------------------- */}
                    {/* Upload button */}
                    {/* -------------------------------- */}

                    <button
                        className="upload-button"
                        onClick={handleUpload}
                        disabled={
                            !selectedFile ||
                            uploading
                        }
                    >

                        {uploading
                            ? "Processing..."
                            : "Upload & Process"}

                    </button>


                    {/* -------------------------------- */}
                    {/* Processing status */}
                    {/* -------------------------------- */}

                    {status && (

                        <div className="processing-status">

                            <div className="status-header">

                                <strong>
                                    {getStageText()}
                                </strong>

                                <span>
                                    {status.status}
                                </span>

                            </div>


                            {/* OCR / extraction progress */}

                            {(
                                status.processing_stage ===
                                    "extracting" ||
                                status.processing_stage ===
                                    "ocr"
                            ) && (
                                <>

                                    <div className="progress-info">

                                        <span>
                                            Page{" "}
                                            {status.current_page}
                                            {" / "}
                                            {status.total_pages}
                                        </span>

                                        <span>
                                            {status.page_progress}%
                                        </span>

                                    </div>

                                    <div className="progress-bar">

                                        <div
                                            className="progress-fill"
                                            style={{
                                                width:
                                                    `${status.page_progress}%`
                                            }}
                                        />

                                    </div>

                                </>
                            )}


                            {/* Chunk / embedding progress */}

                            {(
                                status.processing_stage ===
                                    "chunking" ||
                                status.processing_stage ===
                                    "embedding"
                            ) && (

                                <>

                                    <div className="progress-info">

                                        <span>
                                            {status.processed_chunks}
                                            {" / "}
                                            {status.total_chunks}
                                            {" chunks"}
                                        </span>

                                        <span>
                                            {status.progress}%
                                        </span>

                                    </div>

                                    <div className="progress-bar">

                                        <div
                                            className="progress-fill"
                                            style={{
                                                width:
                                                    `${status.progress}%`
                                            }}
                                        />

                                    </div>

                                </>
                            )}


                            {/* Completed */}

                            {status.status ===
                                "completed" && (

                                <div className="success-message">

                                    ✓ Document processed
                                    successfully

                                </div>

                            )}

                        </div>

                    )}


                    {/* -------------------------------- */}
                    {/* Error */}
                    {/* -------------------------------- */}

                    {error && (

                        <div className="error-message">

                            {error}

                        </div>

                    )}

                </div>

            </div>

        </div>
    );
}


export default UploadPage;