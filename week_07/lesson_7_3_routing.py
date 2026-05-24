# Lesson 7.3 — Conditional Edges and Routing
# CONCEPT: add_conditional_edges() lets you route to different nodes based
#           on the current state. A router function reads state and returns
#           a string naming the next node. This enables branching AND loops.
#
# KOTLIN EQUIVALENT: A when expression on a sealed class/enum that picks
#                    the next state handler. Similar to Spring State Machine's
#                    .withChoice() guard transitions.
#
# PHP EQUIVALENT: A switch/match on $state['category'] that returns the
#                 next handler class name. Like a Laravel Job chain that
#                 conditionally dispatches different jobs.

# ─── IMPORTS ─────────────────────────────────────────────────────────────────

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

# ─── EXAMPLE 1: SIMPLE BRANCHING ─────────────────────────────────────────────
# Question classifier: route to simple_answer OR research based on category.

class QuestionState(TypedDict):
    question: str
    category: str        # "factual" or "opinion"
    answer: str
    final_output: str

# ─── NODES ───────────────────────────────────────────────────────────────────

def classify_question(state: QuestionState) -> dict:
    """Classify the question as 'factual' or 'opinion'."""
    question = state["question"].lower()

    # Simple heuristic (in real code, use an LLM here)
    factual_triggers = ["what is", "who is", "when did", "how many", "define", "capital of"]
    is_factual = any(trigger in question for trigger in factual_triggers)

    category = "factual" if is_factual else "opinion"
    print(f"[classify] '{state['question'][:40]}...' → category: {category}")
    return {"category": category}

def simple_answer(state: QuestionState) -> dict:
    """Handle opinion/discussion questions directly."""
    print(f"[simple_answer] Providing opinion-based response...")
    answer = f"This is a subjective question. Regarding '{state['question']}': there are multiple valid perspectives depending on context and values."
    return {"answer": answer}

def research(state: QuestionState) -> dict:
    """Handle factual questions with a (mock) research step."""
    print(f"[research] Looking up factual information...")
    # In real code: call a search API or vector store
    answer = f"[RESEARCHED] Based on available information about '{state['question']}': this would contain verified factual data from reliable sources."
    return {"answer": answer}

def format_output(state: QuestionState) -> dict:
    """Format the final answer for display."""
    print(f"[format_output] Formatting answer...")
    output = f"Q: {state['question']}\nA ({state['category']}): {state['answer']}"
    return {"final_output": output}

# ─── ROUTER FUNCTION ─────────────────────────────────────────────────────────

# A router function:
#   - Takes state as its only argument
#   - Returns a STRING that is the name of the next node
#   - The string must match one of the keys in the routing map

def route_by_category(state: QuestionState) -> str:
    """Return the next node name based on question category."""
    if state["category"] == "factual":
        return "research"
    else:
        return "simple_answer"

# ─── BUILD GRAPH WITH CONDITIONAL EDGES ──────────────────────────────────────

builder = StateGraph(QuestionState)

builder.add_node("classify",      classify_question)
builder.add_node("simple_answer", simple_answer)
builder.add_node("research",      research)
builder.add_node("format_output", format_output)

builder.add_edge(START, "classify")

# add_conditional_edges(source_node, router_function, routing_map)
# routing_map maps return values to node names.
# If the router returns "research", go to the "research" node.
# If the router returns "simple_answer", go to the "simple_answer" node.
builder.add_conditional_edges(
    "classify",
    route_by_category,
    {
        "research":     "research",
        "simple_answer": "simple_answer",
    }
)

# Both paths converge at format_output
builder.add_edge("research",     "format_output")
builder.add_edge("simple_answer","format_output")
builder.add_edge("format_output", END)

qa_graph = builder.compile()

# ─── RUN BRANCHING EXAMPLE ───────────────────────────────────────────────────

print("=" * 60)
print("Example 1: Branching on question category")
print("=" * 60)

test_questions = [
    "What is the capital of France?",
    "What do you think about remote work?",
    "Who is the author of Python programming language?",
    "Which is better, coffee or tea?",
]

for question in test_questions:
    print(f"\n--- Question: '{question}'")
    state = qa_graph.invoke({
        "question": question,
        "category": "",
        "answer": "",
        "final_output": "",
    })
    print(state["final_output"])

# ─── EXAMPLE 2: LOOPS WITH CONDITIONAL EDGES ─────────────────────────────────
# Research with quality check: keep researching until quality is "good".

print("\n" + "=" * 60)
print("Example 2: Loop with quality check")
print("=" * 60)

class ResearchState(TypedDict):
    topic: str
    research_notes: list       # accumulates notes per research round
    quality_score: int         # 0-10; we want >= 7 to be "done"
    iteration: int
    final_report: str

def research_topic(state: ResearchState) -> dict:
    """Mock research step — each iteration adds more notes."""
    iteration = state["iteration"] + 1
    print(f"[research] Iteration {iteration}...")

    # Simulate finding more information each round
    new_note = f"Finding #{iteration}: Detail about '{state['topic']}' discovered in round {iteration}."
    updated_notes = state["research_notes"] + [new_note]

    return {
        "research_notes": updated_notes,
        "iteration": iteration,
    }

