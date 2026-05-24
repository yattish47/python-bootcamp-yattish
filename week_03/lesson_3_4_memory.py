# Lesson 3.4 — Conversation Memory
# Python for AI Engineers | Week 3
#
# CONCEPT:
#   LLMs are stateless — each API call knows nothing about previous calls.
#   Memory = storing message history and including it in every new request.
#   LangChain provides ChatMessageHistory (the store) and
#   RunnableWithMessageHistory (the wrapper that injects history into chains).
#
# KOTLIN EQUIVALENT:
#   Memory ≈ a session-scoped Map<String, MutableList<Message>> in Spring,
#   where you look up the user's history and inject it before each LLM call.
#
# PHP EQUIVALENT:
#   Memory ≈ Laravel session storage: Session::get('chat_history', []),
#   append the new message, Session::put('chat_history', $history).

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

_week_dir = Path(__file__).parent
load_dotenv(_week_dir / ".env")

_HAS_KEY = bool(os.getenv("OPENAI_API_KEY"))
if not _HAS_KEY:
    print("WARNING: OPENAI_API_KEY not set. Live examples will be skipped.")
    print("Create week_03/.env with: OPENAI_API_KEY=sk-...\n")


# ─── WHY MEMORY MATTERS ───────────────────────────────────────────────────────

# Without memory — every call is independent:
#   User: "My name is Yattish."
#   AI:   "Nice to meet you, Yattish!"
#   User: "What's my name?"
#   AI:   "I don't know your name."   ← stateless, forgot the first exchange
#
# With memory — the full conversation history is included:
#   User: "My name is Yattish."
#   AI:   "Nice to meet you, Yattish!"
#   User: "What's my name?"
#   AI:   "Your name is Yattish!"     ← correct!


# ─── ChatMessageHistory — THE STORE ──────────────────────────────────────────

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ChatMessageHistory is just an in-memory list of messages.
# In production you'd use RedisChatMessageHistory, DynamoDBChatMessageHistory, etc.

history = ChatMessageHistory()
history.add_user_message("My name is Yattish.")
history.add_ai_message("Nice to meet you, Yattish! How can I help?")
history.add_user_message("What's my name?")

print("Message history:")
for msg in history.messages:
    role = msg.__class__.__name__.replace("Message", "")
    print(f"  [{role:6}] {msg.content}")
print()

# Inspect and manipulate
print(f"Total messages: {len(history.messages)}")
history.clear()
print(f"After clear: {len(history.messages)} messages\n")


# ─── MANUAL MEMORY PATTERN (no LangChain wrapper) ────────────────────────────

# This shows you what's happening under the hood:
# maintain a list, prepend system prompt, append each exchange.

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

if _HAS_KEY:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    conversation: list = [
        SystemMessage(content="You are a helpful assistant. Be concise.")
    ]

    def chat_manual(user_input: str) -> str:
        conversation.append(HumanMessage(content=user_input))
        response = llm.invoke(conversation)
        conversation.append(AIMessage(content=response.content))
        return response.content

    print("Manual memory demo:")
    print("User:", "My favourite colour is blue.")
    print("AI:  ", chat_manual("My favourite colour is blue."))
    print("User:", "What is my favourite colour?")
    print("AI:  ", chat_manual("What is my favourite colour?"))
    print(f"Conversation length: {len(conversation)} messages\n")


# ─── RunnableWithMessageHistory — THE LANGCHAIN WAY ──────────────────────────

# RunnableWithMessageHistory wraps a chain and:
#   1. Loads history for the given session_id before each call.
#   2. Appends the human message and AI response to history automatically.
# This is the production pattern for multi-user conversational AI.

from langchain_core.runnables.history import RunnableWithMessageHistory

# A prompt that includes a placeholder for chat history
memory_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Be concise and friendly."),
    MessagesPlaceholder(variable_name="chat_history"),   # ← history injected here
    ("human", "{input}"),
])

