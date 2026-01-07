"""
FINANCIAL CHATBOT MODULE
Provides chatbot functionality for Flask application
"""

from huggingface_hub import InferenceClient

# Your HuggingFace API token
API_TOKEN = "YOUR_API_TOKEN"

# Finance-only system instruction
SYSTEM_PROMPT = """You are a financial advisor chatbot. You ONLY answer questions related to:
- Personal finance (budgeting, saving, investing)
- Banking and loans
- Stock market and trading
- Cryptocurrency
- Insurance
- Taxes
- Financial planning
- Credit cards and debt

If someone asks a non-finance question, politely tell them: "I'm a finance-focused assistant. I can only help with financial topics like budgeting, investing, loans, taxes, etc. Do you have any finance-related questions?"

Be helpful, accurate, and professional. Keep responses concise and clear."""


class FinanceChatbot:
    def __init__(self):
        self.client = InferenceClient(token=API_TOKEN)
        self.conversation_history = {}

    def get_response(self, user_message, session_id="default"):
        """Send message to chatbot and get response"""
        try:
            # Initialize conversation history for this session if not exists
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
                self.conversation_history[session_id].append({
                    "role": "system",
                    "content": SYSTEM_PROMPT
                })

            # Add user message
            self.conversation_history[session_id].append({
                "role": "user",
                "content": user_message
            })

            # Get response from model
            response = self.client.chat_completion(
                model="meta-llama/Llama-3.2-3B-Instruct",
                messages=self.conversation_history[session_id],
                max_tokens=500,
                temperature=0.7
            )

            bot_message = response.choices[0].message.content

            # Add bot response to history
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": bot_message
            })

            return {"success": True, "message": bot_message}

        except Exception as e:
            return {"success": False, "message": f"Sorry, I encountered an error: {str(e)}"}

    def clear_history(self, session_id="default"):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]


# Create global instance
chatbot = FinanceChatbot()