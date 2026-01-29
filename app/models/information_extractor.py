import re
from typing import Dict, List, Any

# Absolute import from project root
from app.utils.config import get_logger

logger = get_logger(__name__)


class InformationExtractor:
    """Extract meaningful information from user messages"""

    def __init__(self):
        self.logger = get_logger(__name__)

        # Try to load spaCy models
        self.nlp_en = None
        self.nlp_zh = None
        self._load_spacy_models()

        # Pattern libraries for extraction
        self.patterns = self._build_patterns()

        self.logger.info("Information Extractor initialized")

    def _load_spacy_models(self):
        """Load spaCy models if available"""
        try:
            import spacy

            self.nlp_en = spacy.load("en_core_web_sm")
            self.nlp_zh = (
                spacy.load("zh_core_web_sm")
                if self._model_exists("zh_core_web_sm")
                else None
            )
            self.logger.info("spaCy models loaded successfully")
        except (ImportError, OSError) as e:
            self.logger.warning(
                "spaCy models not available, using pattern-based extraction: %s", str(e)
            )

    def _model_exists(self, model_name: str) -> bool:
        """Check if spaCy model exists"""
        try:
            import spacy

            spacy.load(model_name)
            return True
        except OSError:
            return False

    def _build_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for information extraction"""
        return {
            # Name patterns
            "name_introductions": [
                r"(?:my name is|i'm|i am|call me)\s+([a-zA-Z]+)",
                r"(?:this is|here is)\s+([a-zA-Z]+)(?:\s+speaking)?",
                r"([a-zA-Z]+)\s+(?:here|speaking)",
            ],
            # Product interests
            "product_mentions": {
                "toys": [r"\b(toy|toys|doll|dolls|game|games|puzzle|puzzles)\b"],
                "gifts": [r"\b(gift|gifts|present|presents)\b"],
                "books": [r"\b(book|books|educational|learning)\b"],
                "electronics": [r"\b(electronic|electronics|gadget|gadgets)\b"],
            },
            # Order references
            "order_patterns": [
                r"order\s+(?:#|number|no.\?)\s*(\w+)",
                r"order\s+(\w{4,})",
                r"my order\s+(\w+)",
            ],
            # Contact information
            "email_patterns": [r"\b[A-Za-z0-9._%+-]+[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"],
            "phone_patterns": [
                r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
                r"\(\d{3}\)\s*\d{3}[-.\s]?\d{4}",
            ],
            # Emotional Indicators
            "positive_emotions": [
                r"\b(happy|excited|love|great|awesome|amazing|perfect|wonderful)\b",
                r"\b(thank you|thanks|appreciate)\b",
            ],
            "negative_emotions": [
                r"\b(frustrated|angry|disappointed|upset|annoyed|terrible|awful)\b",
                r"\b(problem|issue|complain|complaint|wrong|error)\b",
            ],
            # Urgency indicators
            "urgency_patterns": [
                r"\b(urgent|asap|immediately|quickly|rush|emergency)\b",
                r"\b(need.{0,10}(now|today|right away))\b",
            ],
        }

    def extract_user_information(
        self, message: str, language: str = "en"
    ) -> Dict[str, Any]:
        """Extract comprehensive user information from a message"""

        message_lower = message.lower()
        extracted_info = {
            "personal_info": {},
            "interests": [],
            "contact_info": {},
            "emotional_state": {},
            "entities": {},
            "topics": [],
            "urgency_level": "normal",
        }

        # Extract personal information
        extracted_info["personal_info"] = self._extract_personal_info(message_lower)

        # Extract product interests
        extracted_info["interests"] = self._extract_interests(message_lower)

        # Extract contact information
        extracted_info["contact_info"] = self._extract_contact_info(message_lower)

        # Analyze emotional state
        extracted_info["emotional_state"] = self._analyze_emotional_state(message_lower)

        # Extract entities using spaCy (if available)
        extracted_info["entities"] = self._extract_entities_spacy(message, language)

        # Identify conversation topics
        extracted_info["topics"] = self._identify_topics(message_lower)

        # Assess urgency level
        extracted_info["urgency_level"] = self._assess_urgency(message_lower)

        # Log extraction results
        if any(extracted_info.values()):
            self.logger.debug("Extracted information: %s", extracted_info)

        return extracted_info

    def _extract_personal_info(self, message: str) -> Dict[str, str]:
        """Extract personal information  like names"""
        personal_info = {}

        # Extract names
        for pattern in self.patterns["name_introductions"]:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                # Take the first match and capitalize properly
                name = matches[0].strip().title()
                if len(name) > 1 and name.isalpha():  # Basic validation
                    personal_info["name"] = name
                    break

        return personal_info

    def _extract_interests(self, message: str) -> List[str]:
        """Extract product interests and preferences"""
        interests = []

        for category, patterns in self.patterns["product_mentions"].items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    category_name = category.split("_", maxsplit=1)[
                        0
                    ]  # "product_x_y" -> "product", "x_y" -> "product"
                    if category_name not in interests:
                        interests.append(category_name)

        # Alternative approach - direct pattern matching
        product_categories = {
            "toys": r"\b(toy|toys|doll|dolls|action figure|puzzle|game)\b",
            "gifts": r"\b(gift|gifts|present|presents)\b",
            "books": r"\b(book|books|reading|educational)\b",
            "electronics": r"\b(electronics|electronics|gadget|tablet|phone)\b",
        }

        for category, pattern in product_categories.items():
            if re.search(pattern, message, re.IGNORECASE):
                if category not in interests:
                    interests.append(category)

        return interests

    def _extract_contact_info(self, message: str) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {}

        # Extract email addresses
        for pattern in self.patterns["email_patterns"]:
            matches = re.findall(pattern, message)
            if matches:
                contact_info["email"] = matches[0]
                break

        # Extract phone numbers
        for pattern in self.patterns["phone_patterns"]:
            matches = re.findall(pattern, message)
            if matches:
                contact_info["phone"] = matches[0]
                break

        return contact_info

    def _analyze_emotional_state(self, message: str) -> Dict[str, Any]:
        """Analyze user's emotional state"""
        emotional_state = {
            "sentiment": "neutral",
            "emotions": [],
            "confidence": 0.5,
        }

        positive_count = 0
        negative_count = 0

        # Check for positive emotions
        for pattern in self.patterns["positive_emotions"]:
            matches = re.findall(pattern, message)
            if matches:
                positive_count += len(matches)
                emotional_state["emotions"].extend(matches)

        # Check for negative emotions
        for pattern in self.patterns["negative_emotions"]:
            matches = re.findall(pattern, message)
            if matches:
                negative_count += len(matches)
                emotional_state["emotions"].extend(matches)

        # Determine overall sentiment
        if positive_count > negative_count:
            emotional_state["sentiment"] = "positive"
            emotional_state["confidence"] = min(0.9, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            emotional_state["sentiment"] = "negative"
            emotional_state["confidence"] = min(0.9, 0.5 + (negative_count * 0.1))

        return emotional_state

    def _extract_entities_spacy(
        self, message: str, language: str
    ) -> Dict[str, List[str]]:
        """Extract entities using spaCy (if available)"""
        entities = {}

        if language == "zh" and self.nlp_zh:
            nlp = self.nlp_zh
        elif self.nlp_en:
            nlp = self.nlp_en
        else:
            return entities  # Return empty if no spaCy models

        try:
            doc = nlp(message)
            for ent in doc.ents:
                entity_type = ent.label_.lower()
                entity_text = ent.text.strip()

                if entity_type not in entities:
                    entities[entity_type] = []

                if entity_text not in entities[entity_type]:
                    entities[entity_type].append(entity_text)

        except Exception as e:
            self.logger.warning("spaCy entity extraction failed: %s", str(e))

        return entities

    def _identify_topics(self, message: str) -> List[str]:
        """Identify conversation topics"""
        topics = []

        topic_keywords = {
            "order_management": r"\b(order|purchase|buy|bought|cancel|return|refund)\b",
            "product_inquiry": r"\b(product|item|toy|gift|available|stock|price|cost)\b",
            "shipping": r"\b(ship|shipping|delivery|delivered|track|tracking)\b",
            "support": r"\b(help|support|problem|issue|question|assist)\b",
            "account": r"\b(account|profile|login|password|register|sign up)\b",
        }

        for topic, pattern in topic_keywords.items():
            if re.search(pattern, message, re.IGNORECASE):
                topics.append(topic)

        return topics

    def _assess_urgency(self, message: str) -> str:
        """Assess the urgency level of the massage"""
        urgency_score = 0

        for pattern in self.patterns["urgency_patterns"]:
            matches = re.findall(pattern, message, re.IGNORECASE)
            urgency_score += len(matches)

        if urgency_score >= 2:
            return "high"
        elif urgency_score >= 1:
            return "medium"
        else:
            return "normal"

    def extract_conversation_summary(self, messages: List[Dict]) -> Dict[str, Any]:
        """Extract summary information from a conversation"""
        if not messages:
            return {}

        summary = {
            "total_messages": len(messages),
            "topics_discussed": set(),
            "user_interests": set(),
            "emotional_journey": [],
            "key_information": {},
            "resolution_status": "unknown",
        }

        for msg in messages:
            user_input = msg.get("user_input", "")
            if user_input:
                # Extract information from each message
                info = self.extract_user_information(user_input)

                # Aggregate topics
                summary["topics_discussed"].update(info.get("topics", []))

                # Aggregate interests
                summary["user_interests"].update(info.get("interests", []))

                # Track emotional journey
                emotion = info.get("emotional_state", {}).get("sentiment", "neutral")
                summary["emotional_journey"].append(emotion)

                # Store key personal information
                personal_info = info.get("personal_info", {})
                if personal_info:
                    summary["key_information"].update(personal_info)

        # Convert sets to lists for JSON serialization
        summary["topics_discussed"] = list(summary["topics_discussed"])
        summary["user_interests"] = List(summary["user_interests"])

        return summary
