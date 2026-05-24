# Week 4 — Files, Errors, Tool Use

## Setup

No new packages needed. You should already have:

```bash
pip install openai python-dotenv
```

Make sure your `.env` (in this directory or a parent) contains:

```
OPENAI_API_KEY=sk-...your-key-here...
```

---

## Lessons

| File | Topic | Key Concept |
|------|-------|-------------|
| `lesson_4_1_file_io.py` | File I/O + pathlib | `open()`, `json`, `pathlib.Path` |
| `lesson_4_2_env_config.py` | Environment & Config | `python-dotenv`, `os.getenv`, config patterns |
| `lesson_4_3_exceptions.py` | Exception Handling | `try/except/else/finally`, custom exceptions |
| `lesson_4_4_tool_use.py` | OpenAI Tool Use | Function calling, tool loop, JSON schema |

---

## What is Tool Use / Function Calling?

Normally you ask the LLM a question and it generates a text answer from its training data. But what if you need **live data** — the current price of a product, the weather right now, a row from your database?

**Function calling (tool use)** solves this:

1. You define one or more **tools** as JSON schemas — each describes a function name, what it does, and what parameters it accepts.
2. You send the user's message **plus the tool list** to the API.
3. The model decides which tool (if any) to call, and returns a structured `tool_calls` object instead of a plain text response.
4. **Your code** executes the actual function with the arguments the model specified.
5. You send the result back to the model as a `tool` role message.
6. The model uses the result to compose its final answer.

The LLM **never runs your code directly** — it just requests a call and you execute it. This means you retain full control: you validate inputs, enforce permissions, and decide what to actually run.

```
User message + tools
        ↓
   [OpenAI API]
        ↓
  tool_calls: [{name: "get_product", arguments: {"id": 3}}]
        ↓
  Your code: get_product(id=3) → {"name": "Widget", "price": 9.99}
        ↓
  Send tool result back to API
        ↓
   [OpenAI API]
        ↓
  "The Widget costs $9.99 and is currently in stock."
```

---

## Project

`project/tool_chatbot.py` — a CLI chatbot backed by a product catalogue (`data/products.json`). The LLM uses tool calls to look up products rather than guessing from training data.

```bash
cd week_04
python project/tool_chatbot.py
```
