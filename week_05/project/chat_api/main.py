"""
Week 5 Project — Complete FastAPI AI Chat Backend
==================================================
Endpoints:
    POST   /chat               — Chat with session history
    POST   /chat/stream        — Same but streams tokens as SSE
    DELETE /session/{id}       — Clear a session
    GET    /sessions           — List active session IDs
    GET    /health             — Health check

Setup:
    1. Create week_05/.env with OPENAI_API_KEY=sk-...
    2. pip install fastapi uvicorn langchain langchain-openai python-dotenv httpx
    3. uvicorn project.chat_api.main:app --reload  (from week_05/)
       OR: python project/chat_api/main.py

Kotlin equivalent:
    @SpringBootApplication + @RestController with @Autowired ChatService
    Streaming: Spring WebFlux Flux<String> with text/event-stream

Laravel equivalent:
    Route::post('/chat', [ChatController::class, 'chat'])
    Session history in Redis via Cache::put()
"""

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Load .env from week_05/ directory (two levels up from this file)
_env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(_env_path)

# ─── LangChain imports (with graceful fallback) ───────────────────────────────

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# ─── PYDANTIC MODELS ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = Field(None, description="Omit to start a new session")

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tokens: int  # Approximate word count (real token count needs tiktoken)

class StreamChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None

# ─── GLOBAL STATE ─────────────────────────────────────────────────────────────

llm: "ChatOpenAI | None" = None
chain_with_history = None

# Session store: {session_id: InMemoryChatMessageHistory}
# In production: replace with Redis-backed history
session_histories: dict[str, "InMemoryChatMessageHistory"] = {}

# Fallback sessions for mock mode (when LangChain not available)
mock_sessions: dict[str, list] = {}

SYSTEM_PROMPT = (
    "You are a helpful, knowledgeable assistant. "
    "Provide clear, accurate answers. "
    "If you don't know something, say so honestly."
)

