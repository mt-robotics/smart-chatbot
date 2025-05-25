from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from .models.nlp_engine import NLPEngine
from .models.conversation_manager import ConversationManager
from .data.training_data import TRAINING_DATA

app = FastAPI(title="Smart Customer Service Chatbot")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend URL
        "http://127.0.0.1:5500",  # Frontend URL
        "https://*.railway.app",  # For Railway.app
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
nlp_engine = NLPEngine()
conversation_manager = ConversationManager()


# Train the mode on startup
@app.on_event("startup")
async def startup_event():
    nlp_engine.train_intent_classifier(TRAINING_DATA)


class ChatRequest(BaseModel):
    message: str
    session_id: str = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    confidence: float
    entities: dict


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())

    # Detect language
    language = nlp_engine.detect_language(request.message)

    # Process message
    intent, confidence = nlp_engine.classify_intent(request.message)
    entities = nlp_engine.extract_entities(request.message, language)

    # Generate response
    response = conversation_manager.get_response(intent, language, entities)

    # Save conversation
    conversation_manager.save_conversation(
        session_id, request.message, response, intent
    )

    return ChatResponse(
        response=response,
        session_id=session_id,
        intent=intent,
        confidence=confidence,
        entities=entities,
    )


@app.get("/analytics/{session_id}")
async def get_conversation_history(session_id: str):
    if session_id in conversation_manager.conversations:
        return conversation_manager.conversations[session_id]
    raise HTTPException(status_code=404, detail="Session not found")
