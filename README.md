# Python for AI Engineers — Crash Course

A structured 10-week Python crash course designed for developers with existing programming experience (Kotlin/Spring Boot, Laravel/PHP) who want to build AI agent projects.

## What You'll Build

- Week 2: CLI chatbot using the OpenAI API
- Week 3: Conversational chatbot with memory (LangChain)
- Week 4: Tool-calling chatbot that queries a JSON database
- Week 5: Streaming AI chat REST API (FastAPI)
- Week 6: Autonomous web research agent
- Week 7: Multi-step routing agent (LangGraph)
- Week 8: 3-agent research pipeline (CrewAI)
- Capstone 1: AI Customer Support Bot (FastAPI + LangGraph)
- Capstone 2: Autonomous Research Pipeline (CrewAI + FastAPI)

## Roadmap

| Week | Topic | Key Tools |
|------|-------|-----------|
| 1 | Python Foundations | Pure Python |
| 2 | OOP + First LLM Call | OpenAI SDK |
| 3 | Power Features + LangChain | LangChain, asyncio |
| 4 | Files, Errors, Tool Use | OpenAI function calling |
| 5 | FastAPI AI Backend | FastAPI, SSE streaming |
| 6 | LangChain Agents | AgentExecutor, custom tools |
| 7 | LangGraph Stateful Agents | LangGraph, state machines |
| 8 | CrewAI Multi-Agent Systems | CrewAI |
| 9 | Capstone 1 | FastAPI + LangGraph |
| 10 | Capstone 2 | CrewAI + FastAPI |

## Setup

**Prerequisites:** Python 3.11+, conda or pyenv, VS Code

```bash
# Clone and open
git clone <repo-url>
cd python_learning
code .

# Create and activate environment
conda create -n pyai python=3.11 -y
conda activate pyai
```

See `prerequisites.md` for the full setup guide including API keys.

## Lesson Format

Each week contains:
- `README.md` — lesson notes with Kotlin/PHP side-by-side comparisons
- `lesson_X_Y_topic.py` — runnable lesson files with inline explanations
- `exercises/` — coding exercises
- `quiz.md` — knowledge check before moving to the next week

## Progress

- [x] Week 1 — Python Foundations
- [ ] Week 2 — OOP + First LLM Call
- [ ] Week 3 — Power Features + LangChain
- [ ] Week 4 — Files, Errors, Tool Use
- [ ] Week 5 — FastAPI AI Backend
- [ ] Week 6 — LangChain Agents
- [ ] Week 7 — LangGraph Stateful Agents
- [ ] Week 8 — CrewAI Multi-Agent Systems
- [ ] Capstone 1 — AI Customer Support Bot
- [ ] Capstone 2 — Autonomous Research Pipeline

## API Keys Needed

| Week | Service | Free Tier |
|------|---------|-----------|
| Week 2 | OpenAI API | $5 free credit |
| Week 6 | Tavily Search (optional) | 1,000 searches/month |
