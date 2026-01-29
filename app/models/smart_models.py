from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Float,
    Integer,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

# Absolute import from project root
from app.models.database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Preference details
    preference_type = Column(
        String(50), nullable=False
    )  # e.g., "name", "product_interest", "communication_style"
    preference_key = Column(
        String(100), nullable=False
    )  # e.g., "user_name", "preferred_products", "formality_level"
    preference_value = Column(
        Text, nullable=False
    )  # e.g., "John", "toys,gifts", "casual"

    # Learning metadata
    confidence_score = Column(
        Float, default=1.0
    )  # How confident the model is (0.0-1.0)
    learned_from_messages = Column(
        Integer, default=1
    )  # Number of messages that taught us this
    first_learned = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(id={self.id} user_id={self.user_id} {self.preference_key}={self.preference_value})>"


class ConversationTopic(Base):
    __tablename__ = "conversation_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )

    # Topic details
    topic = Column(
        String(100), nullable=False
    )  # "product_inquiry", "order_management", "support"
    subtopic = Column(String(100))  # "toys", "cancellation", "shipping_issue"
    keywords = Column(Text)  # JSON list of relevant keywords

    # Topic metadata
    first_mentioned = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    message_count = Column(Integer, default=1)  # How many messages discussed this topic
    importance_score = Column(
        Float, default=1.0
    )  # How important this topic was (0.0-1.0)

    # Relationships
    conversation = relationship("Conversation", back_populates="topics")

    def __repr__(self):
        return f"<ConversationTopic(topic={self.topic}, subtopic={self.subtopic})>"


class UserInsight(Base):
    __tablename__ = "user_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Insight details
    insight_type = Column(
        String(50), nullable=False
    )  # "behavior_pattern", "preference_trend", "interaction_style"
    insight_key = Column(
        String(100), nullable=False
    )  # "most_active_time", "preferred_topics", "question_complexity"
    insight_value = Column(Text, nullable=False)  # "morning", "toys,gifts", "simple"
    insight_description = Column(Text)  # Human-readable explanation

    # Analytics metadata
    confidence_level = Column(Float, default=1.0)  # Statistical confidence (0.0-1.0)
    based_on_messages = Column(Integer, default=0)  # Number of messages analyzed
    last_calculated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)  # Is this insight still relevant?

    # Relationships
    user = relationship("User", back_populates="insights")

    def __repr__(self):
        return f"<UserInsight(id={self.id} user_id={self.user_id}, {self.insight_key}={self.insight_value})>"
