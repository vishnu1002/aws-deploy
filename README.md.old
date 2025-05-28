# Enterprise Search Platform

A powerful enterprise search platform that enables semantic search across various document types including resumes, policy documents, and reports. The platform uses advanced language models to provide accurate and context-aware search results.

## Architecture

```mermaid
graph TB
    subgraph Frontend
        UI[React Frontend]
        Search[Search Interface]
        Results[Results Display]
        UI --> Search
        Search --> Results
    end

    subgraph Backend
        API[FastAPI Server]
        Models[LLM Models]
        Models --> |Qwen| Qwen[Qwen Model]
        Models --> |DeepSeek| DeepSeek[DeepSeek Model]
        Models --> |Llama| Llama[Llama Model]
        API --> Models
    end

    subgraph Data
        Docs[Document Storage]
        Docs --> |Resumes| Resumes[Resume Collection]
        Docs --> |Policies| Policies[Policy Documents]
        Docs --> |Reports| Reports[Reports Collection]
    end

    Frontend --> |HTTP Requests| Backend
    Backend --> |Query Processing| Data
    Data --> |Search Results| Backend
    Backend --> |Response| Frontend
```

## Features

- **Multi-Model Support**: Integration with multiple language models (Qwen, DeepSeek, Llama) for enhanced search capabilities
- **Document Type Support**:
  - Resume parsing and search
  - Policy document analysis
  - Report processing and indexing
- **Semantic Search**: Advanced semantic search capabilities using state-of-the-art language models
- **Modern UI**: React-based frontend with intuitive search interface
- **RESTful API**: FastAPI backend providing robust API endpoints

## Project Structure

```
enterprise_search/
├── backend/
│   ├── src/
│   ├── api.py
│   ├── server.py
│   ├── qwen.py
│   ├── deepseek.py
│   └── llama.py
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
└── data/
    ├── Resume/
    ├── policy_documents/
    └── reports/
```

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- Required Python packages (see backend/requirements.txt)
- Required Node.js packages (see frontend/package.json)

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python 
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## API Endpoints

The backend provides the following main endpoints:

- `POST /api/search`: Perform semantic search across documents
- `GET /api/models`: List available language models
- `POST /api/analyze`: Analyze document content
- `GET /api/health`: Health check endpoint

## Data Organization

The platform supports three main types of documents:

1. **Resumes**: Stored in `data/resume/`
   - Supports various resume formats
   - Extracts key information and skills

2. **Policy Documents**: Stored in `data/policy_documents/`
   - Company policies and procedures
   - Compliance documents
   - Guidelines and standards

3. **Reports**: Stored in `data/reports/`
   - Business reports
   - Analysis documents
   - Research papers

