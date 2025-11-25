# Deployment Walkthrough

I have prepared your application for deployment on Streamlit Cloud (or similar platforms) while maintaining the separation between frontend and backend code.

## Changes Made

1.  **Entry Point (`app.py`)**: Created a new `app.py` file in the root directory. This script acts as the main entry point. It:
    *   Starts the FastAPI backend server in a background process.
    *   Waits for the backend to be ready.
    *   Runs the Streamlit frontend application.
    *   This allows you to deploy a single "app" that contains both services without merging their codebases.

2.  **Dependencies (`requirements.txt`)**: Created a `requirements.txt` file listing all necessary libraries for both backend and frontend.

3.  **Package Structure**: Added `__init__.py` files to `backend` and `frontend` directories to ensure they can be correctly referenced.

4.  **Configuration Fix**: Updated `backend/llm_service.py` to correctly load the `.env` file when running from the root directory.

## How to Run Locally

Run the following command from the root directory:

```bash
streamlit run app.py
```

This will start both the backend API (on port 8000) and the Streamlit UI.

## How to Deploy to Streamlit Cloud

1.  Push your code to GitHub.
2.  Log in to [Streamlit Cloud](https://streamlit.io/cloud).
3.  Create a new app and select your repository.
4.  **Main file path**: Set this to `app.py`.
5.  **Advanced Settings**:
    *   Add your secrets (e.g., `GEMINI_API_KEY`) in the Streamlit Cloud secrets management.
    *   **Crucial**: The `app.py` script is configured to automatically read `GEMINI_API_KEY` from Streamlit secrets and pass it to the backend process. You do **not** need to manually set environment variables if you use Streamlit secrets.

## Architecture

*   **Frontend**: `frontend/streamlit_app.py` (Streamlit)
*   **Backend**: `backend/main.py` (FastAPI)
*   **Orchestrator**: `app.py` (Python script that runs both)

The frontend communicates with the backend via HTTP requests to `http://localhost:8000/api`.
