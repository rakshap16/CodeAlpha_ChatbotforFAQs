"""
Interactive CLI Chatbot Interface
Run with: python cli_chat.py
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import FAQChatbot


def print_banner():
    print("=" * 65)
    print("         NOVATECH SUPPORT FAQ CHATBOT (CLI INTERFACE)        ")
    print("=" * 65)
    print("Welcome! Ask any question regarding orders, delivery, refunds,")
    print("payments, warranty, or customer support.")
    print("\nSpecial commands:")
    print("  /help     - Show chatbot capabilities and help")
    print("  /faqs     - List all indexed FAQ questions")
    print("  /inspect  - View NLP preprocessing & tokenization details")
    print("  /exit     - Exit the chatbot")
    print("=" * 65 + "\n")


def list_faqs(bot: FAQChatbot):
    print("\n--- ALL AVAILABLE FAQs BY CATEGORY ---")
    faqs = bot.matcher.get_all_faqs()
    categories = {}
    for f in faqs:
        cat = f.get("category", "General")
        categories.setdefault(cat, []).append(f["question"])

    for cat, questions in categories.items():
        print(f"\n[{cat}]")
        for q in questions:
            print(f"  * {q}")
    print("--------------------------------------\n")


def inspect_query_cli(bot: FAQChatbot):
    query = input("\nEnter query to inspect with NLP pipeline: ").strip()
    if not query:
        print("Empty query.")
        return
    info = bot.inspect_query(query)
    print("\n--- NLP PIPELINE DIAGNOSTICS ---")
    print(f"Raw Input:          {info['original']}")
    print(f"NLTK Tokens:        {info['tokens']}")
    print(f"After Stopwords:    {info['after_stopwords']}")
    print(f"Lemmatized Tokens:  {info['lemmatized_tokens']}")
    print(f"Normalized String:  {info['normalized_string']}")
    print("--------------------------------\n")


def run_cli():
    # Set UTF-8 safe output where applicable
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    bot = FAQChatbot()
    print_banner()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in ("/exit", "/quit", "exit", "quit"):
            print("\nNovaBot: Goodbye! Have a great day!")
            break
        elif cmd == "/help":
            res = bot.get_response("help")
            print(f"\nNovaBot:\n{res['response']}\n")
            continue
        elif cmd == "/faqs":
            list_faqs(bot)
            continue
        elif cmd.startswith("/inspect"):
            inspect_query_cli(bot)
            continue

        response = bot.get_response(user_input)

        print("\nNovaBot:")
        print(response["response"])

        # Display matching metadata if an FAQ was matched
        if response.get("type") == "faq_match":
            print(f"\n[Matched FAQ: '{response.get('matched_question')}']")
            print(f"[Category: {response.get('category')} | Match Confidence: {response.get('confidence') * 100:.1f}%]")

        # Show helpful suggestions if available
        suggestions = response.get("suggestions", [])
        if suggestions:
            print("\nRelated Questions:")
            for s in suggestions[:3]:
                print(f"  * {s}")

        print("-" * 65)


if __name__ == "__main__":
    run_cli()