def evaluate_quality(state: ResearchState) -> dict:
    """Score the research quality based on how many notes we have."""
    note_count = len(state["research_notes"])
    # Quality improves with more research (capped at 10)
    quality = min(note_count * 3, 10)
    print(f"[evaluate_quality] Notes: {note_count}, Quality score: {quality}/10")
    return {"quality_score": quality}

def write_report(state: ResearchState) -> dict:
    """Compile research notes into a final report."""
    notes_text = "\n".join(f"  - {n}" for n in state["research_notes"])
    report = (
        f"RESEARCH REPORT: {state['topic']}\n"
        f"Iterations: {state['iteration']}\n"
        f"Quality: {state['quality_score']}/10\n"
        f"\nFindings:\n{notes_text}"
    )
    print("[write_report] Report complete.")
    return {"final_report": report}

# ─── LOOP ROUTER ─────────────────────────────────────────────────────────────

def check_quality(state: ResearchState) -> str:
    """Route to 'done' if quality is sufficient, else loop back to research."""
    if state["quality_score"] >= 7:
        print("[check_quality] Quality is sufficient — moving to write_report.")
        return "done"
    elif state["iteration"] >= 5:
        # Safety valve: prevent infinite loops
        print("[check_quality] Max iterations reached — writing report anyway.")
        return "done"
    else:
        print(f"[check_quality] Quality {state['quality_score']}/10 < 7 — research again.")
        return "research_again"

# ─── BUILD LOOP GRAPH ────────────────────────────────────────────────────────

loop_builder = StateGraph(ResearchState)

loop_builder.add_node("research",         research_topic)
loop_builder.add_node("evaluate_quality", evaluate_quality)
loop_builder.add_node("write_report",     write_report)

loop_builder.add_edge(START, "research")
loop_builder.add_edge("research", "evaluate_quality")

# Conditional edge with a LOOP: "research_again" routes BACK to "research"
loop_builder.add_conditional_edges(
    "evaluate_quality",
    check_quality,
    {
        "done":           "write_report",   # quality is good → write report
        "research_again": "research",       # quality is bad  → loop back
    }
)

loop_builder.add_edge("write_report", END)

loop_graph = loop_builder.compile()

# ─── RUN LOOP EXAMPLE ────────────────────────────────────────────────────────

print("\nRunning research loop for topic: 'quantum computing'")

loop_result = loop_graph.invoke({
    "topic": "quantum computing",
    "research_notes": [],
    "quality_score": 0,
    "iteration": 0,
    "final_report": "",
})

print("\n" + loop_result["final_report"])

# ─── END AS A CONDITIONAL TARGET ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("Using END as a conditional target:")
print("=" * 60)

# Sometimes you want to END early (e.g., invalid input → skip all processing).
# You can return END directly from a router.

class ValidationState(TypedDict):
    input_text: str
    is_valid: bool
    result: str

def validate_input(state: ValidationState) -> dict:
    is_valid = len(state["input_text"].strip()) > 10
    print(f"[validate] Input valid: {is_valid}")
    return {"is_valid": is_valid}

def process_input(state: ValidationState) -> dict:
    print("[process] Processing valid input...")
    return {"result": f"Processed: {state['input_text'].upper()}"}

def route_validation(state: ValidationState) -> str:
    # Return END (the string "END" / the constant) to skip processing
    return "process" if state["is_valid"] else END

val_builder = StateGraph(ValidationState)
val_builder.add_node("validate", validate_input)
val_builder.add_node("process",  process_input)
val_builder.add_edge(START, "validate")
val_builder.add_conditional_edges(
    "validate",
    route_validation,
    {
        "process": "process",
        END:       END,          # map the END constant to END
    }
)
val_builder.add_edge("process", END)

val_graph = val_builder.compile()

for test_input in ["Hi", "This is a long enough input to be valid"]:
    print(f"\nInput: '{test_input}'")
    result = val_graph.invoke({"input_text": test_input, "is_valid": False, "result": ""})
    print(f"Result: {result['result'] or '(skipped — invalid input)'}")

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Modify the question classifier graph to add a third category: "math".
#   If the question contains words like "calculate", "solve", "equation",
#   or numbers, route to a new "math_solver" node.
#   The math_solver node should return a mock answer like:
#   "Mathematical analysis: [result would be computed here]"

# Exercise 2:
#   Add a "max_iterations" key to ResearchState (default 3).
#   Modify check_quality so that instead of hardcoding 5 as the max,
#   it reads from state["max_iterations"].
#   Test with max_iterations=2 (should stop early even with low quality).

# Exercise 3 (Design challenge):
#   Design a content generation loop:
#   State: topic, draft, revision_count, feedback, approved
#   Nodes: generate_draft, review_draft, revise_draft, finalize
#   Router: after review_draft, route to "revise" if feedback is negative,
#           route to "finalize" if approved OR if revision_count >= 3.
#   Sketch out the TypedDict, all node signatures, and the router function.
