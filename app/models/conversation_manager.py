import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from ..utils.config import get_logger
from .database import get_database, User, Conversation, Message


class ConversationManager:
    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)
        # self.conversations = {}
        self.db = get_database()
        self.responses = self.load_responses()

        max_history = config.MAX_CONVERSATION_HISTORY if config else 50
        self.logger.info(
            # "Conversation Manager initialized with max history: %d",
            "Database-powered Conversation Manager initialized with max history: %d",
            max_history,
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

    def get_or_create_user(self, session_id: str) -> User:
        """Get existing user or create new one"""
        with self.db.get_session() as db_session:
            user = db_session.query(User).filter(User.session_id == session_id).first()

            if not user:
                user = User(session_id=session_id)
                db_session.add(user)
                db_session.commit()
                db_session.refresh(user)
                self.logger.info("New user created: %s", session_id)
            else:
                # Update last seen
                user.last_seen = datetime.now(timezone.utc)
                db_session.commit()

            return user

    def get_active_conversation(self, user: User) -> Optional[Conversation]:
        """Get the most recent active conversation for a user"""
        with self.db.get_session() as db_session:
            # Refresh user object in this session
            user = db_session.merge(user)

            conversation = (
                db_session.query(Conversation)
                .filter(Conversation.user_id == user.id, Conversation.is_active == True)
                .order_by(Conversation.last_message_at.desc())
                .first()
            )

            # If conversation is older than 30 minutes, consider it inactive
            if conversation and conversation.last_message_at:
                time_diff = datetime.now(timezone.utc) - conversation.last_message_at
                if time_diff > timedelta(minutes=30):
                    conversation.is_active = False
                    db_session.commit()
                    conversation = None

            return conversation

    def create_conversation(self, user: User) -> Conversation:
        """Create a new conversation for the user"""
        with self.db.get_session() as db_session:
            # Refresh user object in this session
            user = db_session.merge(user)

            conversation = Conversation(user_id=user.id)
            db_session.add(conversation)
            db_session.commit()
            db_session.refresh(conversation)

            self.logger.info("New conversation created for user %s", user.session_id)
            return conversation

    def get_conversation_context(
        self, conversation: Conversation, limit: int = 5
    ) -> List[Dict]:
        """Get recent messages from conversation for context"""
        with self.db.get_session() as db_session:
            # Refresh conversation object in this section
            conversation = db_session.merge(conversation)

            messages = (
                db_session.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .order_by(Message.timestamp.desc())
                .limit(limit)
                .all()
            )

            context = []
            for msg in reversed(messages):  # Reverse to get chronological order
                context.append(
                    {
                        "user_input": msg.user_input,
                        "bot_response": msg.bot_response,
                        "intent": msg.intent,
                        "timestamp": msg.timestamp.isoformat(),
                    }
                )
            return context

    def get_response(
        self, intent: str, language: str, session_id: str = None, entities: Dict = None
    ) -> str:
        """Generate response with context awareness"""

        # Get user and conversation for context
        context_info = ""
        if session_id:
            try:
                user = self.get_or_create_user(session_id)
                conversation = self.get_active_conversation(user)

                if conversation:
                    context = self.get_conversation_context(conversation, limit=3)
                    if context:
                        # Use context to enhance response (simple example)
                        last_intent = context[-1].get("intent")
                        if last_intent == "greeting" and intent == "product_inquiry":
                            if language == "en":
                                context_info = (
                                    "I see you're interested in our products!"
                                )
                            else:
                                context_info = "我看到您对我们产品感兴趣！"

                # Update user's preferred language
                if user and user.preferred_language != language:
                    with self.db.get_session() as db_session:
                        user = db_session.merge(user)
                        user.preferred_language = language
                        db_session.commit()

            except Exception as e:
                self.logger.warning("Could not get conversation context: %s", str(e))

        # Get base response
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

            return context_info + base_response

        return self.responses["fallback"][language]

    def save_conversation(
        self,
        session_id: str,
        user_input: str,
        bot_response: str,
        intent: str,
        confidence: float = None,
        entities: Dict = None,
        language: str = "en",
        response_time_ms: int = None,
    ):
        """Save conversation to database"""
        try:
            # Get or create user
            user = self.get_or_create_user(session_id)

            # Get or create active conversation
            conversation = self.get_active_conversation(user)
            if not conversation:
                conversation = self.create_conversation(user)

            # Create message record
            with self.db.get_session() as db_session:
                # Refresh objects in this session
                conversation = db_session.merge(conversation)
                user = db_session.merge(user)

                message = Message(
                    conversation_id=conversation.id,
                    user_input=user_input,
                    bot_response=bot_response,
                    detected_langauge=language,
                    intent=intent,
                    confidence=confidence,
                    entities=json.dumps(entities) if entities else None,
                    response_time_ms=response_time_ms,
                )

                db_session.add(message)

                # Update conversation stats
                conversation.last_message_at = datetime.now(timezone.utc)
                conversation.message_count += 1

                # Update user stats
                user.total_messages += 1
                user.last_seen = datetime.now(timezone.utc)

                db_session.commit()

            self.logger.debug("Conversation saved for session %s", session_id)

        except Exception as e:
            self.logger.error("Failed to save conversation: %s", str(e), exc_info=True)

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session (for analytics endpoint)"""
        try:
            with self.db.get_session() as db_session:
                user = (
                    db_session.query(User).filter(User.session_id == session_id).first()
                )
                if not user:
                    return []

            messages = (
                db_session.query(Message)
                .join(Conversation)
                .filter(Conversation.user_id == user.id)
                .order_by(Message.timestamp.desc())
                .limit(self.config.MAX_CONVERSATION_HISTORY if self.config else 50)
                .all()
            )

            history = []
            for msg in reversed(messages):  # Reverse for chronological order
                history.append(
                    {
                        "timestamp": msg.timestamp.isoformat(),
                        "user_input": msg.user_input,
                        "bot_response": msg.bot_response,
                        "intent": msg.intent,
                        "confidence": msg.confidence,
                        "language": msg.detected_language,
                        "entities": json.loads(msg.entities) if msg.entities else {},
                    }
                )

            return history

        except Exception as e:
            self.logger.error(
                "Failed to get conversation history: %s", str(e), exc_info=True
            )
            return []

    def get_user_stats(self, session_id: str) -> Dict:
        """Get user statistics"""
        try:
            with self.db.get_session() as db_session:
                user = (
                    db_session.query(User).filter(User.session_id == session_id).first()
                )
                if not user:
                    return {}

                # Get conversation count
                conversation_count = db_session.query(
                    func.count(Conversation.id)  # pylint: disable=not-callable
                    .select_from(Conversation)
                    .filter(Conversation.user_id == user.id)
                )

                return {
                    "session_id": user.session_id,
                    "preferred_language": user.preferred_language,
                    "first_seen": user.first_seen.isoformat(),
                    "last_seen": user.last_seen.isoformat(),
                    "total_messages": user.total_messages,
                    "total_conversations": conversation_count,
                }

        except Exception as e:
            self.logger.error("Failed to get user stats: %s", str(e), exc_info=True)
            return {}
