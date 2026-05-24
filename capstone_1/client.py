"""
Interactive CLI client for the ShopPy Customer Support Bot.

Talks to the FastAPI server over HTTP using httpx.

Usage:
    python client.py

Commands:
    /clear  — Clear the current session and start fresh
    /quit   — Exit the client
"""

import uuid
import sys
import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "http://127.0.0.1:8000"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def send_message(session_id: str, message: str) -> str:
    """Send a chat message and return the AI reply."""
    try:
        response = httpx.post(
            f"{BASE_URL}/chat",
            json={"message": message, "session_id": session_id},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["reply"]
    except httpx.ConnectError:
        return (
            "[Error] Cannot connect to the server. "
            "Make sure it is running:\n  uvicorn api.main:app --reload"
        )
    except httpx.HTTPStatusError as e:
        return f"[Error] Server returned {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"[Error] Unexpected error: {e}"


def clear_session(session_id: str) -> str:
    """Delete the session on the server."""
    try:
        response = httpx.delete(
            f"{BASE_URL}/session/{session_id}",
            timeout=10.0,
        )
        if response.status_code == 404:
            return "Session was already empty or not found."
        response.raise_for_status()
        return "Session cleared. Starting a fresh conversation."
    except httpx.ConnectError:
        return "[Error] Cannot connect to the server."
    except Exception as e:
        return f"[Error] {e}"


def print_banner(session_id: str):
    print()
    print("=" * 60)
    print("  ShopPy AI Customer Support")
    print("=" * 60)
    print(f"  Session ID : {session_id}")
    print(f"  Server     : {BASE_URL}")
    print()
    print("  Commands:")
    print("    /clear  — Start a new conversation")
    print("    /quit   — Exit")
    print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main():
    session_id = str(uuid.uuid4())
    print_banner(session_id)

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            sys.exit(0)

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("Goodbye!")
            sys.exit(0)

        if user_input.lower() == "/clear":
            msg = clear_session(session_id)
            # Generate a fresh session ID after clearing
            session_id = str(uuid.uuid4())
            print(f"Bot: {msg}")
            print(f"     (New Session ID: {session_id})\n")
            continue

        reply = send_message(session_id, user_input)
        print(f"\nBot: {reply}\n")


if __name__ == "__main__":
    main()
