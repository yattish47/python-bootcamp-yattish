# Week 7 Quiz — LangGraph: Stateful Agents

Answer each question, then reveal the answer by reading the hidden text below each question.

---

## Question 1
What is the purpose of `StateGraph` in LangGraph, and what argument does its constructor require?

<details>
<summary>Answer</summary>

`StateGraph` is the main builder class for constructing a LangGraph workflow. It takes a `TypedDict` class as its argument, which defines the shape of the shared state that flows between all nodes.

```python
class MyState(TypedDict):
    message: str
    count: int

builder = StateGraph(MyState)
```

Every node in the graph receives this state dict and can return partial updates to it.
</details>

---

## Question 2
A node function in LangGraph has this signature:

```python
def my_node(state: AgentState) -> dict:
    ...
```

Does the returned dict need to contain ALL keys from `AgentState`, or only the keys that changed? Why?

<details>
<summary>Answer</summary>

Only the keys that **changed**. LangGraph automatically **merges** the returned dict into the existing state — it does not replace the entire state. This is called a **partial state update**.

If your state has 10 keys but your node only modifies 2 of them, you return a dict with only those 2 keys. The other 8 remain unchanged.

This is similar to Kotlin's `copy()` method on a data class — you only specify what changes.
</details>

---

## Question 3
What is the difference between `add_edge()` and `add_conditional_edges()` in LangGraph?

<details>
<summary>Answer</summary>

- **`add_edge(source, target)`** — a fixed edge. The graph always goes from `source` to `target`, no matter what the state says.

- **`add_conditional_edges(source, router_fn, mapping)`** — a dynamic edge. LangGraph calls `router_fn(state)` to get a string, then uses `mapping` to look up which node to go to next.

```python
def my_router(state) -> str:
    return "node_a" if state["score"] > 5 else "node_b"

builder.add_conditional_edges("evaluate", my_router, {
    "node_a": "node_a",
    "node_b": "node_b",
})
```

Conditional edges enable both **branching** and **loops**.
</details>

---

## Question 4
How do you create a loop in LangGraph? What safety mechanism should you always include?

<details>
<summary>Answer</summary>

A loop is created by making a conditional edge route back to a **previous node**:

```python
builder.add_conditional_edges(
    "evaluate_quality",
    check_quality_fn,
    {
        "done":   "finalize",     # exit the loop
        "retry":  "do_research",  # loop back
    }
)
```

**Always include a safety valve** to prevent infinite loops:
- Add an `iteration` counter to the state
- In the router, if `iteration >= MAX_ITERATIONS`, force the "done" branch regardless of quality

Without this, a bug in your quality-check logic can cause the graph to loop forever.
</details>

---

## Question 5
Explain the human-in-the-loop pattern in LangGraph. What are the three key components needed to implement it?

<details>
<summary>Answer</summary>

Human-in-the-loop allows you to **pause** a graph before a critical node, let a human review and optionally edit the state, then **resume** execution.

The three required components are:

1. **A checkpointer** — persists the graph state between runs so the graph can be resumed later.
   ```python
   from langgraph.checkpoint.memory import MemorySaver
   checkpointer = MemorySaver()
   ```

2. **`interrupt_before` parameter** — specifies which node(s) to pause before.
   ```python
   graph = builder.compile(
       checkpointer=checkpointer,
       interrupt_before=["send_email"]
   )
   ```

3. **Thread ID in config** — uniquely identifies a conversation/session so the checkpointer stores the right state.
   ```python
   config = {"configurable": {"thread_id": "user-123"}}
   ```

The flow: `invoke(state, config)` → pauses → human calls `update_state(config, changes)` → `invoke(None, config)` to resume.
</details>

---

## Question 6
What does `START` and `END` represent in LangGraph? Are they actual node functions you define?

<details>
<summary>Answer</summary>

**No** — `START` and `END` are **special built-in constants** provided by LangGraph. You do not define them as functions.

- `START` — the virtual entry point of the graph. You add an edge from `START` to your first real node. This tells LangGraph which node to run first when you call `invoke()`.

- `END` — the virtual exit point. When a node has an edge to `END`, the graph terminates after that node finishes.

```python
from langgraph.graph import START, END

builder.add_edge(START, "my_first_node")
builder.add_edge("my_last_node", END)
```

`END` can also be used as a target in `add_conditional_edges()` to terminate early.
</details>

---

## Question 7
You need to support multiple simultaneous users with a human-in-the-loop agent. Each user's paused state must be kept separate. How does LangGraph handle this, and what do you need to provide?

<details>
<summary>Answer</summary>

LangGraph uses **thread IDs** to separate state for different users. Each call to `invoke()` or `update_state()` must include a config dict with a `thread_id`:

```python
# User A's session
config_a = {"configurable": {"thread_id": "session-alice-001"}}

# User B's session
config_b = {"configurable": {"thread_id": "session-bob-002"}}

# These are completely independent — separate checkpointed states
graph.invoke(state_a, config_a)
graph.invoke(state_b, config_b)
```

The **checkpointer** (e.g., `MemorySaver`) stores each thread's state separately, keyed by thread ID. In production, you would use a persistent checkpointer (SQLite, Redis, PostgreSQL) so that state survives process restarts.

This is analogous to session management in Spring Security or Laravel sessions — each user has their own isolated state identified by a unique key.
</details>
