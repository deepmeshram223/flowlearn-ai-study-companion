const API_BASE_URL = "http://127.0.0.1:8000";


// ========================================
// Upload document
// ========================================

export async function uploadDocument(file) {
    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
        `${API_BASE_URL}/api/documents/upload`,
        {
            method: "POST",
            body: formData
        }
    );

    if (!response.ok) {
        const error = await response.json();

        throw new Error(
            error.detail || "Upload failed"
        );
    }

    return response.json();
}


// ========================================
// Get document processing status
// ========================================

export async function getDocumentStatus(
    documentId
) {
    const response = await fetch(
        `${API_BASE_URL}/api/documents/${documentId}/status`
    );

    if (!response.ok) {
        const error = await response.json();

        throw new Error(
            error.detail || "Could not get document status"
        );
    }

    return response.json();
}

export async function askQuestion(
    question,
    documentId,
    limit = 5
) {

    const response = await fetch(
        `${API_BASE_URL}/api/study/ask`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question,
                document_id: Number(documentId),
                limit
            })
        }
    );

    if (!response.ok) {

        const error = await response.json();

        throw new Error(
            error.detail ||
            "Failed to get an answer."
        );
    }

    return response.json();
}
export async function getDocuments() {
    const response = await fetch(
        `${API_BASE_URL}/api/documents`
    );

    if (!response.ok) {
        const error = await response.json();

        throw new Error(
            error.detail || "Could not load documents."
        );
    }

    return response.json();
}
export async function generateRoadmap(documentId) {
    const response = await fetch(
        `${API_BASE_URL}/api/roadmap/generate`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                document_id: Number(documentId)
            })
        }
    );

    if (!response.ok) {
        const error = await response.json();

        throw new Error(
            error.detail || "Failed to generate roadmap."
        );
    }

    return response.json();
}