# The store: a dict mapping session_id → ChatMessageHistory
# In production this would be Redis, a database, etc.
session_store: dict[str, ChatMessageHistory] = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    """Return (or create) the ChatMessageHistory for this session."""
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]


if _HAS_KEY:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    base_chain = memory_prompt | llm | StrOutputParser()

    chain_with_memory = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    def chat(session_id: str, user_input: str) -> str:
        config = {"configurable": {"session_id": session_id}}
        return chain_with_memory.invoke({"input": user_input}, config=config)

    # Session A
    print("=== Session A ===")
    print("User:", "My name is Yattish and I'm learning Python for AI.")
    print("AI:  ", chat("session_a", "My name is Yattish and I'm learning Python for AI."))
    print("User:", "What am I learning?")
    print("AI:  ", chat("session_a", "What am I learning?"))
    print()

    # Session B — completely separate history
    print("=== Session B (separate user) ===")
    print("User:", "I'm building a Spring Boot microservice.")
    print("AI:  ", chat("session_b", "I'm building a Spring Boot microservice."))
    print("User:", "What language am I using?")
    print("AI:  ", chat("session_b", "What language am I using?"))
    print()


# ─── INSPECTING HISTORY ───────────────────────────────────────────────────────

if _HAS_KEY:
    print("=== Inspecting session_a history ===")
    history_a = get_session_history("session_a")
    for i, msg in enumerate(history_a.messages, 1):
        role = msg.__class__.__name__.replace("Message", "")
        print(f"  {i}. [{role:6}] {msg.content[:60]}")
    print()

    # Clear a specific session
    history_a.clear()
    print(f"After clear: session_a has {len(get_session_history('session_a').messages)} messages\n")


# ─── SESSION_ID PATTERN FOR MULTI-USER SUPPORT ────────────────────────────────

# In a real app, session_id might be:
#   - A user's UUID from your database
#   - A Telegram chat_id
#   - A request session token
#   - A combination: f"{user_id}:{conversation_id}"
#
# Example mapping:

def make_session_id(user_id: int, thread_id: str) -> str:
    """Generate a deterministic session_id for a user + thread combination."""
    return f"user:{user_id}:thread:{thread_id}"


example_session = make_session_id(42, "support-thread-001")
print(f"Example session_id: {example_session}")


# ─── MEMORY TYPES (overview) ─────────────────────────────────────────────────

# LangChain / LangGraph offer several memory strategies:
#
# | Type                          | What it stores                          |
# |-------------------------------|-----------------------------------------|
# | ChatMessageHistory (this)     | Full verbatim message list              |
# | ConversationSummaryMemory     | Summarises old turns to save tokens     |
# | ConversationBufferWindowMemory| Last K turns only (sliding window)      |
# | VectorStoreRetrieverMemory    | Semantically relevant past turns        |
#
# For most chatbots: start with ChatMessageHistory.
# For long conversations or cost control: add summarisation.


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 — MULTI-SESSION DEMO
#   Create three separate chat sessions (use string IDs: "alice", "bob", "carol").
#   Tell each session a different fact about the user (name, hobby, city).
#   Then ask each session "what do you know about me?" and print the responses.
#   Confirm that each session only knows its own facts.

# Exercise 2 — HISTORY EXPORT
#   After a multi-turn conversation (at least 4 turns), write a function
#   `export_history(session_id: str) -> list[dict]` that returns the history
#   as a list of {"role": "human"/"ai", "content": "..."} dicts.
#   Print the exported JSON using json.dumps(..., indent=2).

# Exercise 3 — SLIDING WINDOW MEMORY
#   Implement a `get_session_history_limited(session_id, max_messages=6)`
#   function that returns a ChatMessageHistory containing only the LAST
#   max_messages messages. Use this instead of the full history getter and
#   observe how the bot "forgets" older turns after the window fills up.
