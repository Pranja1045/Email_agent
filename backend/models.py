from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    timestamp: datetime
    read: bool = False
    category: Optional[str] = None
    action_items: List[Dict[str, Any]] = []
    summary: Optional[str] = None
    draft: Optional[str] = None

class PromptConfig(BaseModel):
    categorization_prompt: str
    action_extraction_prompt: str
    auto_reply_prompt: str

class Draft(BaseModel):
    email_id: Optional[str] = None
    subject: str
    body: str
    to: str

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    email_id: Optional[str] = None
