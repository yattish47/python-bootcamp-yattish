#!/usr/bin/env python3
"""
Week 3 Project — Memory Chatbot
================================
A CLI chatbot with persistent conversation memory using LangChain.

Features:
  - ChatOpenAI + ChatPromptTemplate + RunnableWithMessageHistory
  - Session-based memory (each session_id has its own independent history)
  - Commands: /clear, /quit, /history, /session <id>, /newsession

Usage:
  cd week_03
  python project/memory_chatbot.py

Requirements:
  pip install langchain langchain-openai python-dotenv
  .env file in week_03/ with OPENAI_API_KEY=sk-...
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ─── ENV SETUP ────────────────────────────────────────────────────────────────

# Load .env from week_03/ directory regardless of where we run from
_project_dir = Path(__file__).parent          # week_03/project/
_week_dir = _project_dir.parent               # week_03/
_env_file = _week_dir / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv(_env_file)
except ImportError:
    print("Error: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

if not os.getenv("OPENAI_API_KEY"):
    print(f"Error: OPENAI_API_KEY not found.")
    print(f"Create {_env_file} with: OPENAI_API_KEY=sk-...")
    sys.exit(1)

# ─── IMPORTS ──────────────────────────────────────────────────────────────────

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_community.chat_message_histories import ChatMessageHistory
except ImportError as e:
    print(f"Error: Missing LangChain package — {e}")
    print("Run: pip install langchain langchain-openai")
    sys.exit(1)

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.7
MAX_TOKENS = 512
DEFAULT_SESSION = "default"

SYSTEM_PROMPT = """\
You are a helpful, friendly AI assistant. You remember the entire conversation
history within a session. Be concise but thorough. If you don't know something,
say so honestly.
"""

HELP_TEXT = """
Available commands:
  /help              Show this help message
  /history           Print the current session's conversation history
  /clear             Clear the current session's conversation history
  /session <id>      Switch to a different session (creates it if new)
  /newsession        Start a brand new session with a generated ID
  /quit  or  /exit   Exit the chatbot

Type anything else to chat.
"""

# ─── MEMORY STORE ─────────────────────────────────────────────────────────────

# Maps session_id → ChatMessageHistory
# In production this would be backed by Redis, DynamoDB, PostgreSQL, etc.
_session_store: dict[str, ChatMessageHistory] = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    """Return (or create) the ChatMessageHistory for a given session_id."""
    if session_id not in _session_store:
        _session_store[session_id] = ChatMessageHistory()
    return _session_store[session_id]


# ─── CHAIN SETUP ──────────────────────────────────────────────────────────────

def build_chain() -> RunnableWithMessageHistory:
    """Build and return the chain with memory."""
    llm = ChatOpenAI(
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    base_chain = prompt | llm | StrOutputParser()

    return RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )


# ─── COMMAND HANDLERS ─────────────────────────────────────────────────────────

def print_history(session_id: str) -> None:
    """Print the conversation history for the given session."""
    history = get_session_history(session_id)
    messages = history.messages
    if not messages:
        print(f"  [No history for session '{session_id}']\n")
        return

    print(f"\n─── History for session '{session_id}' ({len(messages)} messages) ───")
    for i, msg in enumerate(messages, 1):
        role = msg.__class__.__name__.replace("Message", "").lower()
        icon = "You" if role == "human" else " AI"
        content = msg.content
        if len(content) > 120:
            content = content[:117] + "..."
        print(f"  {i:2}. [{icon}] {content}")
    print()


def clear_session(session_id: str) -> None:
    """Clear the conversation history for the given session."""
    get_session_history(session_id).clear()
    print(f"  [Session '{session_id}' cleared]\n")


def generate_session_id() -> str:
    """Generate a unique session ID."""
    import uuid
    return f"session-{uuid.uuid4().hex[:8]}"


# ─── MAIN CHAT LOOP ───────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Memory Chatbot — Week 3 Project")
    print("  Powered by LangChain + OpenAI")
    print("=" * 60)
    print(f"  Model:   {MODEL}")
    print(f"  Session: {DEFAULT_SESSION}")
    print("  Type /help for commands, /quit to exit")
    print("=" * 60)
    print()

    chain = build_chain()
    current_session = DEFAULT_SESSION

    while True:
        try:
            user_input = input(f"[{current_session}] You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        # ── Command handling ──────────────────────────────────────────────────

        if user_input.lower() in ("/quit", "/exit"):
            print("Goodbye!")
            break

        elif user_input.lower() == "/help":
            print(HELP_TEXT)
            continue

        elif user_input.lower() == "/history":
            print_history(current_session)
            continue

        elif user_input.lower() == "/clear":
            clear_session(current_session)
            continue

        elif user_input.lower().startswith("/session "):
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                print("  Usage: /session <session_id>\n")
            else:
                current_session = parts[1].strip()
                msg_count = len(get_session_history(current_session).messages)
                print(f"  [Switched to session '{current_session}' ({msg_count} messages)]\n")
            continue

        elif user_input.lower() == "/newsession":
            current_session = generate_session_id()
            print(f"  [Started new session: '{current_session}']\n")
            continue

        elif user_input.startswith("/"):
            print(f"  Unknown command: {user_input}. Type /help for commands.\n")
            continue

        # ── Chat with the LLM ─────────────────────────────────────────────────

        config = {"configurable": {"session_id": current_session}}
        try:
            print(f"[{current_session}]  AI: ", end="", flush=True)
            # Stream the response token by token
            for chunk in chain.stream({"input": user_input}, config=config):
                print(chunk, end="", flush=True)
            print("\n")

        except KeyboardInterrupt:
            print("\n  [Response interrupted]\n")

        except Exception as e:
            print(f"\n  [Error: {e}]\n")
            if "rate" in str(e).lower():
                print("  (Rate limit hit — wait a moment and try again)\n")


if __name__ == "__main__":
    main()
