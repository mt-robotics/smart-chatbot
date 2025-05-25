import re
from ..config import get_logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


class NLPEngine:
    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)

        self.confidence_threshold = config.CONFIDENCE_THRESHOLD if config else 0.5
        self.logger.info(
            "NLP Engine initialized with confidence threshold: %s",
            self.confidence_threshold,
        )
        # initialize NLP models - Use smaller models to reduce size
        try:
            import spacy

            self.nlp_en = spacy.load("en_core_web_sm")
            self.nlp_zh = spacy.load("zh_core_web_sm")
            self.logger.info("SpaCy models loaded successfully")
        except (ImportError, OSError):
            # Fallback if models not available
            self.nlp_en = None
            self.nlp_zh = None
            self.logger.warning("SpaCy models not available, using fallback methods.")

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
        entities = {}

        # Simplified entity extraction without spaCy if needed
        if language == "zh" and self.nlp_zh:
            nlp = self.nlp_zh
        elif self.nlp_en:
            nlp = self.nlp_en
        else:
            nlp = None

        if nlp:
            # Use spaCy for entity extraction
            doc = nlp(text)
            for ent in doc.ents:
                entities[ent.label_.lower()] = ent.text

        # Always do regex-based extraction (works with or without spaCy)

        # Extract order numbers (4-6 digits)
        order_pattern = r"\b\d{4,6}\b"
        orders = re.findall(order_pattern, text)
        if orders:
            entities["order_number"] = orders[0]
        # Extract email addresses
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        if emails:
            entities["email"] = emails[0]

        # Extract phone numbers (basic pattern)
        phone_pattern = r"\b\d{3}-\d{3}-\d{4}\b|\b\d{10}\b|\(\d{3}\)\s*\d{3}-\d{4}"
        phones = re.findall(phone_pattern, text)
        if phones:
            entities["phone"] = phones[0]

        # Extract money amounts
        money_pattern = r"\$\d+(?:\.\d{2})?|\d+(?:\.\d{2})?\s*(?:dollars?|USD)"
        money = re.findall(money_pattern, text, re.IGNORECASE)
        if money:
            entities["amount"] = money[0]

        # Extract dates (basic patterns)
        date_patterns = [
            r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # MM/DD/YYYY
            r"\b\d{4}-\d{1,2}-\d{1,2}\b",  # YYYY-MM-DD
            r"\b(?:today|tomorrow|yesterday)\b",  # Relative dates
        ]

        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            if dates:
                entities["date"] = dates[0]
                break

        # Extract product names (simple approach - capitalized words)
        if language == "en":
            product_pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b"
            products = re.findall(product_pattern, text)
            # Filter out common words
            common_words = {"Hello", "Please", "Thank", "Could", "Would", "Should"}
            products = [p for p in products if p not in common_words]
            if products:
                entities["product"] = products[0]

        return entities

    def train_intent_classifier(self, training_data):
        self.logger.info("Starting intent classifier training...")
        texts = []
        labels = []

        for intent, examples in training_data.items():
            for example in examples:
                texts.append(self.preprocess_text(example))
                labels.append(intent)

        X = self.vectorizer.fit_transform(texts)
        self.intent_classifier.fit(X, labels)
        self.trained = True

        self.logger.info(
            "Intent classifier trained with %d examples across %d intents",
            len(texts),
            len(training_data),
        )

    def classify_intent(self, text):
        if not self.trained:
            self.logger.error("Intent classifier not trained!")
            return "unknown", 0.0

        processed_text = self.preprocess_text(text)
        self.logger.debug("Classifying intent for: %s", processed_text)

        # Add keyword-based rules for better accuracy
        if any(
            word in processed_text
            for word in ["buy", "purchase", "want to buy", "interested in"]
        ):
            if not any(
                word in processed_text
                for word in ["cancel", "stop", "remove", "refund"]
            ):
                self.logger.debug("Keyword-based classification: product_inquiry")
                return "product_inquiry", 0.95

        if any(
            word in processed_text for word in ["cancel", "stop", "remove", "refund"]
        ):
            self.logger.debug("Keyword-based classification: cancel_order")
            return "cancel_order", 0.9

        # Fall back to ML classification
        X = self.vectorizer.transform([processed_text])
        intent = self.intent_classifier.predict(X)[0]
        confidence = max(self.intent_classifier.predict_proba(X)[0])

        self.logger.debug(
            "ML classification: %s (confidence: %.2f)", intent, confidence
        )

        # Convert NumPy types to Python Types
        return intent, confidence
