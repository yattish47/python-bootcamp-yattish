# Lesson 7.2 — Nodes, Edges, and State
# CONCEPT: Deep dive into how LangGraph state works. Nodes return PARTIAL
#           state updates. LangGraph merges those updates automatically.
#           Build a full 3-node text processing pipeline.
#
# KOTLIN EQUIVALENT: Each node is like a Kotlin function returning a
#                    Map<String, Any> of changed fields. LangGraph acts like
#                    a state manager that applies those changes via copy().
#                    Similar to a Redux reducer pattern or MVI architecture.
#
# PHP EQUIVALENT: Each node is a class with a handle(array $state): array
#                 method that returns only the keys it changed.
#                 Like a pipeline stage in Laravel Pipeline, but with
#                 explicit state merging instead of passing $next.

# ─── IMPORTS ─────────────────────────────────────────────────────────────────

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

# ─── DEFINING STATE WITH TYPEDDICT ───────────────────────────────────────────

# TypedDict gives you type-checked dict keys.
# Use Optional[T] for keys that may not be set initially.
# All keys must be present when you call graph.invoke(initial_state).

class DocumentState(TypedDict):
    # Input
    raw_text: str           # the original document text

    # After preprocessing
    cleaned_text: str       # whitespace-normalized, lowercased text
    word_count: int         # number of words in cleaned text

    # After analysis
    sentiment: str          # "positive", "negative", or "neutral"
    key_topics: list        # list of extracted topic strings

    # After formatting
    report: str             # final formatted report string

# ─── UNDERSTANDING STATE UPDATES ─────────────────────────────────────────────

# KEY RULE: Nodes only return the keys they change.
# LangGraph merges the returned dict into the existing state.
#
# Example:
#   current state:   {"raw_text": "Hello", "cleaned_text": "", "word_count": 0, ...}
#   node returns:    {"cleaned_text": "hello", "word_count": 1}
#   merged state:    {"raw_text": "Hello", "cleaned_text": "hello", "word_count": 1, ...}
#
# This is similar to Kotlin's data class copy() but applied as a dict merge.
# You DO NOT need to return the entire state — only what changed.

# ─── NODE 1: PREPROCESS ──────────────────────────────────────────────────────

def preprocess(state: DocumentState) -> dict:
    """
    Clean the raw text: normalize whitespace and lowercase.
    Returns: cleaned_text, word_count
    """
    print("[preprocess] Cleaning text...")

    raw = state["raw_text"]

    # Normalize whitespace: split on any whitespace, rejoin with single spaces
    words = raw.split()
    cleaned = " ".join(words).lower()
    count = len(words)

    print(f"[preprocess] Word count: {count}, sample: '{cleaned[:40]}...'")

    # Return ONLY the keys this node changes.
    return {
        "cleaned_text": cleaned,
        "word_count": count,
    }

# ─── NODE 2: ANALYZE ─────────────────────────────────────────────────────────

# Simple keyword-based analysis (no LLM needed for this demo).
# In a real system, this node would call an LLM.

POSITIVE_WORDS = {"good", "great", "excellent", "amazing", "happy", "love", "wonderful", "best"}
NEGATIVE_WORDS = {"bad", "terrible", "awful", "hate", "worst", "horrible", "poor", "disappointing"}

TOPIC_KEYWORDS = {
    "technology": {"python", "ai", "software", "computer", "code", "algorithm", "data"},
    "business":   {"revenue", "profit", "market", "customer", "sales", "growth", "company"},
    "health":     {"health", "medical", "doctor", "hospital", "wellness", "fitness", "disease"},
}

def analyze(state: DocumentState) -> dict:
    """
    Analyze sentiment and extract key topics from cleaned text.
    Returns: sentiment, key_topics
    """
    print("[analyze] Analyzing sentiment and topics...")

    words_in_doc = set(state["cleaned_text"].split())

    # Sentiment
    pos_count = len(words_in_doc & POSITIVE_WORDS)
    neg_count = len(words_in_doc & NEGATIVE_WORDS)
    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # Topics
    topics_found = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if words_in_doc & keywords:  # set intersection
            topics_found.append(topic)

    if not topics_found:
        topics_found = ["general"]

    print(f"[analyze] Sentiment: {sentiment}, Topics: {topics_found}")

    return {
        "sentiment": sentiment,
        "key_topics": topics_found,
    }

