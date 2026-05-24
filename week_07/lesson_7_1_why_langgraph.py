# Lesson 7.1 — Why LangGraph?
# CONCEPT: LangGraph models AI workflows as directed graphs with shared state.
#           Each node is a function. Edges determine execution order.
#           State (TypedDict) flows between nodes — each node can read and modify it.
#
# KOTLIN EQUIVALENT: Spring State Machine / Kotlin Flow with branching.
#                    Think of it as a state machine where each state handler
#                    receives a shared data class, mutates it, and returns
#                    the next state name.
#
# PHP EQUIVALENT: A pipeline of middleware classes where each class can
#                 modify a shared $state array and decide the next step.
#                 Similar to Laravel Pipeline, but with branching and loops.

# ─── WHY NOT JUST USE CHAINS? ────────────────────────────────────────────────

# Basic LangChain chains are linear:  A → B → C → done.
# Problems this creates for real agent workflows:
#
# 1. NO LOOPS:  You can't retry a step if quality is bad.
# 2. NO BRANCHING:  You can't take different paths based on input type.
# 3. NO COMPLEX STATE:  Chains pass simple strings, not rich structured data.
# 4. NO HUMAN CHECKPOINTS:  You can't pause, let a human review, then continue.
# 5. HARD TO DEBUG:  Everything is hidden inside chain internals.
#
# LangGraph solves all of these by making the workflow explicit.

# ─── THE CORE IDEA ───────────────────────────────────────────────────────────

# A LangGraph program has three components:
#
#   1. STATE  — a TypedDict that all nodes share.  Each node reads from it
#               and returns a dict of keys to update.
#
#   2. NODES  — plain Python functions: def my_node(state: MyState) -> dict
#               They do work and return partial state updates.
#
#   3. EDGES  — connections between nodes.  Can be:
#               - Fixed:       A always goes to B
#               - Conditional: A goes to B or C depending on state

# ─── IMPORTS ─────────────────────────────────────────────────────────────────

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# ─── DEFINING STATE ──────────────────────────────────────────────────────────

# State is a TypedDict — a plain dict with type hints.
# Every node receives the full state and returns a partial update.
# LangGraph merges the returned dict into the current state automatically.

class SimpleState(TypedDict):
    message: str       # input message
    processed: str     # result after processing
    step_count: int    # how many nodes have run

# ─── DEFINING NODES ──────────────────────────────────────────────────────────

# A node is just a function:  def name(state: YourState) -> dict
# It receives the FULL current state.
# It returns ONLY the keys it wants to update (partial update).

def node_a(state: SimpleState) -> dict:
    """First node: marks the message as seen and increments counter."""
    print(f"[node_a] Received: '{state['message']}'")
    return {
        "processed": f"(seen by node_a) {state['message']}",
        "step_count": state["step_count"] + 1,
    }

def node_b(state: SimpleState) -> dict:
    """Second node: finalizes the output and increments counter."""
    print(f"[node_b] Processing: '{state['processed']}'")
    return {
        "processed": f"{state['processed']} → [finalized by node_b]",
        "step_count": state["step_count"] + 1,
    }

# ─── BUILDING THE GRAPH ──────────────────────────────────────────────────────

# 1. Create the graph, telling it what state type to use.
builder = StateGraph(SimpleState)

# 2. Register nodes.
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

# 3. Add edges.
#    START is a special built-in node representing the entry point.
#    END   is a special built-in node that terminates the graph.
builder.add_edge(START, "node_a")   # START → node_a
builder.add_edge("node_a", "node_b")  # node_a → node_b
builder.add_edge("node_b", END)     # node_b → END

# 4. Compile: validates the graph and returns a runnable.
graph = builder.compile()

# ─── RUNNING THE GRAPH ───────────────────────────────────────────────────────

print("=" * 60)
print("Running a simple 2-node graph: node_a → node_b → END")
print("=" * 60)

# Provide the initial state — all keys must be present.
initial_state: SimpleState = {
    "message": "Hello, LangGraph!",
    "processed": "",
    "step_count": 0,
}

# .invoke() runs the graph to completion and returns the final state.
final_state = graph.invoke(initial_state)

print("\nFinal state:")
for key, value in final_state.items():
    print(f"  {key}: {value!r}")

# ─── VISUALIZING THE GRAPH ───────────────────────────────────────────────────

# LangGraph can generate a Mermaid diagram of the graph structure.
# Useful for documentation and debugging complex workflows.

print("\n" + "=" * 60)
print("Graph structure (Mermaid format):")
print("=" * 60)
print(graph.get_graph().draw_mermaid())

# To render this visually, paste the output into: https://mermaid.live

# ─── COMPARING WITH CHAINS ───────────────────────────────────────────────────

print("\n" + "=" * 60)
print("What LangGraph gives you that chains do NOT:")
print("=" * 60)

features = [
    ("Loops",             "Route back to a previous node until quality is acceptable"),
    ("Branching",         "Take path A or path B based on the current state"),
    ("Rich state",        "Carry structured data (lists, dicts) across all nodes"),
    ("Human checkpoints", "Pause execution, let a human edit state, then resume"),
    ("Debuggability",     "Every node transition is explicit and inspectable"),
]
for feature, description in features:
    print(f"  {feature:<22} — {description}")

# ─── KOTLIN / SPRING MENTAL MODEL ────────────────────────────────────────────

# Kotlin/Spring developers: think of this as:
#
#   TypedDict state     == data class AgentState(...)
#   Node function       == fun processState(state: AgentState): Map<String, Any>
#   StateGraph          == StateMachineBuilder<AgentState>
#   add_edge()          == .withTransition().source(A).target(B).and()
#   graph.compile()     == stateMachine.build()
#   graph.invoke(state) == stateMachine.start(initialState)
#
# The key insight: nodes are PURE FUNCTIONS — they don't mutate state directly,
# they return a dict of changes.  LangGraph merges those changes for you.
# This is similar to a reducer in Redux or Kotlin's copy() pattern.

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 (Conceptual — model as a graph):
#   You're building an AI content moderation system.
#   It must: receive a post → check for spam → check for hate speech →
#            (if any flag is raised) notify moderator, else publish.
#   Draw this as a graph: list the nodes and edges.
#   Which edges are conditional?

# Exercise 2 (Conceptual — identify state keys):
#   For the moderation system above, what keys would you put in the TypedDict?
#   Think about: what does each node need to READ?  What does each node WRITE?
#   Hint: you'll need flags like is_spam, is_hate, and the post content itself.

# Exercise 3 (Code):
#   Add a third node called node_c to the graph above.
#   node_c should add a timestamp string to the 'processed' field
#   and increment step_count.
#   Connect it: node_b → node_c → END.
#   Run the graph and verify step_count is 3.
