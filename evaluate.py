"""
Comprehensive Evaluation & Test Suite for FAQ Chatbot
Tests preprocessing, intent handling, TF-IDF cosine similarity accuracy, and API endpoints.
Run with: python evaluate.py
"""

import sys
import os
import unittest
import json

# Ensure project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.preprocessor import TextPreprocessor
from src.intent_handler import IntentHandler
from src.matcher import FAQMatcher
from src.chatbot import FAQChatbot
from app import app


class TestFAQChatbot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preprocessor = TextPreprocessor()
        cls.intent_handler = IntentHandler()
        cls.matcher = FAQMatcher()
        cls.bot = FAQChatbot()
        cls.client = app.test_client()

    # ----------------------------------------------------
    # 1. NLP Preprocessing Tests
    # ----------------------------------------------------
    def test_preprocessor_contractions(self):
        text = "What's the return policy? I don't know if I can't track it."
        cleaned = self.preprocessor.clean_text(text)
        self.assertIn("what is", cleaned)
        self.assertIn("do not", cleaned)
        self.assertIn("cannot", cleaned)

    def test_preprocessor_tokenization_and_lemmatization(self):
        text = "Customers are returning broken gadgets"
        tokens = self.preprocessor.preprocess_tokens(text)
        # Verify tokens are lowercased and lemmatized/stemmed
        self.assertTrue(any("return" in t for t in tokens))
        self.assertTrue(any("break" in t or "broken" in t for t in tokens))
        self.assertTrue(any("gadget" in t for t in tokens))

    # ----------------------------------------------------
    # 2. Intent Handling Tests
    # ----------------------------------------------------
    def test_greetings_intent(self):
        for phrase in ["Hello", "Hi there", "hey", "good morning"]:
            res = self.intent_handler.check_intent(phrase)
            self.assertIsNotNone(res, f"Failed for phrase: {phrase}")
            self.assertEqual(res["intent"], "greeting")

    def test_thanks_and_bye_intents(self):
        thanks_res = self.intent_handler.check_intent("thank you so much")
        self.assertIsNotNone(thanks_res)
        self.assertEqual(thanks_res["intent"], "thanks")

        bye_res = self.intent_handler.check_intent("bye take care")
        self.assertIsNotNone(bye_res)
        self.assertEqual(bye_res["intent"], "goodbye")

    # ----------------------------------------------------
    # 3. FAQ Cosine Similarity & Intent Matching Benchmark
    # ----------------------------------------------------
    def test_faq_matching_accuracy(self):
        test_cases = [
            # (User Query, Expected FAQ ID, Description)
            ("Where is my shipment right now?", 1, "Order tracking"),
            ("Can I cancel my purchase before it ships?", 2, "Cancel order"),
            ("How many days will delivery take?", 3, "Shipping duration"),
            ("Can you deliver to Europe or Canada?", 4, "International shipping"),
            ("What if nobody is home for the delivery?", 5, "Missed delivery"),
            ("How do I return an opened box product?", 6, "Return policy"),
            ("When does the money get credited back for my return?", 7, "Refund timeframe"),
            ("My screen arrived broken and damaged", 8, "Damaged item"),
            ("Do you accept Apple Pay or PayPal?", 9, "Payment methods"),
            ("Is my credit card information encrypted and secure?", 10, "Payment security"),
            ("What does the 1 year warranty cover?", 11, "Warranty coverage"),
            ("How to request a repair for my broken gadget under warranty?", 12, "Claim warranty"),
            ("I forgot my password and cannot sign in", 13, "Password reset"),
            ("Change the shipping destination address in my profile", 14, "Update address"),
            ("Are there coupon codes for college students?", 15, "Student discounts"),
            ("Where do I enter my promo voucher code?", 16, "Redeem promo code"),
            ("When will out-of-stock headphones be available?", 17, "Restock / inventory"),
            ("Are certified refurbished devices safe to buy?", 18, "Refurbished condition"),
            ("I want to speak with a human customer service agent", 19, "Contact agent"),
        ]

        correct_matches = 0
        total = len(test_cases)
        total_confidence = 0.0

        print("\n" + "=" * 65)
        print(f"RUNNING FAQ BENCHMARK ON {total} DIVERSE TEST QUERIES")
        print("=" * 65)

        for query, expected_id, desc in test_cases:
            res = self.bot.get_response(query)
            matched_id = res.get("faq_id")
            conf = res.get("confidence", 0.0)
            total_confidence += conf
            is_correct = (matched_id == expected_id)
            if is_correct:
                correct_matches += 1

            status = "PASS" if is_correct else "FAIL"
            print(f"[{status}] Query: '{query}' -> FAQ #{matched_id} (Expected #{expected_id}) [Conf: {conf * 100:.1f}%]")

        accuracy = (correct_matches / total) * 100
        avg_conf = (total_confidence / total) * 100
        print("-" * 65)
        print(f"ACCURACY: {accuracy:.1f}% ({correct_matches}/{total}) | AVG CONFIDENCE: {avg_conf:.1f}%")
        print("=" * 65 + "\n")

        self.assertGreaterEqual(accuracy, 90.0, "Chatbot benchmark accuracy should be >= 90%")

    # ----------------------------------------------------
    # 4. Out-of-Scope Fallback Test
    # ----------------------------------------------------
    def test_out_of_scope_fallback(self):
        out_of_scope_queries = [
            "How do I bake a chocolate cake?",
            "What is the distance between Mars and Jupiter?",
            "qwerty asdfgh zxcvbnm"
        ]
        for query in out_of_scope_queries:
            res = self.bot.get_response(query)
            self.assertEqual(res["type"], "fallback", f"Expected fallback for query: '{query}'")

    # ----------------------------------------------------
    # 5. Flask Web API Endpoints Tests
    # ----------------------------------------------------
    def test_api_chat_success(self):
        resp = self.client.post(
            "/api/chat",
            data=json.dumps({"message": "How do I return a product?"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data.decode("utf-8"))
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["type"], "faq_match")
        self.assertIn("30-day", data["response"])
        self.assertIn("diagnostics", data)

    def test_api_chat_empty_query(self):
        resp = self.client.post(
            "/api/chat",
            data=json.dumps({"message": ""}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_api_faqs_list(self):
        resp = self.client.get("/api/faqs")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data.decode("utf-8"))
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["total"], 20)
        self.assertIn("Orders & Tracking", data["categories"])

    def test_api_inspect(self):
        resp = self.client.post(
            "/api/inspect",
            data=json.dumps({"message": "Testing order tracking"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data.decode("utf-8"))
        self.assertIn("diagnostics", data)
        self.assertIn("tokens", data["diagnostics"])


if __name__ == "__main__":
    unittest.main()
