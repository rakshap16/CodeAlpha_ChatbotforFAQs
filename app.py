"""
Flask Web Application for FAQ Chatbot
Run with: python app.py
Visit: http://127.0.0.1:5000
"""

import sys
import os
from flask import Flask, render_template, request, jsonify

# Ensure project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import FAQChatbot

app = Flask(__name__)
bot = FAQChatbot()


@app.route("/")
def home():
    """Renders the interactive web chat interface."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """Processes user query and returns bot response with NLP metadata."""
    data = request.get_json(force=True, silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "status": "error",
            "response": "Please enter a question or topic.",
            "confidence": 0.0,
            "suggestions": []
        }), 400

    response = bot.get_response(message)
    nlp_diagnostics = bot.inspect_query(message)

    return jsonify({
        "status": "success",
        "query": message,
        "type": response.get("type"),
        "response": response.get("response"),
        "confidence": response.get("confidence", 0.0),
        "category": response.get("category"),
        "matched_question": response.get("matched_question"),
        "suggestions": response.get("suggestions", []),
        "diagnostics": nlp_diagnostics
    })


@app.route("/api/faqs", methods=["GET"])
def get_faqs_endpoint():
    """Returns the full knowledge base of FAQs grouped by category."""
    faqs = bot.matcher.get_all_faqs()
    categories = {}
    for item in faqs:
        cat = item.get("category", "General")
        categories.setdefault(cat, []).append(item)
    return jsonify({
        "status": "success",
        "total": len(faqs),
        "categories": categories
    })


@app.route("/api/inspect", methods=["POST"])
def inspect_endpoint():
    """Exposes NLTK preprocessing pipeline diagnostics."""
    data = request.get_json(force=True, silent=True) or {}
    message = data.get("message", "").strip()
    diagnostics = bot.inspect_query(message)
    return jsonify({
        "status": "success",
        "diagnostics": diagnostics
    })


if __name__ == "__main__":
    print("Starting NovaBot Web Service on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=False)
