# CSV Analysis Assistant

Upload a CSV file and ask questions about your data in plain English. The app uses an LLM (Groq's Llama) to generate and execute pandas code on the fly, returning results, summaries, and charts.

## How it works

1. Upload a CSV file
2. Type a question (e.g. *"How many items does each category have?"*)
3. The backend inspects the data, asks an LLM to write pandas/matplotlib code, executes it safely, and returns the result
4. View the answer, chart, and generated code in the UI

## Project structure

```
backend/
├── main.py            # FastAPI server
├── llm_client.py      # Groq API interaction
├── pandas_runner.py   # Sandboxed pandas code execution
└── requirements.txt

frontend/
├── app.py             # Streamlit UI
└── requirements.txt
```

## Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com/)

## Setup

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GROQ_API_KEY=gsk_...
```

## Usage

Start the backend (terminal 1):

```bash
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend (terminal 2):

```bash
cd frontend && streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
```

Open `http://localhost:8501` in your browser.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Groq API key (required) |
| `BACKEND_SERVER_URL` | `http://localhost:8000` | Backend URL |

## Tech stack

**Backend:** FastAPI, pandas, matplotlib, Groq API  
**Frontend:** Streamlit, pandas, Pillow  
**Model:** `llama-3.3-70b-versatile` (via Groq)

## Development

A `.devcontainer/devcontainer.json` is included for VS Code Dev Containers / GitHub Codespaces.
