"""
Desktop GUI Interface for FAQ Chatbot (Tkinter)
Run with: python gui_chat.py
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont

# Ensure project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import FAQChatbot


class ModernChatGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NovaBot - Customer Support FAQ Assistant")
        self.root.geometry("720x780")
        self.root.minsize(580, 600)

        # Initialize core chatbot
        self.bot = FAQChatbot()

        # Color Palette
        self.bg_main = "#F3F4F6"        # Cool light gray background
        self.header_bg = "#1E293B"      # Dark slate blue header
        self.header_fg = "#FFFFFF"
        self.user_bubble_bg = "#2563EB"  # Royal blue for user
        self.user_bubble_fg = "#FFFFFF"
        self.bot_bubble_bg = "#FFFFFF"   # Crisp white card for bot
        self.bot_bubble_fg = "#1F2937"
        self.accent_color = "#3B82F6"
        self.meta_fg = "#6B7280"        # Gray metadata text

        self.root.configure(bg=self.bg_main)
        self._setup_styles()
        self._build_header()
        self._build_quick_replies()
        self._build_chat_display()
        self._build_input_area()
        self._send_welcome_message()

    def _setup_styles(self):
        self.font_header = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_subtitle = tkfont.Font(family="Segoe UI", size=9)
        self.font_msg = tkfont.Font(family="Segoe UI", size=10)
        self.font_bold = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.font_meta = tkfont.Font(family="Segoe UI", size=8, slant="italic")
        self.font_btn = tkfont.Font(family="Segoe UI", size=9, weight="bold")

    def _build_header(self):
        header_frame = tk.Frame(self.root, bg=self.header_bg, height=65)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_container = tk.Frame(header_frame, bg=self.header_bg)
        title_container.pack(side=tk.LEFT, padx=16, pady=10)

        title_lbl = tk.Label(
            title_container,
            text="[NovaBot] Customer Support FAQ Assistant",
            font=self.font_header,
            bg=self.header_bg,
            fg=self.header_fg
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            title_container,
            text="Powered by NLP Tokenization, Lemmatization & Cosine Similarity",
            font=self.font_subtitle,
            bg=self.header_bg,
            fg="#94A3B8"
        )
        sub_lbl.pack(anchor="w")

        # Action Buttons on Header
        btn_container = tk.Frame(header_frame, bg=self.header_bg)
        btn_container.pack(side=tk.RIGHT, padx=16, pady=14)

        faqs_btn = tk.Button(
            btn_container,
            text="Browse FAQs",
            font=self.font_btn,
            bg="#334155",
            fg="#FFFFFF",
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.show_faqs_dialog
        )
        faqs_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            btn_container,
            text="Clear",
            font=self.font_btn,
            bg="#334155",
            fg="#FFFFFF",
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.clear_chat
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

    def _build_quick_replies(self):
        quick_frame = tk.Frame(self.root, bg="#E2E8F0", height=42)
        quick_frame.pack(fill=tk.X, side=tk.TOP)

        lbl = tk.Label(
            quick_frame,
            text="Quick Topics:",
            font=self.font_bold,
            bg="#E2E8F0",
            fg="#475569"
        )
        lbl.pack(side=tk.LEFT, padx=(16, 8), pady=8)

        sample_topics = [
            ("Track Order", "How do I track my order?"),
            ("Return Policy", "What is your return policy?"),
            ("Payments", "What payment methods do you accept?"),
            ("Warranty", "Do products come with a warranty?"),
            ("Contact Support", "How can I contact a live agent?")
        ]

        for label_text, query_text in sample_topics:
            btn = tk.Button(
                quick_frame,
                text=label_text,
                font=self.font_btn,
                bg="#FFFFFF",
                fg="#2563EB",
                relief=tk.RIDGE,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda q=query_text: self.submit_query(q)
            )
            btn.pack(side=tk.LEFT, padx=4, pady=6)

    def _build_chat_display(self):
        chat_container = tk.Frame(self.root, bg=self.bg_main)
        chat_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)

        self.scrollbar = tk.Scrollbar(chat_container)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_area = tk.Text(
            chat_container,
            wrap=tk.WORD,
            bg=self.bg_main,
            relief=tk.FLAT,
            yscrollcommand=self.scrollbar.set,
            font=self.font_msg,
            padx=10,
            pady=10
        )
        self.chat_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.chat_area.yview)

        # Configure Text Tags for message layout
        self.chat_area.tag_configure("user_header", font=self.font_bold, foreground="#1D4ED8", justify="right")
        self.chat_area.tag_configure("user_msg", font=self.font_msg, foreground="#111827", justify="right")

        self.chat_area.tag_configure("bot_header", font=self.font_bold, foreground="#0F766E", justify="left")
        self.chat_area.tag_configure("bot_msg", font=self.font_msg, foreground="#1F2937", justify="left")

        self.chat_area.tag_configure("meta_info", font=self.font_meta, foreground="#64748B", justify="left")
        self.chat_area.tag_configure("suggestion_tag", font=self.font_msg, foreground="#2563EB", justify="left")
        self.chat_area.tag_configure("divider", foreground="#CBD5E1", justify="center")

        self.chat_area.config(state=tk.DISABLED)

    def _build_input_area(self):
        input_container = tk.Frame(self.root, bg="#FFFFFF", height=70, relief=tk.RIDGE, bd=1)
        input_container.pack(fill=tk.X, side=tk.BOTTOM, padx=16, pady=(0, 16))

        self.entry_var = tk.StringVar()
        self.entry_field = tk.Entry(
            input_container,
            textvariable=self.entry_var,
            font=self.font_msg,
            relief=tk.FLAT,
            bg="#F9FAFB"
        )
        self.entry_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=14, pady=12)
        self.entry_field.bind("<Return>", lambda event: self.send_message())
        self.entry_field.focus_set()

        send_btn = tk.Button(
            input_container,
            text="Send",
            font=self.font_btn,
            bg=self.user_bubble_bg,
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.send_message
        )
        send_btn.pack(side=tk.RIGHT, padx=12, pady=10)

    def _send_welcome_message(self):
        self.display_bot_message(
            "Hello! Welcome to NovaTech Support Assistant.\n"
            "Ask me any question about your orders, shipping options, return requests, warranty claims, or payment methods.",
            meta_info="Ready to assist | NLP Model Initialized"
        )

    def send_message(self):
        user_text = self.entry_var.get().strip()
        if not user_text:
            return
        self.entry_var.set("")
        self.submit_query(user_text)

    def submit_query(self, query: str):
        # 1. Display User Message
        self.display_user_message(query)

        # 2. Get Bot Response
        res = self.bot.get_response(query)
        msg_type = res.get("type")
        bot_reply = res.get("response", "")
        meta = []

        if msg_type == "faq_match":
            conf = res.get("confidence", 0.0) * 100
            q_match = res.get("matched_question", "")
            cat = res.get("category", "")
            meta.append(f"Matched FAQ: \"{q_match}\" ({cat}) | Confidence: {conf:.1f}%")
        elif msg_type == "intent":
            meta.append(f"Intent detected: {res.get('intent')} | 100% confidence")
        elif msg_type == "clarification":
            meta.append("Confidence below primary threshold | Suggested queries below")
        else:
            meta.append("Fallback | No direct FAQ match found")

        meta_str = " | ".join(meta)
        suggestions = res.get("suggestions", [])

        self.display_bot_message(bot_reply, meta_info=meta_str, suggestions=suggestions)

    def display_user_message(self, message: str):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "\nYou\n", "user_header")
        self.chat_area.insert(tk.END, f"{message}\n", "user_msg")
        self.chat_area.insert(tk.END, "--------------------------------------------------------\n", "divider")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def display_bot_message(self, message: str, meta_info: str = "", suggestions: list = None):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "\nNovaBot\n", "bot_header")
        self.chat_area.insert(tk.END, f"{message}\n", "bot_msg")

        if meta_info:
            self.chat_area.insert(tk.END, f"[{meta_info}]\n", "meta_info")

        if suggestions:
            self.chat_area.insert(tk.END, "\nRelated FAQ Suggestions:\n", "meta_info")
            for s in suggestions[:3]:
                self.chat_area.insert(tk.END, f"  * {s}\n", "suggestion_tag")

        self.chat_area.insert(tk.END, "--------------------------------------------------------\n", "divider")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def clear_chat(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete("1.0", tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self._send_welcome_message()

    def show_faqs_dialog(self):
        """Opens a modal popup listing all available FAQs grouped by category."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Indexed Knowledge Base FAQs")
        dialog.geometry("640x550")
        dialog.minsize(500, 400)
        dialog.configure(bg="#F8FAFC")

        lbl = tk.Label(
            dialog,
            text="Knowledge Base FAQs by Category",
            font=self.font_header,
            bg="#F8FAFC",
            fg="#0F172A",
            pady=10
        )
        lbl.pack(fill=tk.X)

        frame = tk.Frame(dialog, bg="#F8FAFC")
        frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        sb = tk.Scrollbar(frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        txt = tk.Text(frame, wrap=tk.WORD, yscrollcommand=sb.set, font=self.font_msg, padx=10, pady=10)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=txt.yview)

        faqs = self.bot.matcher.get_all_faqs()
        categories = {}
        for f in faqs:
            cat = f.get("category", "General")
            categories.setdefault(cat, []).append(f)

        txt.tag_configure("cat_header", font=self.font_bold, foreground="#1E40AF")
        txt.tag_configure("faq_q", font=self.font_bold, foreground="#0F172A")
        txt.tag_configure("faq_a", font=self.font_msg, foreground="#334155")

        for cat, items in categories.items():
            txt.insert(tk.END, f"\n=== {cat.upper()} ===\n\n", "cat_header")
            for item in items:
                txt.insert(tk.END, f"Q: {item['question']}\n", "faq_q")
                txt.insert(tk.END, f"A: {item['answer']}\n\n", "faq_a")

        txt.config(state=tk.DISABLED)

        close_btn = tk.Button(
            dialog,
            text="Close",
            font=self.font_btn,
            bg="#334155",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            command=dialog.destroy
        )
        close_btn.pack(pady=10)


def main():
    root = tk.Tk()
    app = ModernChatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