# ─── LIFESPAN ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm, chain_with_history

    api_key = os.getenv("OPENAI_API_KEY")

    if LANGCHAIN_AVAILABLE and api_key:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, streaming=True)

        # Build a prompt that includes chat history
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])

        # Chain: prompt → LLM → string output
        base_chain = prompt | llm | StrOutputParser()

        # Wrap with message history management
        chain_with_history = RunnableWithMessageHistory(
            base_chain,
            get_session_history=_get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        print("Chat API ready with LangChain + OpenAI")
    else:
        reason = "langchain-openai not installed" if not LANGCHAIN_AVAILABLE else "OPENAI_API_KEY not set"
        print(f"Chat API running in MOCK MODE: {reason}")

    yield

    # Cleanup
    llm = None
    chain_with_history = None
    session_histories.clear()
    mock_sessions.clear()

app = FastAPI(
    title="AI Chat API",
    description="FastAPI + LangChain chat backend with streaming support",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── SESSION HISTORY HELPERS ──────────────────────────────────────────────────

def _get_session_history(session_id: str) -> "InMemoryChatMessageHistory":
    """
    Called by RunnableWithMessageHistory to get/create history for a session.
    Kotlin: sessionsMap.computeIfAbsent(sessionId) { InMemoryChatMessageHistory() }
    Laravel: Cache::rememberForever("session_{$id}", fn() => new ChatHistory())
    """
    if session_id not in session_histories:
        session_histories[session_id] = InMemoryChatMessageHistory()
    return session_histories[session_id]

def _ensure_session(session_id: Optional[str]) -> str:
    """Return existing session_id or generate a new one."""
    if not session_id:
        return str(uuid.uuid4())
    return session_id

# ─── POST /chat ───────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(req: ChatRequest):
    """
    Chat with the AI. Pass session_id to continue a conversation.

    Example:
        POST /chat  {"message": "What is FastAPI?"}
        → {"reply": "FastAPI is...", "session_id": "abc-123", "tokens": 42}

        POST /chat  {"message": "Give a code example", "session_id": "abc-123"}
        → {"reply": "Here is an example...", "session_id": "abc-123", "tokens": 85}
    """
    session_id = _ensure_session(req.session_id)

    if chain_with_history is not None:
        # LangChain path — RunnableWithMessageHistory handles history automatically
        config = {"configurable": {"session_id": session_id}}
        reply = await chain_with_history.ainvoke({"input": req.message}, config=config)
    else:
        # Mock path
        reply = _mock_reply(req.message)
        # Track mock session manually
        if session_id not in mock_sessions:
            mock_sessions[session_id] = []
        mock_sessions[session_id].append({"user": req.message, "ai": reply})

    tokens = len(reply.split())  # Approximate; use tiktoken for accurate count
    return ChatResponse(reply=reply, session_id=session_id, tokens=tokens)

# ─── POST /chat/stream ────────────────────────────────────────────────────────

@app.post("/chat/stream", tags=["Chat"])
async def chat_stream(req: StreamChatRequest):
    """
    Stream AI response as Server-Sent Events.

    SSE format:
        event: token
        data: {"token": "Hello"}

        event: token
        data: {"token": " world"}

        event: done
        data: [DONE]

    Test with curl:
        curl -N -X POST http://localhost:8000/chat/stream \\
             -H "Content-Type: application/json" \\
             -d '{"message": "Explain Python generators"}'

    Kotlin: Flux<String> with text/event-stream media type (Spring WebFlux)
    Laravel: response()->stream() with flush() after each token
    """
    session_id = _ensure_session(req.session_id)

    async def generate():
        if chain_with_history is not None:
            yield _sse({"session_id": session_id}, event="init")

            full_reply = []
            config = {"configurable": {"session_id": session_id}}

            # Build messages manually for streaming (chain_with_history doesn't expose astream cleanly)
            history = _get_session_history(session_id)
            messages = [SystemMessage(content=SYSTEM_PROMPT)]
            messages.extend(history.messages)
            messages.append(HumanMessage(content=req.message))

            async for chunk in llm.astream(messages):
                token = chunk.content
                if token:
                    full_reply.append(token)
                    yield _sse({"token": token}, event="token")

            # Save to history
            full_text = "".join(full_reply)
            history.add_user_message(req.message)
            history.add_ai_message(full_text)

            yield _sse({"tokens": len(full_text.split()), "session_id": session_id}, event="complete")
        else:
            # Mock streaming
            yield _sse({"session_id": session_id}, event="init")
            words = _mock_reply(req.message).split()
            for word in words:
                yield _sse({"token": word + " "}, event="token")
                await asyncio.sleep(0.05)
            yield _sse({"tokens": len(words), "session_id": session_id}, event="complete")

        yield f"event: done\ndata: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

def _sse(data: dict, event: str = "message") -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

# ─── DELETE /session/{session_id} ────────────────────────────────────────────

@app.delete("/session/{session_id}", tags=["Sessions"])
def delete_session(session_id: str):
    """
    Clear a session's conversation history.

    Kotlin: sessionsMap.remove(sessionId)
    Laravel: Cache::forget("session_{$sessionId}")
    """
    deleted = False
    if session_id in session_histories:
        del session_histories[session_id]
        deleted = True
    if session_id in mock_sessions:
        del mock_sessions[session_id]
        deleted = True

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    return {"deleted": True, "session_id": session_id}

# ─── GET /sessions ────────────────────────────────────────────────────────────

@app.get("/sessions", tags=["Sessions"])
def list_sessions():
    """List all active session IDs."""
    all_ids = list(set(list(session_histories.keys()) + list(mock_sessions.keys())))
    return {"sessions": all_ids, "total": len(all_ids)}

# ─── GET /health ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Meta"])
def health():
    return {
        "status": "ok",
        "mode": "live" if chain_with_history is not None else "mock",
        "llm": "gpt-4o-mini" if llm is not None else None,
        "active_sessions": len(session_histories) + len(mock_sessions),
    }

# ─── ROOT ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Meta"])
def root():
    return {
        "name": "AI Chat API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "POST /chat",
            "POST /chat/stream",
            "DELETE /session/{id}",
            "GET /sessions",
            "GET /health",
        ],
    }

# ─── MOCK HELPER ──────────────────────────────────────────────────────────────

def _mock_reply(message: str) -> str:
    return (
        f"[MOCK MODE] You asked: '{message}'. "
        "To get real AI responses, set OPENAI_API_KEY in week_05/.env "
        "and install langchain-openai."
    )

# ─── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("Starting Chat API on http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    uvicorn.run(
        "project.chat_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
