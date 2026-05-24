"""
Week 7 Project: Routing Agent CLI
==================================
A complete LangGraph-based CLI agent that:
- Classifies incoming questions as "factual", "technical", or "opinion"
- Routes to the appropriate handler based on classification
- Uses mock responses (swap in real LLM calls when you have an API key)
- Supports /debug to see the full state after each step
- Supports /quit to exit

State flow:
  START → classify_question → [route] → (factual: research | technical: code_lookup | opinion: simple_answer)
                                      → format_output → END

Run with:
  python3 week_07/project/routing_agent.py
"""

import os
import sys
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END

# ─── STATE ────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    question: str
    category: str            # "factual" | "technical" | "opinion" | "unknown"
    search_results: list     # mock search results
    answer: str
    reasoning: str           # why this path was taken
    final_output: str
    debug_log: list          # trace of nodes visited

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _log(state: AgentState, node_name: str, message: str) -> list:
    """Append to debug_log and return updated list."""
    entry = f"[{node_name}] {message}"
    return state.get("debug_log", []) + [entry]

# ─── NODES ────────────────────────────────────────────────────────────────────

def classify_question(state: AgentState) -> dict:
    """Classify the question into a category using keyword heuristics."""
    question = state["question"].lower()

    factual_signals    = ["what is", "who is", "when did", "how many", "where is",
                          "define", "capital of", "year", "date", "founded"]
    technical_signals  = ["how do i", "how to", "code", "python", "implement",
                          "debug", "error", "install", "command", "function",
                          "class", "api", "script", "algorithm"]
    opinion_signals    = ["should i", "best", "better", "recommend", "prefer",
                          "opinion", "think", "feel", "experience"]

    if any(s in question for s in factual_signals):
        category = "factual"
        reasoning = "Question contains factual-lookup keywords."
    elif any(s in question for s in technical_signals):
        category = "technical"
        reasoning = "Question contains technical/code keywords."
    elif any(s in question for s in opinion_signals):
        category = "opinion"
        reasoning = "Question contains opinion/recommendation keywords."
    else:
        category = "opinion"
        reasoning = "No strong signal detected — defaulting to opinion path."

    log = _log(state, "classify", f"'{state['question'][:40]}' → {category}")
    return {"category": category, "reasoning": reasoning, "debug_log": log}


def research(state: AgentState) -> dict:
    """Handle factual questions with mock search results."""
    question = state["question"]

    # Mock search results — in real code, use SerperAPI / Tavily / etc.
    mock_results = [
        {"source": "wikipedia.org",  "snippet": f"Overview article about: {question}"},
        {"source": "britannica.com", "snippet": f"Encyclopedic definition related to: {question}"},
        {"source": "reuters.com",    "snippet": f"Recent news context for: {question}"},
    ]

    answer = (
        f"Based on research across {len(mock_results)} sources:\n"
        f"The factual answer to '{question}' would be retrieved from authoritative "
        f"sources and synthesized here. In production, this node calls a search API."
    )

    log = _log(state, "research", f"Fetched {len(mock_results)} mock results.")
    return {"search_results": mock_results, "answer": answer, "debug_log": log}


def code_lookup(state: AgentState) -> dict:
    """Handle technical/coding questions."""
    question = state["question"]

    # Mock technical response
    answer = (
        f"Technical guidance for: '{question}'\n\n"
        f"Step-by-step approach:\n"
        f"  1. Understand the requirements and edge cases.\n"
        f"  2. Choose the appropriate library/pattern.\n"
        f"  3. Write a minimal working example first.\n"
        f"  4. Add error handling and tests.\n\n"
        f"In production, this node would query a code-specific LLM with the full question."
    )

    log = _log(state, "code_lookup", "Provided technical guidance.")
    return {"answer": answer, "debug_log": log}


def simple_answer(state: AgentState) -> dict:
    """Handle opinion/discussion questions."""
    question = state["question"]

    answer = (
        f"Regarding '{question}':\n\n"
        f"This is a subjective question with multiple valid perspectives. "
        f"Key considerations include: your specific context, constraints, and goals. "
        f"A thoughtful answer would weigh the trade-offs specific to your situation.\n\n"
        f"In production, this node sends the question to an LLM for a nuanced response."
    )

    log = _log(state, "simple_answer", "Provided opinion-style response.")
    return {"answer": answer, "debug_log": log}


