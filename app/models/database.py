# app/models/database.py
import os
from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID

# Absolute import from project root
from app.utils.config import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, index=True)
    preferred_language = Column(String(10), default="en")
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_messages = Column(Integer, default=0)

    # Relationships
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    preferences = relationship(
        "UserPreference", back_populates="user", cascade="all, delete-orphan"
    )
    insights = relationship(
        "UserInsight", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<User(session_id={self.session_id}, language={self.preferred_language})>"
        )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_message_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    message_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Relationship
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    topics = relationship(
        "ConversationTopic", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, messages={self.message_count})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )

    # Message content
    user_input = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)

    # NLP analysis
    detected_language = Column(String(10))
    intent = Column(String(100))
    confidence = Column(Float)
    entities = Column(Text)  # JSON string

    # Metadata
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    response_time_ms = Column(Integer)  # How long the bot took to respond

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, intent={self.intent}, confidence={self.confidence})>"


class Database:
    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        # Create engine
        self.engine = create_engine(
            self.database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,  # Recycle connections every 5 minutes
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        logger.info(
            "Database manager initialized with URL: %s",
            self.database_url.split("@")[0] + "@***",
        )

    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()

    def health_check(self):
        """Check if database connection is working"""
        try:
            with self.get_session() as session:
                from sqlalchemy import text

                session.execute(text("SELECT 1"))
            logger.info("Database health check passed")
            return True
        except Exception as e:
            logger.error("Database health check failed: %s", str(e))
            return False


class DatabaseManager:
    """Singleton database manager"""

    def __init__(self):
        self.db = None

    def get_database(self) -> Database:
        """Get the database instance (create if doesn't exist)"""
        if self.db is None:
            self.db = Database()
        return self.db

    def init_database(self):
        """Initialize the database instance and create tables"""
        db = self.get_database()
        db.create_tables()
        return db


# Create single instance of DatabaseManager
db_manager = DatabaseManager()


# Convenience functions for easier imports
def get_database() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager.get_database()


def init_database():
    """Initialize the global database manager instance and create tables"""
    return db_manager.init_database()
