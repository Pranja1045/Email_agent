# Prompt-Driven Email Productivity Agent

An intelligent email agent capable of processing an inbox, categorizing emails, extracting action items, and drafting replies using LLM-driven prompts.

## Features
- **Inbox Ingestion**: Loads emails from a mock source.
- **Prompt-Driven Architecture**: User-configurable prompts for categorization, extraction, and drafting.
- **Email Agent Chat**: Chat interface to query the inbox ("Summarize this", "Find tasks").
- **Auto-Drafting**: Generates reply drafts based on context and tone.
- **Modern UI**: Streamlit interface.

## Project Structure
- `backend/`: FastAPI application (Python)
- `frontend/`:streamlit application (Python)
- `data/`: JSON storage for mock inbox and prompts

## Setup Instructions

### Prerequisites
- Python 3.8+

### 1. Backend Setup
1. Navigate to the `backend` directory (or root).
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```
3. Run the server:
   ```bash
   # From the root directory
   python -m backend.main
   ```
   The API will be available at `http://localhost:8000`.

### 2. Frontend Setup (Streamlit)
1. Install Streamlit:
   ```bash
   pip install streamlit
   ```
2. Run the application:
   ```bash
   streamlit run streamlit_app.py
   ```
   The UI will be available at `http://localhost:8501`.

## Usage Guide

### Loading the Mock Inbox
1. Open the UI.
2. Click the **"Refresh & Process"** button in the Inbox panel.
3. This triggers the ingestion pipeline:
   - Loads emails from `data/mock_inbox.json`.
   - Runs the **Categorization Prompt** to tag emails (Important, Newsletter, etc.).
   - Runs the **Action Item Prompt** to extract tasks.

### Configuring Prompts ("The Brain")
1. Navigate to **"Agent Brain"** in the sidebar.
2. Edit the prompts for:
   - **Categorization**: Define rules for tagging.
   - **Action Extraction**: Define how tasks are identified.
   - **Auto-Reply**: Define the tone and logic for drafts.
3. Click **Save Configuration**. Future processing will use these new prompts.

### Using the Email Agent
1. Navigate to **"Inbox"**.
2. Use the **Agent Chat** in the sidebar.
3. Ask questions like:
   - "Summarize this email"
   - "What is the deadline?"
   - "Draft a polite refusal"

### Drafting Replies
1. Select an email from the list.
2. In the detail view, enter optional instructions.
3. Click **"Generate Draft"**.
4. The agent will generate a draft based on the `auto_reply_prompt`.

## Mock Data
- `data/mock_inbox.json`: Contains 40 sample emails.
- `data/default_prompts.json`: Contains the initial system prompts.

## Notes
- The system currently runs in **Mock LLM Mode** for demonstration. It uses keyword matching and pre-canned responses instead of a live OpenAI/Gemini API call to ensure it runs out-of-the-box without keys.
- To enable real LLM integration, update `backend/llm_service.py` to call your preferred API.
