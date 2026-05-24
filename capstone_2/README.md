# Capstone 2: Autonomous Research Pipeline

An autonomous multi-agent research pipeline built with CrewAI and FastAPI. Given any topic, a crew of three AI agents — Researcher, Writer, and Editor — collaborate sequentially to produce a polished research report saved to disk.

This project puts Week 8 (CrewAI) into practice while reinforcing FastAPI (Week 5) and structured AI workflows (Weeks 6–7).

---

## Architecture

```
Client (curl / Postman)
        |
        | POST /research  { "topic": "..." }
        v
+----------------------+
|   FastAPI Server     |  (api/main.py)
|   Job Store (dict)   |
+----------------------+
        |
        | crew.kickoff()
        v
+----------------------+
|    CrewAI Crew       |  (crew/)
+----------------------+
        |
   Sequential process:
        |
        v
+------------------+
|   Researcher     |  Gathers facts and sources about the topic
|   (Agent 1)      |  Uses: MockSearchTool / SerperDevTool
+------------------+
        |
        v
+------------------+
|   Writer         |  Turns research into a structured report
|   (Agent 2)      |  Context: Researcher output
+------------------+
        |
        v
+------------------+
|   Editor         |  Reviews, improves, and finalises the report
|   (Agent 3)      |  Context: Writer output
+------------------+
        |
        | Saves to file
        v
+-------------------------+
|  output/{job_id}.md     |
+-------------------------+
        ^
        |
        | GET /report/{job_id}
        |
      Client
```

---

## Prerequisites

- Python 3.11+
- An OpenAI API key
- (Optional) A Serper API key for real web search — the pipeline works without it using mock data

---

## Setup

```bash
# 1. Navigate to the project directory
cd capstone_2

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and add your OPENAI_API_KEY
# Optionally add SERPER_API_KEY for real web search
```

---

## How to Run

**Terminal 1 — Start the API server:**
```bash
uvicorn api.main:app --reload
```

**Terminal 2 — Trigger a research job:**
```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "the impact of large language models on software engineering"}'
```

**Fetch the report:**
```bash
curl http://127.0.0.1:8000/report/{job_id}
```

Or open http://127.0.0.1:8000/docs in your browser to use the interactive Swagger UI.

---

## API Endpoints

| Method | Endpoint          | Description                              |
|--------|-------------------|------------------------------------------|
| POST   | /research         | Start a research job for a given topic   |
| GET    | /report/{job_id}  | Retrieve the finished report             |
| GET    | /jobs             | List all jobs with their status          |
| GET    | /health           | Health check                             |

### Example: POST /research

**Request:**
```json
{
  "topic": "quantum computing for beginners"
}
```

**Response:**
```json
{
  "job_id": "a1b2c3d4",
  "status": "completed",
  "message": "Research completed. Retrieve your report at GET /report/a1b2c3d4"
}
```

---

## Output

Reports are saved as Markdown files in the `output/` directory:
```
output/
  a1b2c3d4.md
  e5f6g7h8.md
```

Each report contains:
- Introduction
- Key Findings
- Analysis
- Conclusion

---

## Evaluation Checklist

- [ ] POST /research with a topic returns a job_id
  - Try: `{"topic": "the history of the internet"}`
- [ ] The crew completes and `output/{job_id}.md` is created on disk
  - Check with: `ls output/`
- [ ] GET /report/{job_id} returns the report content
  - Paste the job_id from the POST response
- [ ] The report has clear sections (Introduction, Key Findings, Analysis, Conclusion)
  - Read the returned content or open the .md file directly
- [ ] The editor's improvements are visible
  - Compare the writer's raw output (visible in server logs) vs the final report
- [ ] Multiple topics can be researched in sequence
  - Run two POST /research requests with different topics, then fetch both reports

---

## Bonus Challenges

1. **Async background tasks** — Move `crew.kickoff()` to a FastAPI `BackgroundTask` so POST /research returns immediately with `status: "pending"`, then poll GET /report until it's ready.
2. **Add a Critic agent** — Insert a fourth agent that fact-checks the Editor's output and flags unverified claims.
3. **Real web search** — Get a free Serper API key (https://serper.dev), add `SERPER_API_KEY` to your .env, and the pipeline will automatically switch from mock data to real web search results.
4. **Report formats** — Add a POST /research parameter `format: "markdown" | "html" | "json"` and generate different output formats.
5. **Streaming progress** — Use Server-Sent Events (SSE) to stream crew progress updates to the client as each agent finishes.
6. **Persistent job store** — Replace the in-memory dict with SQLite using `aiosqlite` so jobs survive server restarts.
