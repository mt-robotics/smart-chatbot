import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import re


class NLPEngine:
    def __init__(self):
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_zh = spacy.load("zh_core_web_sm")
        self.intent_classifier = MultinomialNB()
        self.vectorizer = TfidfVectorizer()
        self.trained = False

    def detect_language(self, text):
        # Simple Chinese Character detection
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        return "zh" if chinese_chars > 0 else "en"

    def preprocess_text(self, text):
        # Clean and normalize text
        text = text.lower().strip()
        text = re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)
        return text

    def extract_entities(self, text, language="en"):
        nlp = self.nlp_zh if language == "zh" else self.nlp_en
        doc = nlp(text)

        entities = {}

        # Extract order numbers
        order_pattern = r"\b\d{4,6}\b"
        orders = re.findall(order_pattern, text)
        if orders:
            entities["order_number"] = orders[0]

        # Extract other entities
        for ent in doc.ents:
            entities[ent.label_.lower()] = ent.text

        return entities

    def train_intent_classifier(self, training_data):
        texts = []
        labels = []

        for intent, examples in training_data.items():
            for example in examples:
                texts.append(self.preprocess_text(example))
                labels.append(intent)

        X = self.vectorizer.fit_transform(texts)
        self.intent_classifier.fit(X, labels)
        self.trained = True

    def classify_intent(self, text):
        if not self.trained:
            return "unknown", 0.0

        processed_text = self.preprocess_text(text)

        # Add keyword-based rules for better accuracy
        if any(
            word in processed_text
            for word in ["buy", "purchase", "want to buy", "interested in"]
        ):
            if not any(
                word in processed_text
                for word in ["cancel", "stop", "remove", "refund"]
            ):
                return "product_inquiry", 0.95

        if any(
            word in processed_text for word in ["cancel", "stop", "remove", "refund"]
        ):
            return "cancel_order", 0.9

        # Fall back to ML classification
        X = self.vectorizer.transform([processed_text])
        intent = self.intent_classifier.predict(X)[0]
        confidence = max(self.intent_classifier.predict_proba(X)[0])

        return intent, confidence
