import json
import os
from typing import List, Dict
from .models import Email, PromptConfig

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
MOCK_INBOX_PATH = os.path.join(DATA_DIR, "mock_inbox.json")
PROCESSED_STATE_PATH = os.path.join(DATA_DIR, "processed_emails.json")
PROMPTS_PATH = os.path.join(DATA_DIR, "default_prompts.json")

def load_prompts() -> PromptConfig:
    if not os.path.exists(PROMPTS_PATH):
        # Default fallback
        return PromptConfig(
            categorization_prompt="Categorize emails...",
            action_extraction_prompt="Extract tasks...",
            auto_reply_prompt="Draft a reply..."
        )
    with open(PROMPTS_PATH, "r") as f:
        data = json.load(f)
    return PromptConfig(**data)

def save_prompts(config: PromptConfig):
    with open(PROMPTS_PATH, "w") as f:
        json.dump(config.dict(), f, indent=2)

def load_emails() -> List[Email]:
    # Load raw emails
    if not os.path.exists(MOCK_INBOX_PATH):
        return []
    
    with open(MOCK_INBOX_PATH, "r") as f:
        raw_emails = json.load(f)
    
    # Load processed state (categories, etc.) if exists
    processed_data = {}
    if os.path.exists(PROCESSED_STATE_PATH):
        with open(PROCESSED_STATE_PATH, "r") as f:
            try:
                processed_data = json.load(f)
            except json.JSONDecodeError:
                processed_data = {}
            # processed_data is expected to be a dict keyed by email ID
            
    emails = []
    for e in raw_emails:
        email_obj = Email(**e)
        if email_obj.id in processed_data:
            # Merge processed data
            p_data = processed_data[email_obj.id]
            email_obj.category = p_data.get("category")
            email_obj.action_items = p_data.get("action_items", [])
            email_obj.summary = p_data.get("summary")
            email_obj.draft = p_data.get("draft")
        emails.append(email_obj)
        
    emails.sort(key=lambda x: int(x.id), reverse=True)
    return emails

def save_email_state(email: Email):
    processed_data = {}
    if os.path.exists(PROCESSED_STATE_PATH):
        with open(PROCESSED_STATE_PATH, "r") as f:
            try:
                processed_data = json.load(f)
            except json.JSONDecodeError:
                processed_data = {}
            
    processed_data[email.id] = {
        "category": email.category,
        "action_items": email.action_items,
        "summary": email.summary,
        "draft": email.draft
    }
    
    with open(PROCESSED_STATE_PATH, "w") as f:
        json.dump(processed_data, f, indent=2)

def save_all_email_states(emails: List[Email]):
    processed_data = {}
    for email in emails:
        processed_data[email.id] = {
            "category": email.category,
            "action_items": email.action_items,
            "summary": email.summary,
            "draft": email.draft
        }
    with open(PROCESSED_STATE_PATH, "w") as f:
        json.dump(processed_data, f, indent=2)
