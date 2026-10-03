"""
Core FAQ Chatbot Engine
Orchestrates text preprocessing, conversational intent handling, and FAQ similarity matching.
"""

from typing import Dict, Any, Optional
import os
from src.preprocessor import TextPreprocessor
from src.intent_handler import IntentHandler
from src.matcher import FAQMatcher


class FAQChatbot:
    """
    Main FAQ Chatbot engine.
    Processes user input, routes conversational intents,
    and returns NLP-ranked answers with confidence scores.
    """

    def __init__(
        self,
        faq_path: Optional[str] = None,
        match_threshold: float = 0.22,
        clarification_threshold: float = 0.12
    ):
        if faq_path is None:
            # Locate relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            faq_path = os.path.join(base_dir, "data", "faqs.json")

        self.preprocessor = TextPreprocessor()
        self.intent_handler = IntentHandler()
        self.matcher = FAQMatcher(
            faq_path=faq_path,
            match_threshold=match_threshold,
            clarification_threshold=clarification_threshold
        )

    def get_response(self, user_message: str) -> Dict[str, Any]:
        """
        Processes a user message and returns a comprehensive response dictionary.
        """
        raw_message = (user_message or "").strip()
        if not raw_message:
            return {
                "type": "empty",
                "response": "Please enter a question or topic so I can help you.",
                "confidence": 0.0,
                "preprocessed": "",
                "suggestions": []
            }

        # Step 1: Check for Conversational Intents (Greeting, Thanks, Goodbye, Help, Identity)
        intent_match = self.intent_handler.check_intent(raw_message)
        if intent_match:
            return {
                "type": "intent",
                "intent": intent_match["intent"],
                "response": intent_match["response"],
                "confidence": 1.0,
                "matched_question": None,
                "preprocessed": self.preprocessor.preprocess(raw_message),
                "suggestions": [
                    "How do I track my order?",
                    "What payment methods do you accept?",
                    "What is your return policy?"
                ] if intent_match["intent"] in ("greeting", "help") else []
            }

        # Step 2: FAQ Vector Search via TF-IDF & Cosine Similarity
        match_result = self.matcher.match(raw_message)
        preprocessed_query = self.preprocessor.preprocess(raw_message)

        if match_result.get("matched", False):
            return {
                "type": "faq_match",
                "response": match_result["answer"],
                "confidence": match_result["confidence"],
                "category": match_result.get("category"),
                "matched_question": match_result["matched_question"],
                "faq_id": match_result.get("faq_id"),
                "preprocessed": preprocessed_query,
                "suggestions": match_result.get("suggestions", [])
            }
        elif match_result.get("is_clarification", False):
            return {
                "type": "clarification",
                "response": match_result["answer"],
                "confidence": match_result["confidence"],
                "matched_question": None,
                "preprocessed": preprocessed_query,
                "suggestions": match_result.get("suggestions", [])
            }
        else:
            return {
                "type": "fallback",
                "response": match_result["answer"],
                "confidence": match_result["confidence"],
                "matched_question": None,
                "preprocessed": preprocessed_query,
                "suggestions": match_result.get("suggestions", [])
            }

    def inspect_query(self, user_message: str) -> Dict[str, Any]:
        """Diagnostic helper showing exact tokenization and preprocessing stages."""
        tokens = self.preprocessor.tokenize(user_message)
        without_stopwords = self.preprocessor.remove_stopwords(tokens)
        lemmas = self.preprocessor.lemmatize_or_stem(without_stopwords)
        normalized = " ".join(lemmas)

        return {
            "original": user_message,
            "tokens": tokens,
            "after_stopwords": without_stopwords,
            "lemmatized_tokens": lemmas,
            "normalized_string": normalized
        }
