# Mini-Project: Simple CLI Chatbot
# Python for AI Engineers | Week 2
#
# A complete CLI chatbot using the OpenAI API directly (no frameworks).
# This is your first real AI project.
#
# SETUP:
#   cd week_02
#   source .venv/bin/activate
#   python project/simple_chatbot.py
#
# FEATURES:
#   - Multi-turn conversation with memory
#   - Configurable system prompt (persona)
#   - Token usage tracking
#   - Commands: /clear, /history, /quit, /persona <text>

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from the week_02 folder
load_dotenv(Path(__file__).parent.parent / ".env")

# ─── CONFIGURATION ───────────────────────────────────────────────────────────

MODEL = "gpt-4o-mini"
MAX_TOKENS = 500
TEMPERATURE = 0.7

DEFAULT_PERSONA = (
    "You are a helpful AI assistant. "
    "Be concise and clear. "
    "If you don't know something, say so."
)

# ─── CHATBOT CLASS ───────────────────────────────────────────────────────────

class Chatbot:
    def __init__(self, persona: str = DEFAULT_PERSONA):
        self.client = OpenAI()
        self.persona = persona
        self.history: list[dict] = []
        self.total_tokens = 0

    @property
    def messages(self) -> list[dict]:
        return [{"role": "system", "content": self.persona}] + self.history

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )

        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        self.total_tokens += response.usage.total_tokens

        return reply

    def clear(self) -> None:
        self.history = []
        print("  [History cleared]")

    def set_persona(self, persona: str) -> None:
        self.persona = persona
        self.history = []   # clear history when persona changes
        print(f"  [Persona updated. History cleared.]")

    def show_history(self) -> None:
        if not self.history:
            print("  [No conversation history yet]")
            return
        print("\n  ─── Conversation History ───")
        for msg in self.history:
            role = msg["role"].upper()
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"  {role}: {content}")
        print(f"  Total tokens used: {self.total_tokens}")
        print()


# ─── MAIN LOOP ───────────────────────────────────────────────────────────────

HELP_TEXT = """
Commands:
  /clear              Clear conversation history
  /history            Show conversation history
  /persona <text>     Change the AI's persona (clears history)
  /tokens             Show total tokens used
  /quit or /exit      Exit the chatbot
  /help               Show this help
"""

def main():
    print("=" * 50)
    print("  Python AI Chatbot — Week 2 Mini-Project")
    print("=" * 50)
    print("Type /help for commands. Type your message to chat.\n")

    bot = Chatbot()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # ── Commands ──────────────────────────────────────────────────────────
        if user_input.startswith("/"):
            command = user_input.split(maxsplit=1)
            cmd = command[0].lower()

            if cmd in ("/quit", "/exit"):
                print(f"\nGoodbye! Total tokens used: {bot.total_tokens}")
                break
            elif cmd == "/clear":
                bot.clear()
            elif cmd == "/history":
                bot.show_history()
            elif cmd == "/tokens":
                print(f"  Total tokens used: {bot.total_tokens}")
            elif cmd == "/persona":
                if len(command) < 2:
                    print("  Usage: /persona <persona description>")
                else:
                    bot.set_persona(command[1])
            elif cmd == "/help":
                print(HELP_TEXT)
            else:
                print(f"  Unknown command: {cmd}. Type /help for commands.")
            continue

        # ── Chat ──────────────────────────────────────────────────────────────
        try:
            reply = bot.chat(user_input)
            print(f"AI: {reply}\n")
        except Exception as e:
            print(f"  [Error: {e}]")
            print("  Make sure your OPENAI_API_KEY is set in week_02/.env\n")


if __name__ == "__main__":
    main()
