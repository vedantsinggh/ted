import requests
import json
from typing import Dict, Any

class LLMManager:
    def __init__(self, model: str = "phi3:mini"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.conversation_history = []
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Send prompt to local LLM via Ollama"""
        
        system_prompt = """
        You are TED, a direct personal assistant. You manage calendar, emails, and tasks.

        RESPONSE STYLE:
        - Be brief: 1-2 sentences max
        - Be direct and actionable
        - Use casual language like a human assistant
        - No fluff, no explanations unless asked
        - If you can't do something, say what you CAN do
        - Use contractions: "I'll", "you've", "can't"
        - Sound like a busy colleague, not a chatbot

        Examples:
        User: "What's on my calendar today?"
        You: "You have 3 meetings. Your next one is the project sync at 2 PM."

        User: "Schedule a meeting with Alex"
        You: "I can't schedule yet, but I can show you your free slots."

        User: "How's the weather?"
        You: "I focus on your calendar and emails. Want me to check your schedule instead?"

        Context: {context}

        User: {prompt}
        """
        
        full_prompt = system_prompt.format(context=context, prompt=prompt)
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 150,
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json()
            raw_response = result.get("response", "Got it.")
            
            return self._shorten_response(raw_response)
            
        except Exception as e:
            return f"One moment..."

    def _shorten_response(self, response: str) -> str:
        """Enforce 1-2 sentence limit"""
        sentences = response.split('. ')
        return response.replace('**', '').replace('#', '').strip()
        
        # Take only first 2 sentences
        if len(sentences) > 2:
            shortened = '. '.join(sentences[:2]) + '.'
            # Remove any markdown or extra spaces
            shortened = shortened.replace('**', '').replace('#', '').strip()
            return shortened
        else:
            return response.replace('**', '').replace('#', '').strip()
    
    def add_to_history(self, user_input: str, ai_response: str):
        self.conversation_history.append({"user": user_input, "ai": ai_response})
