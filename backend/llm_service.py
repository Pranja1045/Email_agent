import os
import json
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure your API key here or via environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class LLMService:
    def __init__(self):
        self.mock_mode = True
        if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_API_KEY_HERE":
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
                self.mock_mode = False
                print("Gemini API configured successfully.")
            except Exception as e:
                print(f"Failed to configure Gemini API: {e}. Falling back to mock mode.")
        else:
            print("No valid Gemini API key found. Using mock mode.")

    def _call_gemini(self, prompt: str) -> str:
        import time
        retries = 5
        for i in range(retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                if "429" in str(e):
                    time.sleep(2 ** (i + 1))  # Exponential backoff: 2s, 4s, 8s
                    continue
                print(f"Gemini API call failed: {e}")
                return "Error calling Gemini API."
        return "Error calling Gemini API (Rate Limit Exceeded)."

    def categorize_email(self, sender: str, subject: str, body: str, prompt: str) -> str:
        if self.mock_mode:
            # Mock fallback
            body_lower = body.lower()
            if "urgent" in body_lower or "deadline" in body_lower: return "Important"
            if "newsletter" in body_lower: return "Newsletter"
            if "prize" in body_lower: return "Spam"
            if "meeting" in body_lower: return "Work"
            return "General"
        
        full_prompt = f"{prompt}\n\nSender: {sender}\nSubject: {subject}\nBody:\n{body}\n\nRespond ONLY with the category name from the list."
        return self._call_gemini(full_prompt).strip()

    def extract_action_items(self, email_body: str, prompt: str) -> List[Dict[str, Any]]:
        if self.mock_mode:
            # Mock fallback
            if "report" in email_body.lower():
                return [{"task": "Submit Q4 Report", "deadline": "Tomorrow EOD"}]
            return []

        full_prompt = f"{prompt}\n\nEmail Body:\n{email_body}\n\nRespond ONLY with valid JSON."
        response_text = self._call_gemini(full_prompt)
        try:
            # Clean up markdown code blocks if present
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except:
            return []

    def generate_reply(self, email_body: str, prompt: str, instructions: str = "") -> str:
        if self.mock_mode:
            return "Mock reply: Received your email."
            
        full_prompt = f"{prompt}\n\nUser Instructions: {instructions}\n\nEmail Context:\n{email_body}\n\nDraft:"
        return self._call_gemini(full_prompt)

    def chat_with_agent(self, message: str, context: str, prompt: str) -> str:
        if self.mock_mode:
            return f"Mock response to: {message}"
            
        full_prompt = f"System: You are a helpful email assistant.\nContext:\n{context}\n\nUser: {message}"
        return self._call_gemini(full_prompt)

llm_service = LLMService()