def format_output(state: AgentState) -> dict:
    """Format the final answer for display."""
    separator = "─" * 56

    lines = [
        separator,
        f"Category : {state['category'].upper()}",
        f"Routing  : {state['reasoning']}",
        separator,
        "Answer:",
        state["answer"],
        separator,
    ]

    if state.get("search_results"):
        lines.insert(-1, f"\nSources consulted: {len(state['search_results'])}")

    final_output = "\n".join(lines)

    log = _log(state, "format_output", "Output formatted.")
    return {"final_output": final_output, "debug_log": log}

# ─── ROUTER ───────────────────────────────────────────────────────────────────

def route_question(state: AgentState) -> str:
    """Return the next node name based on category."""
    routing_map = {
        "factual":   "research",
        "technical": "code_lookup",
        "opinion":   "simple_answer",
        "unknown":   "simple_answer",
    }
    next_node = routing_map.get(state["category"], "simple_answer")
    return next_node

# ─── BUILD GRAPH ──────────────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("classify",      classify_question)
    builder.add_node("research",      research)
    builder.add_node("code_lookup",   code_lookup)
    builder.add_node("simple_answer", simple_answer)
    builder.add_node("format_output", format_output)

    builder.add_edge(START, "classify")

    builder.add_conditional_edges(
        "classify",
        route_question,
        {
            "research":     "research",
            "code_lookup":  "code_lookup",
            "simple_answer":"simple_answer",
        }
    )

    builder.add_edge("research",      "format_output")
    builder.add_edge("code_lookup",   "format_output")
    builder.add_edge("simple_answer", "format_output")
    builder.add_edge("format_output", END)

    return builder.compile()

# ─── CLI ──────────────────────────────────────────────────────────────────────

def print_banner():
    print("\n" + "=" * 60)
    print("  LangGraph Routing Agent")
    print("  Week 7 Project — Python AI Engineering")
    print("=" * 60)
    print("  Commands:")
    print("    /quit    — exit the agent")
    print("    /debug   — show full state after next question")
    print("    /graph   — print the graph structure (Mermaid)")
    print("=" * 60 + "\n")

def run_cli():
    graph = build_graph()
    debug_mode = False

    print_banner()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("Goodbye!")
            break

        if user_input.lower() == "/debug":
            debug_mode = not debug_mode
            status = "ON" if debug_mode else "OFF"
            print(f"[Debug mode: {status}]")
            continue

        if user_input.lower() == "/graph":
            print("\n" + graph.get_graph().draw_mermaid())
            continue

        # Build initial state
        initial_state: AgentState = {
            "question":       user_input,
            "category":       "",
            "search_results": [],
            "answer":         "",
            "reasoning":      "",
            "final_output":   "",
            "debug_log":      [],
        }

        # Run the graph
        try:
            final_state = graph.invoke(initial_state)
        except Exception as e:
            print(f"[Error] {e}")
            continue

        # Display result
        print("\n" + final_state.get("final_output", "[No output generated]"))

        # Show debug trace if requested
        if debug_mode:
            print("\n[Debug — node execution trace:]")
            for entry in final_state.get("debug_log", []):
                print(f"  {entry}")

        print()

# ─── DEMO MODE (non-interactive) ──────────────────────────────────────────────

def run_demo():
    """Run a quick demo with preset questions — useful for testing."""
    graph = build_graph()

    questions = [
        ("Factual",   "What is the capital of Germany?"),
        ("Technical", "How do I implement a binary search in Python?"),
        ("Opinion",   "Should I use PostgreSQL or MongoDB for my project?"),
        ("Ambiguous", "Tell me about machine learning"),
    ]

    print("\n" + "=" * 60)
    print("DEMO MODE — Running preset questions")
    print("=" * 60)

    for label, question in questions:
        print(f"\n[{label}] Q: {question}")
        state = graph.invoke({
            "question":       question,
            "category":       "",
            "search_results": [],
            "answer":         "",
            "reasoning":      "",
            "final_output":   "",
            "debug_log":      [],
        })
        print(state["final_output"])

# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_cli()
