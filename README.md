# FlowLearn

AI-powered study companion that transforms learning materials into an interactive learning experience using RAG, semantic search, LLMs, and AI-generated learning paths.

## Overview

FlowLearn allows students to upload learning materials such as PDFs, presentations, documents, and text files.

The system processes the material, extracts and chunks the content, generates semantic embeddings, stores them using PostgreSQL and pgvector, and uses Retrieval-Augmented Generation to answer questions based on the uploaded material.

It also generates hierarchical learning roadmaps to organize large documents into topics, subtopics, and learning nodes.

## Features

- Document upload and processing
- PDF, DOCX, PPTX, and TXT support
- OCR for scanned PDF pages
- Automatic document chunking
- Semantic embeddings
- PostgreSQL + pgvector vector storage
- Hybrid semantic and keyword retrieval
- Retrieval-Augmented Generation (RAG)
- AI-powered tutoring
- AI-generated flashcards
- AI-generated quizzes
- Hierarchical learning roadmaps
- React-based web interface
- Background document processing
- Processing progress tracking

## Architecture

```text
                    User
                     |
                     v
              React Frontend
                     |
                  REST API
                     |
                     v
                FastAPI
                     |
        +------------+------------+
        |            |            |
        v            v            v
   Document       RAG         AI Generation
   Pipeline      Pipeline        Pipeline
        |            |            |
        v            v            v
   Extraction    Retrieval      Groq LLM
        |            |
        v            v
      OCR       pgvector
        |            |
        v            |
     Chunking <------+
        |
        v
   Embeddings
        |
        v
   PostgreSQL

Document Processing
Document Upload
       |
       v
File Validation
       |
       v
Text Extraction
       |
       +----> OCR for scanned pages
       |
       v
Text Cleaning
       |
       v
Chunking
       |
       v
Embedding Generation
       |
       v
PostgreSQL + pgvector

Large documents are processed in the background so document processing does not block the main API request.
The system tracks processing status, processing stage, page progress, and chunk progress.
RAG Pipeline
FlowLearn uses Retrieval-Augmented Generation instead of sending an entire document to the LLM.
User Question
      |
      v
Question Embedding
      |
      +------------------+
      |                  |
      v                  v
Semantic Search     Keyword Search
      |                  |
      +--------+---------+
               |
               v
        Relevant Chunks
               |
               v
        Context Building
               |
               v
             LLM
               |
               v
        Grounded Answer

Semantic retrieval finds conceptually similar content, while keyword retrieval helps preserve exact technical terminology.
The retrieved content is then provided to the LLM as context.
Hierarchical Roadmap
FlowLearn does not simply copy a document's table of contents.
The roadmap is generated from concepts discovered from the document content.
Document
    |
    v
Document Chunks
    |
    v
Embeddings
    |
    v
Concept Discovery
    |
    v
Topic Groups
    |
    v
Hierarchical Organization
    |
    +---- Parent Topics
             |
             +---- Subtopics
                     |
                     +---- Learning Nodes

This structure allows large documents to be represented as a manageable learning path instead of displaying hundreds or thousands of concepts at once.
Learning nodes can contain source pages, prerequisites, and mastery information.
Technology Stack
Backend
- Python
- FastAPI
- PostgreSQL
- pgvector
- SQLAlchemy
- Sentence Transformers
- PyMuPDF
- Tesseract OCR
Generative AI
- Groq API
- Large Language Models
- Retrieval-Augmented Generation
- Semantic embeddings
- Hybrid retrieval
- AI-generated learning content
Frontend
- React
- Vite
- React Router
- JavaScript
- CSS
Project Structure
ai-study-companion/
|
+-- backend/
|   +-- api/
|   +-- database/
|   +-- models/
|   +-- services/
|   +-- main.py
|
+-- frontend/
|   +-- web/
|       +-- src/
|           +-- components/
|           +-- pages/
|           +-- services/
|
+-- data/
+-- tests/
+-- requirements.txt
+-- .env.example
+-- README.md

Running Locally
1. Clone the repository
git clone https://github.com/deepmeshram223/flowlearn-ai-study-companion.git
cd flowlearn-ai-study-companion

2. Create a virtual environment
python -m venv venv

Windows:
venv\Scripts\activate

3. Install backend dependencies
pip install -r requirements.txt

4. Install frontend dependencies
cd frontend/web
npm install
cd ../..

5. Configure environment variables
Create a .env file based on .env.example.
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
GROQ_ROADMAP_MODEL=openai/gpt-oss-120b

DATABASE_URL=postgresql://username:password@localhost:5432/ai_study_companion

Never commit your .env file or API keys.
6. Start the backend
uvicorn backend.main:app --reload

Backend:
http://127.0.0.1:8000

API documentation:
http://127.0.0.1:8000/docs

7. Start the frontend
Open another terminal:
cd frontend/web
npm run dev

Frontend:
http://localhost:5173

API
Important endpoints include:
POST /api/documents/upload
GET  /api/documents
GET  /api/documents/{document_id}/status
POST /api/study/ask
POST /api/roadmap/generate

Key Engineering Decisions
Why RAG?
Large documents cannot efficiently be sent to an LLM as one large prompt.
RAG retrieves only the relevant portions of the document and provides those sections as context to the model.
Why Hybrid Retrieval?
Semantic search captures conceptual similarity.
Keyword retrieval helps with exact technical terminology.
Combining both approaches improves retrieval for technical study material.
Why PostgreSQL + pgvector?
The application already requires PostgreSQL for relational data.
pgvector allows embeddings to be stored and queried inside the same database instead of introducing a separate vector database.
Why a Hierarchical Roadmap?
A large document may contain hundreds or thousands of concepts.
Displaying everything simultaneously would create an unusable learning interface.
FlowLearn organizes the concepts hierarchically:
Parent Topic
     |
     v
Subtopic
     |
     v
Learning Node

This allows the roadmap to remain readable while supporting deeper exploration.
Current Status
FlowLearn currently includes:
- Document ingestion
- PDF/DOCX/PPTX/TXT processing
- OCR fallback
- Document chunking
- Embedding generation
- PostgreSQL vector storage
- Hybrid retrieval
- RAG-based tutoring
- AI-generated hierarchical roadmaps
- React web interface
Future Improvements
- User authentication
- Persistent learning progress
- Adaptive study scheduling
- Spaced repetition
- Personalized difficulty
- Improved concept graphs
- Prerequisite-aware learning paths
- RAG evaluation and retrieval benchmarking
Author
Deep Meshram
GitHub: deepmeshram223
LinkedIn: Deep Meshram

Then scroll to the bottom.

Under **Commit changes**, use:

```text
Commit message:
Improve FlowLearn project documentation
