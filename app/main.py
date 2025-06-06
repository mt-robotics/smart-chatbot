# app/main.py
# pylint: disable=unused-import
import uuid
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .utils.config import get_config, get_logger
from .models.nlp_engine import NLPEngine
from .models.conversation_manager import ConversationManager
from .models.database import init_database, get_database, User, Conversation, Message
from .models.smart_models import UserPreference, UserInsight, ConversationTopic
from .data.training_data import TRAINING_DATA

# Load configuration (this sets up logging automatically)
config = get_config()
logger = get_logger(__name__)


# Train the mode on startup
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):  # pylint: disable=unused-argument
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("Starting application..")
    logger.info("CORS origins configured: %s", config.CORS_ORIGINS)

    # Initialize database
    try:
        db = init_database()
        if db.health_check():
            logger.info("Database connection established successfully")
        else:
            logger.warning("Database health check failed, but continuing...")
    except Exception as e:
        logger.error("Database initialization failed: %s", str(e))
        logger.warning("Continuing without database - some features may not work...")

    # Train NLP model
    nlp_engine.train_intent_classifier(TRAINING_DATA)
    logger.info("NLP model training completed")
    logger.info("Application started successfully in %s mode", config.ENVIRONMENT)

    yield  # App runs here

    # Shutdown (if needed)
    logger.info("Application shutting down...")


app = FastAPI(title=config.API_TITLE, debug=config.API_DEBUG, lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
nlp_engine = NLPEngine(config)
conversation_manager = ConversationManager(config)

# Request logging middleware
if config.ENABLE_REQUEST_LOGGING:

    @app.middleware("http")
    async def log_requests(request, call_next):
        logger.info("Request: %s %s", request.method, request.url)
        response = await call_next(request)
        logger.info("Response: %s", response.status_code)
        return response


class ChatRequest(BaseModel):
    message: str
    session_id: str = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    confidence: float
    entities: dict
    debug_info: dict = None


@app.get("/")
async def root():
    logger.debug("Root endpoint accessed")
    return {
        "message": config.API_TITLE,
        "environment": config.ENVIRONMENT,
        "docs": "/docs",
        "database": "connected" if get_database().health_check() else "disconnected",
    }


@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")

    # Check database health
    db_status = "healthy" if get_database().health_check() else "unhealthy"

    return {
        "status": "healthy",
        "environment": config.ENVIRONMENT,
        "version": "2.0.0",  # Updated version with database
        "database": db_status,
        "components": {
            "nlp_engine": "ready",
            "conversation_manager": "ready",
            "database": db_status,
        },
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.debug("Chat request received: %s ...", request.message[:50])
    start_time = time.time()

    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Detect language
        language = nlp_engine.detect_language(request.message)

        # Process message
        intent, confidence = nlp_engine.classify_intent(request.message)
        entities = nlp_engine.extract_entities(request.message, language)

        # Convert NumPy types to Python types
        intent = str(intent)
        confidence = float(confidence)

        logger.debug(
            "Processed - Language: %s, Intent: %s, Confidence: %.2f",
            language,
            intent,
            confidence,
        )

        # Apply confidence threshold
        if confidence < config.CONFIDENCE_THRESHOLD:
            logger.info(
                "Low confidence (%.2f}) for intent %s, using fallback",
                confidence,
                intent,
            )
            intent = "low_confidence"

        # Generate response (now with context awareness)
        response = conversation_manager.get_response(
            intent, language, session_id, entities
        )

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Save conversation (now to database)
        conversation_manager.save_conversation(
            session_id,
            request.message,
            response,
            intent,
            confidence,
            entities,
            language,
            response_time_ms,
        )

        # Prepare response
        chat_response = ChatResponse(
            response=response,
            session_id=session_id,
            intent=intent,
            confidence=confidence,
            entities=entities,
        )

        # Add debug info if enabled
        if config.ENABLE_DEBUG_INFO:
            chat_response.debug_info = {
                "language": language,
                "original_confidence": confidence,
                "threshold_applied": confidence < config.CONFIDENCE_THRESHOLD,
                "environment": config.ENVIRONMENT,
                "response_time_ms": response_time_ms,
                "database_enabled": get_database().health_check(),
            }

        logger.info("Chat response generated successfully for session %s", session_id)
        return chat_response

    except Exception as e:
        logger.error("Error processing chat request: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.get("/analytics/{session_id}")
async def get_conversation_history(session_id: str):
    logger.debug("Analytics requested for session: %s", session_id)

    try:
        history = conversation_manager.get_conversation_history(session_id)
        if history:
            logger.info("Conversation history found for session %s", session_id)
            return {
                "session_id": session_id,
                "message_count": len(history),
                "messages": history,
            }
        else:
            logger.warning("No conversation history found for session %s", session_id)
            raise HTTPException(status_code=404, detail="Session not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving conversation history: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.get("/analytics/{session_id}/stats")
async def get_user_stats(session_id: str):
    logger.debug("User stats requested for session: %s", session_id)

    try:
        stats = conversation_manager.get_user_stats(session_id)
        if stats:
            logger.info("User stats found for session %s", session_id)
            return stats
        else:
            logger.warning("No user stats found for session %s", session_id)
            raise HTTPException(status_code=404, detail="Session not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving user stats: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e
