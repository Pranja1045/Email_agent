import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    .email-card {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid #334155;
    }
    .category-badge {
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hello! I am your Email Agent. Ask me to summarize emails or find tasks."}]

# API Helpers
def get_emails():
    try:
        res = requests.get(f"{API_BASE_URL}/emails")
        return res.json()
    except:
        st.error("Failed to connect to backend.")
        return []

def ingest_emails():
    try:
        requests.post(f"{API_BASE_URL}/emails/ingest")
        st.rerun()
    except:
        st.error("Failed to ingest emails.")

def get_prompts():
    try:
        res = requests.get(f"{API_BASE_URL}/prompts")
        return res.json()
    except:
        return {}

def update_prompts(prompts):
    try:
        requests.post(f"{API_BASE_URL}/prompts", json=prompts)
        st.success("Prompts updated!")
    except:
        st.error("Failed to update prompts.")

def chat_with_agent(message, email_id=None):
    try:
        payload = {"message": message, "email_id": email_id}
        res = requests.post(f"{API_BASE_URL}/agent/chat", json=payload)
        return res.json().get("response", "Error")
    except:
        return "Error communicating with agent."

def generate_draft(message, email_id):
    try:
        payload = {"message": message, "email_id": email_id}
        res = requests.post(f"{API_BASE_URL}/drafts/generate", json=payload,api_key=GEMINI_API_KEY)
        return res.json().get("draft", "")
    except:
        return "Error generating draft."

# Sidebar - Navigation & Brain
with st.sidebar:
    st.title("📧 Email Agent")
    
    page = st.radio("Navigation", ["Inbox", "Agent Brain"])
    
    st.divider()
    
    if page == "Inbox":
        st.subheader("Agent Chat")
        
        # Chat Interface
        chat_container = st.container(height=400)
        for msg in st.session_state.chat_history:
            with chat_container.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if prompt := st.chat_input("Ask the agent..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with chat_container.chat_message("user"):
                st.write(prompt)
            
            # Get context from selected email if any
            email_id = st.session_state.selected_email['id'] if st.session_state.selected_email else None
            response = chat_with_agent(prompt, email_id)
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            with chat_container.chat_message("assistant"):
                st.write(response)

# Main Content
if page == "Inbox":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Inbox")
        if st.button("Refresh & Process"):
            with st.spinner("Processing inbox..."):
                ingest_emails()
        
        emails = get_emails()
        
        # Filter/Search could go here
        
        for email in emails:
            # Determine badge color
            cat_color = "#64748b"
            if email['category'] == 'Important': cat_color = "#ef4444"
            elif email['category'] == 'Newsletter': cat_color = "#3b82f6"
            elif email['category'] == 'Spam': cat_color = "#94a3b8"
            elif email['category'] == 'To-Do': cat_color = "#eab308"
            
            # Card
            with st.container():
                st.markdown(f"""
                <div class="email-card" style="border-left: 4px solid {cat_color}; cursor: pointer;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: bold;">{email['sender']}</span>
                        <span style="font-size: 0.8em; color: #94a3b8;">{datetime.fromisoformat(email['timestamp']).strftime('%b %d')}</span>
                    </div>
                    <div style="font-weight: 600; margin: 2px 0;">{email['subject']}</div>
                    <div style="font-size: 0.8em; color: #cbd5e1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{email['body'][:50]}...</div>
                    <div style="margin-top: 5px;">
                        <span class="category-badge" style="background-color: {cat_color}33; color: {cat_color}; border: 1px solid {cat_color}88;">{email['category'] or 'Uncategorized'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View", key=f"btn_{email['id']}", use_container_width=True):
                    st.session_state.selected_email = email
                    if 'current_draft' in st.session_state:
                        del st.session_state.current_draft
                    st.session_state.draft_instructions = ""

    with col2:
        if st.session_state.selected_email:
            email = st.session_state.selected_email
            st.subheader(email['subject'])
            st.markdown(f"**From:** {email['sender']} | **Date:** {email['timestamp']}")
            st.divider()
            st.write(email['body'])
            
            st.divider()
            
            # Action Items
            if email.get('action_items'):
                st.markdown("### ✅ Action Items")
                for item in email['action_items']:
                    st.info(f"**{item['task']}** (Due: {item.get('deadline', 'N/A')})")
            
            # Drafting
            st.markdown("### ✍️ Draft Reply")
            draft_instructions = st.text_input("Instructions for reply (optional)", placeholder="e.g., Be polite but firm", key="draft_instructions")
            
            if st.button("Generate Draft"):
                with st.spinner("Generating draft..."):
                    draft = generate_draft(draft_instructions, email['id'])
                    st.session_state.current_draft = draft
            
            if 'current_draft' in st.session_state:
                draft_text = st.text_area("Edit Draft", value=st.session_state.current_draft, height=200)
                if st.button("Save Draft"):
                    try:
                        requests.post(f"{API_BASE_URL}/emails/{email['id']}/draft", json={"body": draft_text, "subject": "", "to": ""})
                        st.success("Draft saved!")
                        # Update local state to reflect saved status if needed, or just rely on reload
                    except:
                        st.error("Failed to save draft.")
                    del st.session_state.current_draft
            elif email.get('draft'):
                 st.info("Saved Draft:")
                 st.text_area("Saved Draft", value=email['draft'], height=200, disabled=True)
        else:
            st.info("Select an email to view details.")

elif page == "Agent Brain":
    st.header("🧠 Agent Brain Configuration")
    st.write("Configure the prompts that guide the agent's behavior.")
    
    current_prompts = get_prompts()
    
    with st.form("prompts_form"):
        cat_prompt = st.text_area("Categorization Prompt", value=current_prompts.get("categorization_prompt", ""), height=150)
        action_prompt = st.text_area("Action Item Extraction Prompt", value=current_prompts.get("action_extraction_prompt", ""), height=150)
        reply_prompt = st.text_area("Auto-Reply Draft Prompt", value=current_prompts.get("auto_reply_prompt", ""), height=150)
        
        if st.form_submit_button("Save Configuration"):
            new_prompts = {
                "categorization_prompt": cat_prompt,
                "action_extraction_prompt": action_prompt,
                "auto_reply_prompt": reply_prompt
            }
            update_prompts(new_prompts)
