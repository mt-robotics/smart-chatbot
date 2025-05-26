import json
from datetime import datetime
from typing import Dict, List
from ..utils.config import get_logger


class ConversationManager:
    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)
        self.conversations = {}
        self.responses = self.load_responses()

        max_history = config.MAX_CONVERSATION_HISTORY if config else 50
        self.logger.info(
            "Conversation Manager initialized with max history: %d", max_history
        )

    def load_responses(self):
        return {
            "order_status": {
                "en": "I'll help you check your order status. Please provide your order number.",
                "zh": "我来帮您查询订单状态。请提供订单号。",
            },
            "cancel_order": {
                "en": "I understand you want to cancel an order. Please provide your order number so I can help you.",
                "zh": "我理解您想取消订单。请提供订单号，我来帮您处理。",
            },
            "product_inquiry": {
                "en": "I'd love to help you find the perfect product! What are you looking for? Toys or gifts?",
                "zh": "我很乐意帮您找到合适的产品！您在寻找什么？玩具还是礼品？",
            },
            "greeting": {
                "en": "Hello! How can I help you today?",
                "zh": "您好！今天我能为您做些什么？",
            },
            "goodbye": {
                "en": "Thank you for contacting us. Have a great day!",
                "zh": "感谢您联系我们，祝您愉快！",
            },
            "fallback": {
                "en": "I'm not sure I understand. Could you please rephrase your question?",
                "zh": "我不太理解您的意思，能否换个方式表达？",
            },
        }

    def get_response(self, intent: str, language: str, entities: Dict = None):
        if intent in self.responses:
            base_response = self.responses[intent][language]

            # Customize response based on entities
            if entities and "order_number" in entities:
                if intent == "order_status":
                    if language == "en":
                        base_response = (
                            f"Let me check order #{entities['order_number']} for you."
                        )
                    else:
                        base_response = (
                            f"让我为您查询订单 #{entities['order_number']}。"
                        )

            return base_response

        return self.responses["fallback"][language]

    def save_conversation(
        self, session_id: str, user_input: str, bot_response: str, intent: str
    ):
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            self.logger.info("New conversation session created: %s", session_id)

        self.conversations[session_id].append(
            {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "bot_response": bot_response,
                "intent": intent,
            }
        )

        # Limit conversation history
        max_history = self.config.MAX_CONVERSATION_HISTORY if self.config else 50
        if len(self.conversations[session_id]) > max_history:
            self.conversations[session_id] = self.conversations[session_id][
                -max_history:
            ]
            self.logger.debug("Conversation history trimmed for session %s", session_id)

        self.logger.debug("Conversation saved for session %s", {session_id})
