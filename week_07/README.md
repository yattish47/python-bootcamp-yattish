# Week 7 — LangGraph: Stateful Agents

## Setup

```bash
pip install langgraph langchain langchain-openai python-dotenv
```

Add your OpenAI key to a `.env` file in the project root:
```
OPENAI_API_KEY=sk-...
```

---

## Lessons

| File | Topic |
|------|-------|
| `lesson_7_1_why_langgraph.py` | Why LangGraph? Limitations of chains, directed graphs, first example |
| `lesson_7_2_nodes_edges.py` | Nodes, edges, TypedDict state, building a 3-node pipeline |
| `lesson_7_3_routing.py` | Conditional edges, router functions, loops |
| `lesson_7_4_human_in_loop.py` | Interrupt-before, MemorySaver checkpointer, human review pattern |
| `project/routing_agent.py` | Complete CLI routing agent with classification and research |

---

## Key Concept

**LangGraph = a state machine for AI.**

- Every step is a **node** (a plain Python function).
- The graph decides **what to call next** based on the current **state**.
- State is a `TypedDict` that flows from node to node — each node reads it and returns a partial update.

```
START → classify → (factual?) → research → format_output → END
                 ↘ simple_answer ↗
```

This gives you:
- **Loops** — route back to a previous node until quality is good enough
- **Branching** — different paths for different input types
- **Persistence** — pause the graph, let a human review, then resume
- **Full control** — you define every transition, nothing is hidden

---

## When to Use LangGraph vs AgentExecutor

| Situation | Use |
|-----------|-----|
| Simple tool-calling loop ("use tools until done") | `AgentExecutor` |
| Complex multi-step workflow with conditional logic | `LangGraph` |
| You need human-in-the-loop checkpoints | `LangGraph` |
| You need loops with quality checks | `LangGraph` |
| Rapid prototyping, one-shot tasks | `AgentExecutor` |
| Production pipelines with auditing | `LangGraph` |

---

## Mental Model (for Kotlin/Spring developers)

LangGraph is like **Spring State Machine** or a **Kotlin Flow pipeline** where:
- `TypedDict` state = your domain object / data class
- Nodes = state handlers / processors
- Edges = transition rules
- `compile()` = build the state machine
- `invoke()` = fire the initial event

The key difference from a simple chain: **the graph can loop and branch based on data**, not just execute linearly.
