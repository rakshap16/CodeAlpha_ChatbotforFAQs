# 🤖 NovaBot: AI FAQ Chatbot with NLP & Cosine Similarity

An intelligent, multi-interface customer support FAQ chatbot designed for **NovaTech Electronics & Gadgets**. The chatbot accurately understands user inquiries, applies Natural Language Processing (NLP) preprocessing, and finds the most relevant FAQ using **TF-IDF Vectorization** and **Cosine Similarity**.

---

## 🌟 Key Features

1. **Rich FAQ Knowledge Base**:
   - 20 comprehensive customer support FAQs covering:
     - 📦 **Orders & Tracking** (Status, cancellation, address modification)
     - 🚚 **Shipping & Delivery** (Durations, international shipping, missed delivery)
     - 🔄 **Returns & Refunds** (30-day window, refund timeframe, damaged item claims)
     - 💳 **Payments & Billing** (Credit cards, Apple Pay, PayPal, 256-bit SSL security)
     - 🛡️ **Warranty & Repairs** (1-year manufacturer warranty, repair claim procedure)
     - 🎟️ **Discounts & Promotions** (Student/military discounts, promo code redemption)
     - 🎧 **Products & Inventory** (Restock notifications, certified refurbished condition)
     - 👤 **Customer Support** (24/7 human agent phone, email, and live chat)
   - Stored in both structured [JSON](file:///c:/chatbot%20for%20FAQ's/data/faqs.json) and [CSV](file:///c:/chatbot%20for%20FAQ's/data/faqs.csv) formats for easy editing.

2. **Full NLP Preprocessing Pipeline (`src/preprocessor.py`)**:
   - **Contraction Expansion**: Resolves informal text (`"what's"` ➔ `"what is"`, `"can't"` ➔ `"cannot"`).
   - **Normalization & Cleaning**: Lowercasing, punctuation stripping, whitespace normalization.
   - **Tokenization**: NLTK `word_tokenize` with robust regex fallback.
   - **Stopword Removal**: Eliminates non-informative filler words using NLTK English stopwords.
   - **Lemmatization & Stemming**: Reduces inflected forms to base roots via NLTK `WordNetLemmatizer` (with `PorterStemmer` fallback).

3. **Hybrid Matching Engine (`src/matcher.py` & `src/intent_handler.py`)**:
   - **Conversational Intent Handling**: Intercepts greetings, farewells, gratitude, identity inquiries, and help requests with natural dialogues.
   - **TF-IDF + Cosine Similarity**: Computes similarity vectors over unigrams and bigrams (`ngram_range=(1, 2)`).
   - **Keyword Overlap Boosting**: Enhances retrieval for concise single-word and short multi-word queries.
   - **Confidence Scoring & Smart Fallback**:
     - $\ge 22\%$ Score: Displays answer with confidence percentage and related FAQ suggestions.
     - $12\% - 22\%$ Score: Displays polite clarification with top suggestions.
     - $< 12\%$ or Out-of-Scope: Friendly fallback offering human support and quick topic recommendations.

4. **Three Interactive User Interfaces**:
   - 🌐 **Modern Web UI (`app.py`)**: Sleek browser chat interface with live typing animation, quick reply chips, FAQ database browser modal, and an **interactive NLP Diagnostics Inspector**.
   - 💻 **Desktop GUI (`gui_chat.py`)**: Fast, native Tkinter desktop window with message bubbles, quick topic buttons, and an FAQ modal viewer.
   - ⌨️ **Command-Line Interface (`cli_chat.py`)**: Clean terminal chat loop with `/help`, `/faqs`, and `/inspect` commands.

---

## 📁 Project Structure

```
c:\chatbot for FAQ's\
│
├── data/
│   ├── faqs.json               # Structured FAQ knowledge base (questions, patterns, answers, tags)
│   └── faqs.csv                # Tabular CSV version of the FAQ dataset
│
├── src/
│   ├── __init__.py             # Python package marker
│   ├── preprocessor.py         # NLP cleaning, tokenization, stopword removal, lemmatization
│   ├── intent_handler.py       # Conversational intent matching (greetings, thanks, goodbyes)
│   ├── matcher.py              # TF-IDF vectorization, Cosine Similarity & ranking engine
│   └── chatbot.py              # Core Chatbot coordinator
│
├── static/                     # Web UI static assets
│   ├── css/
│   │   └── style.css           # Clean, responsive CSS stylesheet
│   └── js/
│       └── app.js              # Client-side chat logic, quick topics & NLP inspector
│
├── templates/
│   └── index.html              # Modern Web Chat UI HTML template
│
├── app.py                      # Flask Web server & REST API endpoints
├── gui_chat.py                 # Desktop Tkinter GUI application
├── cli_chat.py                 # Terminal interactive CLI chatbot
├── evaluate.py                 # Automated unit tests & 19-query benchmark suite
├── requirements.txt            # Python dependencies
└── README.md                   # Complete documentation
```

---

## 🚀 How to Run

### 1. Requirements & Setup
All dependencies are already installed. If setting up on a new environment:
```bash
pip install -r requirements.txt
```

---

### 2. Option A: Web Chat Interface (Recommended)
Launch the Flask web server:
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
**Web Features:**
- 💬 Chat directly with NovaBot in real-time.
- ⚡ Click quick suggestion chips for one-tap answers.
- 🔍 Open the **"NLP Inspector"** drawer to see how your question was tokenized, cleaned, and matched in real-time.
- 📚 Click **"FAQs"** to search the full FAQ directory.

---

### 3. Option B: Desktop GUI Application
Run the native desktop GUI without needing a browser:
```bash
python gui_chat.py
```
- Message bubbles with user and bot avatars.
- Quick topic buttons across the top.
- "Browse FAQs" modal dialog and "Clear" chat button.

---

### 4. Option C: Terminal CLI
Interact via the command line:
```bash
python cli_chat.py
```
Available CLI commands:
- `/help` — View available topics and commands.
- `/faqs` — Browse all indexed questions by category.
- `/inspect` — Interactively examine how any sentence is preprocessed by NLTK.
- `/exit` — Quit the chatbot.

---

## 🧪 Evaluation & Benchmark Results

Run the automated test suite and benchmark:
```bash
python evaluate.py
```

### Benchmark Summary:
- **Total Test Cases**: 19 diverse queries covering tracking, cancellations, international delivery, missed shipments, opened returns, refunds, damaged packages, Apple Pay, card security, warranty claims, password resets, address updates, student discounts, vouchers, restock checks, refurbished products, human agents, out-of-scope queries, and conversational intents.
- **Accuracy**: **100.0% (19/19)**
- **Average Confidence**: **95.1%**
- **Unit & Integration Tests**: **10/10 Passed** in 0.27s

---

## 🔬 NLP Pipeline Walkthrough

When a user submits: `"Where is my shipment right now?"`
1. **Contraction Expansion**: `"what's"` ➔ `"what is"`
2. **Text Cleaning**: Lowercase and strip punctuation ➔ `"where is my shipment right now"`
3. **NLTK Tokenization**: `['where', 'is', 'my', 'shipment', 'right', 'now']`
4. **Stopwords Filtered**: `['shipment', 'right']`
5. **Lemmatization**: `['shipment', 'right']`
6. **Vectorization**: Transformed into TF-IDF vector against FAQ unigram/bigram index.
7. **Cosine Similarity**: Matches FAQ #1 (*"How do I track my order?"*) with **100.0% confidence**!
