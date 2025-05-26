# app/main.py
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .utils.config import get_config, get_logger
from .models.nlp_engine import NLPEngine
from .models.conversation_manager import ConversationManager
from .data.training_data import TRAINING_DATA

# Load configuration (this sets up logging automatically)
config = get_config()
logger = get_logger(__name__)

app = FastAPI(
    title=config.API_TITLE,
    debug=config.API_DEBUG,
)

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


# Train the mode on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")
    logger.info("CORS origins configured: %s", config.CORS_ORIGINS)
    nlp_engine.train_intent_classifier(TRAINING_DATA)
    logger.info("NLP model training completed")
    logger.info("Application started successfully in %s mode", config.ENVIRONMENT)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")


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
    }


@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    return {
        "status": "healthy",
        "environment": config.ENVIRONMENT,
        "version": "1.0.0",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.debug("Chat request received: %s ...", request.message[:50])

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

        # Generate response
        response = conversation_manager.get_response(intent, language, entities)

        # Save conversation
        conversation_manager.save_conversation(
            session_id, request.message, response, intent
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
            }

        logger.info("Chat response generated successfully for session %s", session_id)
        return chat_response

    except Exception as e:
        logger.error("Error processing chat request: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/analytics/{session_id}")
async def get_conversation_history(session_id: str):
    logger.debug("Analytics requested for session: %s", session_id)

    if session_id in conversation_manager.conversations:
        logger.info("Conversation history found for session %s", session_id)
        return conversation_manager.conversations[session_id]

    logger.warning("No conversation history found for session %s", session_id)
    raise HTTPException(status_code=404, detail="Session not found")