# ─── NODE 3: FORMAT OUTPUT ───────────────────────────────────────────────────

def format_output(state: DocumentState) -> dict:
    """
    Assemble all analysis results into a final readable report.
    Returns: report
    """
    print("[format_output] Generating report...")

    report_lines = [
        "=" * 50,
        "DOCUMENT ANALYSIS REPORT",
        "=" * 50,
        f"Word count   : {state['word_count']}",
        f"Sentiment    : {state['sentiment'].upper()}",
        f"Topics       : {', '.join(state['key_topics'])}",
        "",
        "Cleaned text preview:",
        f"  {state['cleaned_text'][:100]}{'...' if len(state['cleaned_text']) > 100 else ''}",
        "=" * 50,
    ]

    report = "\n".join(report_lines)

    return {"report": report}

# ─── BUILDING THE GRAPH ──────────────────────────────────────────────────────

print("Building document processing pipeline...")

builder = StateGraph(DocumentState)

# Register all three nodes
builder.add_node("preprocess",    preprocess)
builder.add_node("analyze",       analyze)
builder.add_node("format_output", format_output)

# Wire them together as a linear pipeline
builder.add_edge(START,         "preprocess")
builder.add_edge("preprocess",  "analyze")
builder.add_edge("analyze",     "format_output")
builder.add_edge("format_output", END)

# Compile
pipeline = builder.compile()

# ─── RUNNING THE PIPELINE ────────────────────────────────────────────────────

sample_document = """
    Python is an amazing programming language for AI development.
    The data science ecosystem is the best in the world.
    Great libraries make software development wonderful and efficient.
    The code quality is excellent when you follow best practices.
"""

print("\n" + "=" * 60)
print("Running 3-node pipeline: preprocess → analyze → format_output")
print("=" * 60)

initial_state: DocumentState = {
    "raw_text":     sample_document,
    "cleaned_text": "",
    "word_count":   0,
    "sentiment":    "",
    "key_topics":   [],
    "report":       "",
}

final_state = pipeline.invoke(initial_state)

print("\n" + final_state["report"])

# ─── INSPECTING STATE AT EACH STEP ───────────────────────────────────────────

# You can use .stream() to see the state after EACH node runs.
# This is invaluable for debugging.

print("\n" + "=" * 60)
print("Streaming execution (see state updates step by step):")
print("=" * 60)

for step_output in pipeline.stream(initial_state):
    # step_output is a dict: { node_name: {keys_that_changed} }
    for node_name, state_update in step_output.items():
        print(f"\n  After [{node_name}]:")
        for key, value in state_update.items():
            preview = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
            print(f"    {key}: {preview!r}")

# ─── GRAPH VISUALIZATION ─────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Graph structure:")
print("=" * 60)
print(pipeline.get_graph().draw_mermaid())

# ─── KEY RULES RECAP ─────────────────────────────────────────────────────────

print("=" * 60)
print("Key rules for nodes:")
print("  1. Signature: def node(state: YourState) -> dict")
print("  2. Return ONLY the keys you change (partial update)")
print("  3. Never mutate state in-place — always return a new dict")
print("  4. All required state keys must be present in initial_state")
print("=" * 60)

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Add a new node called 'validate' that runs BEFORE 'preprocess'.
#   It should check that raw_text is not empty and has at least 5 words.
#   Add a key 'is_valid: bool' to the TypedDict.
#   If invalid, set is_valid=False and set report to an error message.
#   Wire it: START → validate → preprocess → ...
#   Hint: you'll need a conditional edge after validate (next lesson covers this,
#         but try to think about how you'd structure it).

# Exercise 2:
#   Add a 'statistics' key to DocumentState (a dict with sentence_count,
#   avg_word_length, etc.).
#   Add a new node 'compute_stats' between preprocess and analyze that
#   populates this key.
#   Use .stream() to verify the statistics appear after the right node.

# Exercise 3:
#   Change format_output to also include the top 3 longest words in the
#   cleaned text.  The node should compute this internally (no new state keys
#   needed) and include them in the report string.
