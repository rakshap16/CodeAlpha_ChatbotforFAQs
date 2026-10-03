"""
Conversational Intent Handler
Detects and handles greetings, goodbyes, gratitude, help, and bot identity intents.
"""

import random
from typing import Optional, Dict, Any


INTENTS = {
    "greeting": {
        "patterns": [
            r"\b(hi|hello|hey|howdy|greetings|good\s*(morning|afternoon|evening)|what's\s*up|sup)\b"
        ],
        "responses": [
            "Hello! Welcome to NovaTech Support. How can I help you today?",
            "Hi there! I'm NovaBot, your 24/7 assistant. Feel free to ask any question about orders, shipping, returns, or warranty!",
            "Hey! How can I assist you with your tech gadgets and orders today?"
        ]
    },
    "goodbye": {
        "patterns": [
            r"\b(bye|goodbye|see\s*you|later|cya|take\s*care|exit|quit)\b"
        ],
        "responses": [
            "Goodbye! Have a fantastic day, and let me know if you need anything else.",
            "Take care! Thank you for chatting with NovaTech Support.",
            "Bye! Feel free to come back whenever you have questions."
        ]
    },
    "thanks": {
        "patterns": [
            r"\b(thanks|thank\s*you|thx|appreciate\s*it|grateful|awesome\s*thanks)\b"
        ],
        "responses": [
            "You're very welcome! Let me know if you need help with anything else.",
            "Happy to help! Do you have any other questions for me?",
            "Anytime! Glad I could assist you today."
        ]
    },
    "bot_identity": {
        "patterns": [
            r"\b(who\s*are\s*you|what\s*are\s*you|what\s*is\s*your\s*name|tell\s*me\s*about\s*yourself)\b"
        ],
        "responses": [
            "I am NovaBot, the AI customer support chatbot for NovaTech Electronics. I can answer your questions about orders, payments, shipping, warranty, returns, and more!",
            "I'm NovaTech's intelligent FAQ chatbot. Ask me anything about our gadgets, policies, shipping, or customer support!"
        ]
    },
    "help": {
        "patterns": [
            r"\b(help|what\s*can\s*you\s*do|how\s*to\s*use|commands|menu|options)\b"
        ],
        "responses": [
            "Here is what I can help you with:\n"
            "  * Orders & Tracking (e.g., 'Where is my order?', 'Can I cancel?')\n"
            "  * Shipping & Delivery (e.g., 'How long does shipping take?', 'Do you ship internationally?')\n"
            "  * Returns & Refunds (e.g., 'What is your return policy?', 'Damaged item')\n"
            "  * Payments & Billing (e.g., 'Payment options', 'Is checkout secure?')\n"
            "  * Warranty & Repairs (e.g., 'Warranty period', 'How to claim repair?')\n"
            "  * Discounts & Support (e.g., 'Student discount', 'Contact human agent')"
        ]
    }
}


class IntentHandler:
    """Classifies user queries against known conversational intents."""

    def __init__(self):
        import re
        self.re = re
        self.compiled_patterns = {}
        for intent, data in INTENTS.items():
            self.compiled_patterns[intent] = [
                self.re.compile(pat, self.re.IGNORECASE) for pat in data["patterns"]
            ]

    def check_intent(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Checks if the input text matches any conversational intent.
        Returns a dict with intent name and response, or None if not an intent.
        """
        clean_query = text.strip()
        words = clean_query.split()
        if len(words) <= 7:
            for intent, patterns in self.compiled_patterns.items():
                for pat in patterns:
                    if pat.search(clean_query):
                        response = random.choice(INTENTS[intent]["responses"])
                        return {
                            "is_intent": True,
                            "intent": intent,
                            "response": response,
                            "confidence": 1.0
                        }
        return None
