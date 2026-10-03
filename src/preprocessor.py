"""
Text Preprocessing Module for FAQ Chatbot
Handles tokenization, normalization, cleaning, stopword removal, and lemmatization/stemming.
"""

import re
import string
from typing import List, Optional

# NLTK imports with robust fallback handling
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer, PorterStemmer

    # Attempt to load resources safely
    try:
        STOPWORDS_SET = set(stopwords.words("english"))
    except Exception:
        nltk.download("stopwords", quiet=True)
        STOPWORDS_SET = set(stopwords.words("english"))

    try:
        LEMMATIZER = WordNetLemmatizer()
        LEMMATIZER.lemmatize("testing")
        HAS_LEMMATIZER = True
    except Exception:
        try:
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-1.4", quiet=True)
            LEMMATIZER = WordNetLemmatizer()
            LEMMATIZER.lemmatize("testing")
            HAS_LEMMATIZER = True
        except Exception:
            HAS_LEMMATIZER = False
            STEMMER = PorterStemmer()

    STEMMER = PorterStemmer()
except ImportError:
    STOPWORDS_SET = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
        "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
        "by", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", 
        "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", 
        "himself", "his", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", 
        "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", 
        "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", "should", "so", 
        "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", 
        "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", 
        "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", 
        "will", "with", "you", "your", "yours", "yourself", "yourselves"
    }
    HAS_LEMMATIZER = False
    STEMMER = None


# Common English contractions mapping
CONTRACTIONS = {
    "what's": "what is",
    "whatre": "what are",
    "whats": "what is",
    "how's": "how is",
    "hows": "how is",
    "where's": "where is",
    "wheres": "where is",
    "who's": "who is",
    "whos": "who is",
    "there's": "there is",
    "theres": "there is",
    "it's": "it is",
    "its": "it is",
    "can't": "cannot",
    "cant": "cannot",
    "won't": "will not",
    "wont": "will not",
    "don't": "do not",
    "dont": "do not",
    "didn't": "did not",
    "didnt": "did not",
    "doesn't": "does not",
    "doesnt": "does not",
    "i'm": "i am",
    "im": "i am",
    "i've": "i have",
    "ive": "i have",
    "i'll": "i will",
    "ill": "i will",
    "you're": "you are",
    "youre": "you are",
    "you've": "you have",
    "youve": "you have",
    "you'll": "you will",
    "they're": "they are",
    "theyre": "they are",
    "we're": "we are",
    "were": "were",
    "isn't": "is not",
    "isnt": "is not",
    "aren't": "are not",
    "arent": "are not",
    "haven't": "have not",
    "havent": "have not",
    "hasn't": "has not",
    "hasnt": "has not",
    "wouldn't": "would not",
    "couldn't": "could not",
    "shouldn't": "should not"
}

# Words that provide critical intent in FAQ questions which shouldn't be stripped unconditionally
PRESERVED_FAQ_TERMS = {"how", "what", "where", "when", "why", "who", "can", "not", "no"}


class TextPreprocessor:
    """
    NLP Preprocessing pipeline including:
    - Contraction expansion
    - Lowercasing and punctuation removal
    - NLTK Tokenization
    - FAQ-aware Stopword Filtering
    - Lemmatization (or Stemming fallback)
    """

    def __init__(self, use_lemmatizer: bool = True, preserve_question_words: bool = False):
        self.use_lemmatizer = use_lemmatizer and HAS_LEMMATIZER
        self.preserve_question_words = preserve_question_words
        self.stopwords = STOPWORDS_SET.copy()
        if self.preserve_question_words:
            self.stopwords = self.stopwords - PRESERVED_FAQ_TERMS

    def expand_contractions(self, text: str) -> str:
        """Expands informal contractions (e.g., 'don't' -> 'do not')."""
        words = text.split()
        expanded = []
        for word in words:
            clean_word = word.lower()
            if clean_word in CONTRACTIONS:
                expanded.append(CONTRACTIONS[clean_word])
            else:
                expanded.append(word)
        return " ".join(expanded)

    def clean_text(self, text: str) -> str:
        """Removes punctuation and unwanted characters, keeping alphanumeric and spaces."""
        text = text.lower()
        text = self.expand_contractions(text)
        # Replace hyphens with space to separate compound words (e.g., 'check-out' -> 'check out')
        text = text.replace("-", " ")
        # Remove punctuation
        text = re.sub(r"[^\w\s]", " ", text)
        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes text using NLTK word_tokenize with regex fallback."""
        cleaned = self.clean_text(text)
        try:
            tokens = word_tokenize(cleaned)
        except Exception:
            tokens = re.findall(r"\b\w+\b", cleaned)
        return tokens

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Filters out standard English stopwords."""
        return [tok for tok in tokens if tok not in self.stopwords and len(tok) > 1]

    def lemmatize_or_stem(self, tokens: List[str]) -> List[str]:
        """Lemmatizes tokens to their root form, or stems if lemmatizer is unavailable."""
        if self.use_lemmatizer:
            # Lemmatize both as noun and verb to obtain the best canonical root
            processed = []
            for tok in tokens:
                lemma = LEMMATIZER.lemmatize(tok, pos="v")
                if lemma == tok:
                    lemma = LEMMATIZER.lemmatize(tok, pos="n")
                processed.append(lemma)
            return processed
        elif STEMMER:
            return [STEMMER.stem(tok) for tok in tokens]
        return tokens

    def preprocess(self, text: str) -> str:
        """
        Full end-to-end preprocessing pipeline.
        Returns a single normalized string ready for TF-IDF / NLP similarity.
        """
        if not text or not isinstance(text, str):
            return ""
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        processed_tokens = self.lemmatize_or_stem(tokens)
        return " ".join(processed_tokens)

    def preprocess_tokens(self, text: str) -> List[str]:
        """Full pipeline returning processed token list."""
        if not text or not isinstance(text, str):
            return []
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        return self.lemmatize_or_stem(tokens)
