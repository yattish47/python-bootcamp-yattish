# Lesson 2.4 — OpenAI SDK Introduction
# Python for AI Engineers | Week 2
#
# CONCEPT:
#   The OpenAI API is a REST API. The Python SDK is a thin wrapper around it.
#   The core primitive is `chat.completions.create()` — you send a list of
#   "messages" with roles (system/user/assistant) and get a response back.
#
# BEFORE RUNNING:
#   1. pip install openai python-dotenv
#   2. Create a .env file in this folder:
#      OPENAI_API_KEY=sk-...your-key...

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ─── CLIENT SETUP ────────────────────────────────────────────────────────────

# The client reads OPENAI_API_KEY from environment automatically
client = OpenAI()

# Or explicitly:
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─── BASIC CHAT COMPLETION ───────────────────────────────────────────────────

# The messages list is the "conversation so far"
# - "system": sets the AI's behavior/persona
# - "user":   what the human says
# - "assistant": what the AI previously said (for multi-turn)

response = client.chat.completions.create(
    model="gpt-4o-mini",      # cheap model for learning
    messages=[
        {"role": "system", "content": "You are a helpful Python tutor."},
        {"role": "user", "content": "What is a list comprehension in Python?"}
    ],
    max_tokens=200
)

# Extract the text response
reply = response.choices[0].message.content
print(reply)
print()

# Inspect the full response object
print(f"Model: {response.model}")
print(f"Tokens used: {response.usage.total_tokens}")
print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")

# ─── SYSTEM PROMPT — SETTING AI BEHAVIOR ─────────────────────────────────────

# The system prompt is like a "configuration" for the AI's personality and rules.
# It's invisible to end users but shapes every response.

def ask_ai(question: str, system_prompt: str = "You are a helpful assistant.") -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        max_tokens=300,
        temperature=0.7    # 0 = deterministic, 1 = creative, 2 = chaotic
    )
    return response.choices[0].message.content


# Same question, different system prompts → different responses
pirate_answer = ask_ai(
    "What is Python?",
    system_prompt="You are a pirate. Answer everything in pirate speak. Keep it under 50 words."
)
print("PIRATE:", pirate_answer)

formal_answer = ask_ai(
    "What is Python?",
    system_prompt="You are a formal academic professor. Be concise and precise. One sentence only."
)
print("FORMAL:", formal_answer)

# ─── MULTI-TURN CONVERSATION ─────────────────────────────────────────────────

# To maintain conversation history, you append messages manually
# This is what a chatbot does — send the full history each time

def simple_chat_session():
    messages = [
        {"role": "system", "content": "You are a concise Python tutor. Keep answers under 3 sentences."}
    ]

    print("Chat session started (type 'quit' to exit)\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        print(f"AI: {reply}\n")

    print("Session ended.")
    return messages   # return the full history


# Uncomment to run the interactive session:
# history = simple_chat_session()

# ─── PARAMETERS TO KNOW ──────────────────────────────────────────────────────

# model:        which model to use
#   "gpt-4o-mini"   → cheapest, fast, good for learning (~$0.15/1M tokens)
#   "gpt-4o"        → powerful, more expensive (~$5/1M tokens)
#   "gpt-4-turbo"   → 128k context window
#
# temperature:  controls randomness (0.0 to 2.0)
#   0.0 = always picks the most likely token (deterministic)
#   0.7 = balanced creativity (good default)
#   1.5+ = very creative / unpredictable
#
# max_tokens:   maximum tokens in the response (not the request)
#   Rough guide: 1 token ≈ 0.75 words in English
#
# stop:         list of strings that stop generation early
#   stop=["###", "\n\n"]
#
# n:            how many response choices to generate (default 1)
#   If n=3, response.choices has 3 options

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Write a function `translate(text: str, target_language: str) -> str`
#   that uses the OpenAI API to translate text into the target language.
#   Use a clear system prompt. Test: translate("Hello, how are you?", "Bahasa Malaysia")

# Exercise 2:
#   Write a function `summarize(text: str, max_words: int = 50) -> str`
#   that summarizes the given text. The system prompt should enforce
#   the max_words limit.

# Exercise 3:
#   Build on the multi-turn example: write a function `chat_with_history()`
#   that keeps asking for input, sends the full history to the API, and
#   prints responses. Add a "clear" command that resets the history (but keeps
#   the system prompt).
