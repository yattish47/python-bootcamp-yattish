# Capstone 1: AI Customer Support Bot

An AI-powered customer support bot for "ShopPy," a fictional e-commerce store. Built with FastAPI, LangGraph, and OpenAI — this project ties together everything from Weeks 1–7: Python fundamentals, OOP, OpenAI SDK, LangChain tools, FastAPI, and LangGraph agents.

---

## Architecture

```
Client (client.py / Postman)
        |
        | HTTP POST /chat
        v
+-------------------+
|   FastAPI Server  |  (api/main.py)
|   Session Store   |  (in-memory dict)
+-------------------+
        |
        | invoke(messages)
        v
+-------------------+
|  LangGraph Agent  |  (agent/graph.py)
|  ReAct loop       |
+-------------------+
        |
   +---------+-----------+
   |         |           |
   v         v           v
+------+ +--------+ +---------+
| FAQ  | | Orders | | Tickets |
| Tool | | Tool   | | Tool    |
+------+ +--------+ +---------+
   |         |           |
   v         v           v
data/      data/       (simulated,
faq.json  orders.json  logs to console)
```

---

## Prerequisites

- Python 3.11+
- An OpenAI API key (get one at https://platform.openai.com)

---

## Setup

```bash
# 1. Navigate to the project directory
cd capstone_1

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and add your OPENAI_API_KEY
```

---

## How to Run

**Terminal 1 — Start the API server:**
```bash
uvicorn api.main:app --reload
```

The server starts at http://127.0.0.1:8000

**Terminal 2 — Start the interactive client:**
```bash
python client.py
```

You will see a prompt. Type your customer support questions. Use `/clear` to reset the session, `/quit` to exit.

---

## API Endpoints

| Method | Endpoint              | Description                        |
|--------|-----------------------|------------------------------------|
| POST   | /chat                 | Send a message, get a reply        |
| DELETE | /session/{session_id} | Clear a session's conversation     |
| GET    | /sessions             | List all active session IDs        |
| GET    | /health               | Health check                       |

### Example: POST /chat

**Request:**
```json
{
  "message": "What is your return policy?",
  "session_id": "abc-123"
}
```

**Response:**
```json
{
  "reply": "Our return policy allows you to return items within 30 days...",
  "session_id": "abc-123"
}
```

---

## Evaluation Checklist

Work through these to confirm everything is working correctly:

- [ ] POST /chat responds correctly to a FAQ question
  - Try: `"What is your return policy?"`
- [ ] POST /chat responds correctly to an order status question
  - Try: `"What is the status of order ORD-001?"`
- [ ] Conversation memory persists: ask a follow-up question that references a previous answer
  - Try: ask about an order, then ask "When will it arrive?" without repeating the order ID
- [ ] DELETE /session/{id} clears the session
  - Verify by calling GET /sessions before and after
- [ ] Unknown queries are handled gracefully (no crash)
  - Try: `"What is the capital of France?"` — agent should respond helpfully
- [ ] The client.py interactive session works end-to-end
  - Run `python client.py`, have a multi-turn conversation, test /clear and /quit

---

## Bonus Challenges

These are optional extensions to deepen your learning:

1. **Persistent sessions** — Replace the in-memory dict with Redis or SQLite so sessions survive server restarts.
2. **Streaming responses** — Use LangGraph's `astream_events` to stream the agent's reply token-by-token to the client.
3. **Tool call visibility** — Log which tools the agent called for each message and expose that in the API response.
4. **Real ticket system** — Integrate with a real ticketing API (e.g., Freshdesk or a simple SQLite DB) instead of simulating ticket creation.
5. **Semantic FAQ search** — Replace keyword matching in `search_faq` with embedding-based similarity search using `langchain_openai.OpenAIEmbeddings`.
6. **Add tests** — Write pytest tests for each tool and for the API endpoints using `httpx.AsyncClient`.
