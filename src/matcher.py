"""
FAQ Matching Engine
Utilizes TF-IDF vectorization, N-grams, Cosine Similarity, and Keyword Boosting.
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocessor import TextPreprocessor


class FAQMatcher:
    """
    Matches user input questions against the FAQ knowledge base
    using TF-IDF representation and Cosine Similarity with hybrid keyword boosting.
    """

    def __init__(
        self,
        faq_path: str = "data/faqs.json",
        match_threshold: float = 0.22,
        clarification_threshold: float = 0.12
    ):
        self.faq_path = faq_path
        self.match_threshold = match_threshold
        self.clarification_threshold = clarification_threshold
        self.preprocessor = TextPreprocessor()
        self.faqs: List[Dict[str, Any]] = []
        self.indexed_documents: List[str] = []
        self.doc_to_faq_map: List[int] = []  # Maps indexed document index to FAQ index
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None

        self.load_and_index()

    def load_and_index(self):
        """Loads FAQ data from JSON and builds TF-IDF index."""
        if not os.path.exists(self.faq_path):
            raise FileNotFoundError(f"FAQ dataset file not found at: {self.faq_path}")

        with open(self.faq_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.faqs = data.get("faq_data", [])

        self.indexed_documents = []
        self.doc_to_faq_map = []

        for faq_idx, faq in enumerate(self.faqs):
            # Index primary question
            q_clean = self.preprocessor.preprocess(faq["question"])
            self.indexed_documents.append(q_clean)
            self.doc_to_faq_map.append(faq_idx)

            # Index alternate phrasing patterns
            for pattern in faq.get("patterns", []):
                p_clean = self.preprocessor.preprocess(pattern)
                if p_clean:
                    self.indexed_documents.append(p_clean)
                    self.doc_to_faq_map.append(faq_idx)

            # Index combined query with tags for broader coverage
            tags_str = " ".join(faq.get("tags", []))
            combo_clean = self.preprocessor.preprocess(f"{faq['question']} {tags_str}")
            self.indexed_documents.append(combo_clean)
            self.doc_to_faq_map.append(faq_idx)

        # Fit TF-IDF Vectorizer with Unigram and Bigram support
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            norm="l2"
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.indexed_documents)

    def _keyword_overlap_score(self, query_tokens: List[str], faq: Dict[str, Any]) -> float:
        """Calculates token overlap ratio between query and FAQ tags/question."""
        if not query_tokens:
            return 0.0

        faq_text = (
            faq["question"] + " " + " ".join(faq.get("tags", [])) + " " + " ".join(faq.get("patterns", []))
        ).lower()
        faq_tokens = set(self.preprocessor.tokenize(faq_text))

        matches = sum(1 for tok in query_tokens if tok in faq_tokens)
        return min(1.0, matches / len(query_tokens))

    def match(self, user_query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Finds the best matching FAQ for the user query.
        Returns match metadata, confidence score, answers, and suggested related questions.
        """
        if not user_query or not user_query.strip():
            return {
                "matched": False,
                "confidence": 0.0,
                "answer": "Please enter a valid question or keyword.",
                "matched_question": None,
                "suggestions": []
            }

        # Preprocess the query
        processed_query = self.preprocessor.preprocess(user_query)
        query_tokens = self.preprocessor.preprocess_tokens(user_query)

        if not processed_query:
            # All tokens were filtered out (e.g. pure punctuation or unsupported chars)
            return {
                "matched": False,
                "confidence": 0.0,
                "answer": "I could not understand your question. Could you please rephrase it with more details?",
                "matched_question": None,
                "suggestions": [f["question"] for f in self.faqs[:3]]
            }

        # Compute TF-IDF representation and Cosine Similarity
        user_vector = self.vectorizer.transform([processed_query])
        if user_vector.nnz == 0:
            return {
                "matched": False,
                "is_fallback": True,
                "confidence": 0.0,
                "answer": (
                    "I'm sorry, I couldn't find a matching FAQ for your question. "
                    "You can try rephrasing, or ask about orders, shipping, returns, warranty, or speaking to human support."
                ),
                "matched_question": None,
                "suggestions": [
                    "How do I track my order?",
                    "What is your return policy?",
                    "How can I contact customer support?"
                ]
            }

        similarities = cosine_similarity(user_vector, self.tfidf_matrix)[0]

        # Aggregate max similarity per FAQ entry
        faq_scores = {}
        for doc_idx, sim in enumerate(similarities):
            faq_idx = self.doc_to_faq_map[doc_idx]
            if faq_idx not in faq_scores or sim > faq_scores[faq_idx]:
                faq_scores[faq_idx] = float(sim)

        # Compute hybrid score by adding keyword overlap boost
        final_scores: List[Tuple[int, float]] = []
        for faq_idx, cos_sim in faq_scores.items():
            faq = self.faqs[faq_idx]
            kw_overlap = self._keyword_overlap_score(query_tokens, faq)
            # Hybrid formula: 75% cosine similarity + 25% keyword overlap
            hybrid_score = (0.75 * cos_sim) + (0.25 * kw_overlap)
            final_scores.append((faq_idx, hybrid_score))

        # Sort descending by hybrid score
        final_scores.sort(key=lambda x: x[1], reverse=True)

        if not final_scores:
            return {
                "matched": False,
                "confidence": 0.0,
                "answer": "I'm sorry, I couldn't find an answer to your question.",
                "matched_question": None,
                "suggestions": [f["question"] for f in self.faqs[:3]]
            }

        best_faq_idx, best_score = final_scores[0]
        best_faq = self.faqs[best_faq_idx]

        # Prepare suggestions from top alternative matches
        suggestions = []
        for idx, score in final_scores[1:top_k + 1]:
            if score > 0.05 and self.faqs[idx]["id"] != best_faq["id"]:
                suggestions.append(self.faqs[idx]["question"])

        # Case 1: High confidence match
        if best_score >= self.match_threshold:
            return {
                "matched": True,
                "confidence": round(best_score, 4),
                "faq_id": best_faq["id"],
                "category": best_faq["category"],
                "matched_question": best_faq["question"],
                "answer": best_faq["answer"],
                "suggestions": suggestions
            }

        # Case 2: Borderline match (Clarification)
        elif best_score >= self.clarification_threshold:
            clarification_suggestions = [best_faq["question"]] + suggestions[:2]
            return {
                "matched": False,
                "is_clarification": True,
                "confidence": round(best_score, 4),
                "answer": (
                    "I'm not completely certain, but here are some related topics that might answer your question:"
                ),
                "matched_question": None,
                "suggestions": clarification_suggestions
            }

        # Case 3: Low confidence (Fallback)
        else:
            return {
                "matched": False,
                "is_fallback": True,
                "confidence": round(best_score, 4),
                "answer": (
                    "I'm sorry, I couldn't find a matching FAQ for your question. "
                    "You can try rephrasing, or ask about orders, shipping, returns, warranty, or speaking to human support."
                ),
                "matched_question": None,
                "suggestions": [
                    "How do I track my order?",
                    "What is your return policy?",
                    "How can I contact customer support?"
                ]
            }

    def get_all_faqs(self) -> List[Dict[str, Any]]:
        """Returns the full list of FAQs."""
        return self.faqs

    def get_categories(self) -> List[str]:
        """Returns unique categories in the dataset."""
        cats = []
        for faq in self.faqs:
            if faq["category"] not in cats:
                cats.append(faq["category"])
        return cats
