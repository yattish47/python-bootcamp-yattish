# Lesson 5.3 — AI Chat Endpoint: LangChain wired into FastAPI
# CONCEPT: Stateful AI conversations via session management in a REST API
# KOTLIN EQUIVALENT: @Service ChatService with a ConcurrentHashMap<String, List<Message>>
# PHP EQUIVALENT: Laravel controller with session/cache-backed conversation history

# ─── OVERVIEW ─────────────────────────────────────────────────────────────────
# Pattern:
#   POST /chat   → {message, session_id} → LLM call with history → {reply, session_id}
#   POST /reset  → {session_id} → clear that session's history → {cleared: true}
#   GET  /sessions → list all active session IDs

# Each session_id maps to a list of messages (ConversationBufferMemory equivalent).
# We store history in memory here. In production: Redis or a DB.

import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Load .env from week_05/ directory (parent of this file's expected location)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ─── OPTIONAL LANGCHAIN IMPORT ───────────────────────────────────────────────
# Wrapped in try/except so the file can be imported even without LangChain installed.
# In production: remove the try/except and require the dependency.

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("WARNING: langchain-openai not installed. Using mock responses.")

# ─── PYDANTIC MODELS ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """
    The body of POST /chat.
    session_id is optional — if not provided, a new session is created.

    Kotlin:  data class ChatRequest(val message: String, val sessionId: String?)
    Laravel: Form Request with nullable session_id
    """
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID (omit to start new session)")

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    message_count: int  # How many turns in this conversation

class ResetRequest(BaseModel):
    session_id: str

class SessionsResponse(BaseModel):
    sessions: list[str]
    total: int

# ─── SESSION STORE ────────────────────────────────────────────────────────────
# In-memory store: {session_id: [list of LangChain message objects]}
# Kotlin: ConcurrentHashMap<String, MutableList<BaseMessage>>
# Laravel: Cache::put("chat_session_{id}", $messages)

sessions: dict[str, list] = {}

def get_or_create_session(session_id: Optional[str]) -> tuple[str, list]:
    """Return (session_id, history_list). Creates a new session if needed."""
    if not session_id or session_id not in sessions:
        new_id = session_id or str(uuid.uuid4())
        sessions[new_id] = []
        return new_id, sessions[new_id]
    return session_id, sessions[session_id]

# ─── LLM SETUP ────────────────────────────────────────────────────────────────
# Initialized once at startup via lifespan, reused across all requests.
# Kotlin: @Bean fun chatModel(): ChatOpenAI = ChatOpenAI(...)
# Laravel: singleton in AppServiceProvider

llm: "ChatOpenAI | None" = None
chain = None

SYSTEM_PROMPT = (
    "You are a helpful assistant. Be concise and clear. "
    "If you don't know something, say so."
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm, chain
    if LANGCHAIN_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=1024,
        )
        print("LLM initialized: gpt-4o-mini")
    else:
        print("WARNING: Running in mock mode (no OPENAI_API_KEY or langchain not installed)")
    yield
    llm = None

app = FastAPI(title="AI Chat API", version="1.0.0", lifespan=lifespan)

# ─── CHAT LOGIC ───────────────────────────────────────────────────────────────

async def _mock_reply(message: str) -> str:
    """Fallback when LLM is not configured."""
    return f"[MOCK] You said: '{message}'. (Set OPENAI_API_KEY to get real responses.)"

async def _llm_reply(message: str, history: list) -> str:
    """
    Build message list and invoke LLM.

    LangChain message types:
        SystemMessage — sets the AI persona/instructions
        HumanMessage  — user's message
        AIMessage     — assistant's previous replies

    Kotlin equivalent:
        val messages = listOf(SystemMessage(prompt)) + history + listOf(HumanMessage(message))
        val response = chatClient.call(messages)
    """
    if llm is None:
        return await _mock_reply(message)

    # Build the full message list: system prompt + history + new message
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(history)
    messages.append(HumanMessage(content=message))

    response = await llm.ainvoke(messages)
    return response.content

# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(req: ChatRequest):
    """
    Send a message and get an AI reply.

    The session_id tracks conversation history.
    Omit it to start a new conversation.
    Pass the same session_id to continue a conversation.

    Example:
        POST /chat
        {"message": "What is Python?"}
        → {"reply": "Python is...", "session_id": "abc-123", "message_count": 1}

        POST /chat
        {"message": "Give me an example", "session_id": "abc-123"}
        → {"reply": "Here is an example...", "session_id": "abc-123", "message_count": 2}
    """
    session_id, history = get_or_create_session(req.session_id)

    # Get reply from LLM (or mock)
    reply = await _llm_reply(req.message, history)

    # Store this turn in history
    if LANGCHAIN_AVAILABLE:
        history.append(HumanMessage(content=req.message))
        history.append(AIMessage(content=reply))
    else:
        # Simple dict fallback when LangChain not installed
        history.append({"role": "user", "content": req.message})
        history.append({"role": "assistant", "content": reply})

    # Count turns (2 messages per turn)
    turn_count = len(history) // 2

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        message_count=turn_count,
    )

@app.post("/reset", tags=["Chat"])
def reset_session(req: ResetRequest):
    """
    Clear a session's history.

    Useful when a user starts a new topic and wants to forget the previous conversation.

    Kotlin: sessionsMap.remove(sessionId)
    Laravel: Cache::forget("chat_session_{$sessionId}")
    """
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found")

    message_count = len(sessions[req.session_id]) // 2
    del sessions[req.session_id]
    return {
        "cleared": True,
        "session_id": req.session_id,
        "messages_deleted": message_count,
    }

@app.get("/sessions", response_model=SessionsResponse, tags=["Chat"])
def list_sessions():
    """
    List all active session IDs.

    In production: add authentication — users should only see their own sessions.
    """
    return SessionsResponse(
        sessions=list(sessions.keys()),
        total=len(sessions),
    )

@app.get("/sessions/{session_id}", tags=["Chat"])
def get_session_info(session_id: str):
    """Inspect a session's conversation history (for debugging)."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    history = sessions[session_id]

    # Format history for display
    formatted = []
    for msg in history:
        if LANGCHAIN_AVAILABLE:
            if isinstance(msg, HumanMessage):
                formatted.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted.append({"role": "assistant", "content": msg.content})
        else:
            formatted.append(msg)

    return {
        "session_id": session_id,
        "turn_count": len(history) // 2,
        "history": formatted,
    }

@app.get("/health", tags=["Meta"])
def health():
    return {
        "status": "ok",
        "llm_ready": llm is not None,
        "active_sessions": len(sessions),
    }

# ─── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lesson_5_3_ai_endpoint:app", host="0.0.0.0", port=8002, reload=True)

# ─── EXERCISES ────────────────────────────────────────────────────────────────
# EXERCISE 1:
#   Add a GET /sessions/{session_id}/summary endpoint that asks the LLM to
#   summarize the conversation so far. If the session has fewer than 2 turns,
#   return {"summary": "Conversation too short to summarize"}.
#
# EXERCISE 2:
#   Add a `max_history: int = 10` setting. Before calling the LLM, trim the
#   history list so it only keeps the last `max_history` messages (to avoid
#   token overflow on long conversations).
#   Hint: trimmed = history[-max_history:] if len(history) > max_history else history
#
# EXERCISE 3:
#   Add a `system_prompt: Optional[str]` field to ChatRequest.
#   If provided, use it instead of the default SYSTEM_PROMPT for that session.
#   Store the custom system prompt in the session data so it persists across turns.
#   Hint: change sessions to store {"history": [], "system_prompt": "..."} per session.
