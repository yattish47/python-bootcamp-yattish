"""
FastAPI server for the ShopPy AI Customer Support Bot.

Endpoints:
  POST   /chat                  — Send a message, receive an AI reply
  DELETE /session/{session_id}  — Clear a session's conversation history
  GET    /sessions              — List all active session IDs
  GET    /health                — Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from agent.graph import create_agent

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ShopPy Customer Support API",
    description="AI-powered customer support bot for ShopPy e-commerce store.",
    version="1.0.0",
)

# Allow all origins for local development — lock this down in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Agent (created once at startup)
# ---------------------------------------------------------------------------

agent = create_agent()

# ---------------------------------------------------------------------------
# In-memory session store
# sessions maps session_id -> list of LangChain message objects
# In production, replace with Redis or a database.
# ---------------------------------------------------------------------------

sessions: dict[str, list] = {}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    session_id: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "What is your return policy?",
                "session_id": "user-abc-123",
            }
        }
    }


class ChatResponse(BaseModel):
    reply: str
    session_id: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Utility"])
def health_check():
    """Returns a simple health check response."""
    return {"status": "ok"}


@app.get("/sessions", tags=["Sessions"])
def list_sessions():
    """Return all active session IDs and their message counts."""
    return {
        "sessions": [
            {"session_id": sid, "message_count": len(msgs)}
            for sid, msgs in sessions.items()
        ]
    }


@app.delete("/session/{session_id}", tags=["Sessions"])
def clear_session(session_id: str):
    """
    Clear all conversation history for the given session ID.
    Useful when the customer wants to start a fresh conversation.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    del sessions[session_id]
    return {"status": "cleared", "session_id": session_id}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    """
    Send a message to the AI customer support agent and receive a reply.

    The session_id is used to maintain conversation memory across requests.
    The full history for that session is passed to the agent on each turn.
    """
    session_id = request.session_id
    user_message = request.message

    # Retrieve or initialise session history
    if session_id not in sessions:
        sessions[session_id] = []

    history = sessions[session_id]

    # Append the new user message
    history.append(HumanMessage(content=user_message))

    # Invoke the LangGraph agent with the full conversation history
    # The agent returns a dict with a "messages" key containing all messages
    # including tool calls; the last AIMessage is the final reply.
    result = agent.invoke({"messages": history})

    # Extract the final AI response (last message in the output)
    output_messages = result["messages"]
    ai_reply = output_messages[-1].content

    # Update session with the full message history returned by the agent
    # (this includes tool call messages, which preserves full context)
    sessions[session_id] = output_messages

    return ChatResponse(reply=ai_reply, session_id=session_id)
