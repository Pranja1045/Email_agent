from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models import Email, PromptConfig, Draft, ChatRequest, ChatMessage
from .database import load_emails, save_email_state, save_all_email_states, load_prompts, save_prompts
from .llm_service import llm_service

app = FastAPI(title="Email Productivity Agent")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/emails", response_model=List[Email])
def get_emails():
    return load_emails()

@app.post("/api/emails/ingest")
def ingest_emails():
    """
    Triggers the processing of all emails using the current prompts.
    Only processes emails that are read and not yet categorized.
    """
    emails = load_emails()
    prompts = load_prompts()
    
    import time
    processed_count = 0
    for email in emails:
        if not email.category:
            # Categorize
            email.category = llm_service.categorize_email(email.sender, email.subject, email.body, prompts.categorization_prompt)
            
            # Extract Actions only for Important or To-Do
            if email.category in ["Important", "To-Do"]:
                email.action_items = llm_service.extract_action_items(email.body, prompts.action_extraction_prompt)
            else:
                email.action_items = []
            
            processed_count += 1
            processed_count += 1
            time.sleep(2.5)  # Rate limit throttling (approx 24 req/min)
        
        # Cleanup: Ensure no action items for other categories (even if already processed)
        elif email.category not in ["Important", "To-Do"] and email.action_items:
            email.action_items = []
    
    # Save new state (overwriting old one)
    save_all_email_states(emails)
    return {"message": f"Processed {processed_count} emails", "emails": emails}

@app.get("/api/prompts", response_model=PromptConfig)
def get_prompts():
    return load_prompts()

@app.post("/api/prompts")
def update_prompts(config: PromptConfig):
    save_prompts(config)
    return {"message": "Prompts updated"}

@app.post("/api/agent/chat")
def agent_chat(request: ChatRequest):
    prompts = load_prompts()
    context = ""
    if request.email_id:
        emails = load_emails()
        email = next((e for e in emails if e.id == request.email_id), None)
        if email:
            context = f"Subject: {email.subject}\nBody: {email.body}"
    
    response = llm_service.chat_with_agent(request.message, context, prompts.auto_reply_prompt)
    return {"response": response}

@app.post("/api/drafts/generate")
def generate_draft(request: ChatRequest):
    prompts = load_prompts()
    context = ""
    if request.email_id:
        emails = load_emails()
        email = next((e for e in emails if e.id == request.email_id), None)
        if email:
            context = email.body
            
    draft_body = llm_service.generate_reply(context, prompts.auto_reply_prompt, request.message)
    return {"draft": draft_body}

@app.post("/api/emails/{email_id}/draft")
def save_draft(email_id: str, draft: Draft):
    emails = load_emails()
    email = next((e for e in emails if e.id == email_id), None)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email.draft = draft.body
    save_email_state(email)
    return {"message": "Draft saved"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)