# Lesson 7.4 — Human-in-the-Loop
# CONCEPT: LangGraph can PAUSE execution before a specified node, letting a
#           human review the current state, make changes, and then resume.
#           This is critical for AI workflows involving irreversible actions
#           (sending emails, making purchases, deleting data, etc.).
#
# KOTLIN EQUIVALENT: Like a coroutine that suspends at a checkpoint, publishes
#                    its state to a review queue, then resumes when a human
#                    sends an approval event. Similar to a saga with a manual
#                    confirmation step in an event-driven architecture.
#
# PHP EQUIVALENT: Like a queued job that pauses itself, stores state in Redis,
#                 notifies a reviewer, and only continues when a webhook
#                 arrives with approval. Similar to a Laravel workflow with
#                 manual approval gates.

# ─── IMPORTS ─────────────────────────────────────────────────────────────────

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# ─── WHY HUMAN-IN-THE-LOOP? ──────────────────────────────────────────────────

# AI should NOT autonomously perform:
#   - Sending emails or messages to real people
#   - Making financial transactions
#   - Deleting or overwriting important data
#   - Posting to social media
#   - Any action that is hard or impossible to undo
#
# The pattern:
#   1. AI generates a DRAFT of the action (e.g., writes an email)
#   2. Graph PAUSES — execution stops before the "send" node
#   3. Human REVIEWS the draft in the current state
#   4. Human can EDIT the state (change the email content)
#   5. Human RESUMES — graph continues from where it paused
#   6. Graph EXECUTES the action (sends the email)

# ─── MEMOSAVER — THE CHECKPOINTER ────────────────────────────────────────────

# A checkpointer persists the graph state between runs.
# MemorySaver stores state in RAM (use SqliteSaver/RedisSaver in production).
# Without a checkpointer, you can't resume a paused graph.

checkpointer = MemorySaver()

# ─── STATE DEFINITION ────────────────────────────────────────────────────────

class EmailState(TypedDict):
    # Input
    recipient: str
    topic: str

    # Drafted by AI
    subject: str
    body: str

    # Set by human or auto-approved
    approved: bool
    human_notes: str      # optional notes the human can add

    # Final result
    send_status: str

# ─── NODES ───────────────────────────────────────────────────────────────────

def draft_email(state: EmailState) -> dict:
    """AI drafts the email subject and body."""
    print(f"[draft_email] Drafting email to {state['recipient']} about '{state['topic']}'...")

    # In real code: call an LLM here
    subject = f"Following up on: {state['topic']}"
    body = (
        f"Dear {state['recipient']},\n\n"
        f"I wanted to follow up regarding {state['topic']}. "
        f"This is an AI-drafted message and requires your review before sending.\n\n"
        f"Please let me know if you have any questions.\n\n"
        f"Best regards,\nYour AI Assistant"
    )

    print(f"[draft_email] Draft ready. Subject: '{subject}'")
    return {
        "subject": subject,
        "body": body,
        "approved": False,
    }

def human_review(state: EmailState) -> dict:
    """
    THIS NODE IS THE INTERRUPT POINT.
    In interrupt_before mode, the graph PAUSES BEFORE running this node.
    The human reviews state BEFORE this node executes.
    When the human resumes, this node then runs.
    """
    # After the human has reviewed and updated the state (externally),
    # this node just logs that review is complete.
    print(f"[human_review] Human review completed. Approved: {state['approved']}")
    if state["human_notes"]:
        print(f"[human_review] Human notes: {state['human_notes']}")
    return {}  # no state changes needed here

def route_after_review(state: EmailState) -> str:
    """Route to send_email if approved, else to revise_email."""
    if state["approved"]:
        return "send_email"
    else:
        return "revise_email"

def revise_email(state: EmailState) -> dict:
    """AI revises the email based on human notes."""
    print(f"[revise_email] Revising based on notes: '{state['human_notes']}'...")
    revised_body = (
        f"{state['body']}\n\n"
        f"[REVISED based on feedback: {state['human_notes']}]"
    )
    return {
        "body": revised_body,
        "approved": True,   # auto-approve after revision for simplicity
    }

def send_email(state: EmailState) -> dict:
    """Actually send the email (mock)."""
    print(f"[send_email] Sending email...")
    print(f"  To:      {state['recipient']}")
    print(f"  Subject: {state['subject']}")
    print(f"  Body:    {state['body'][:80]}...")
    # In real code: call SendGrid / SMTP here
    return {"send_status": "sent_successfully"}

# ─── BUILD THE GRAPH WITH INTERRUPT ──────────────────────────────────────────

builder = StateGraph(EmailState)

builder.add_node("draft_email",   draft_email)
builder.add_node("human_review",  human_review)
builder.add_node("revise_email",  revise_email)
builder.add_node("send_email",    send_email)

builder.add_edge(START, "draft_email")
builder.add_edge("draft_email", "human_review")

# Conditional: approved → send, not approved → revise → send
builder.add_conditional_edges(
    "human_review",
    route_after_review,
    {
        "send_email":   "send_email",
        "revise_email": "revise_email",
    }
)
builder.add_edge("revise_email", "send_email")
builder.add_edge("send_email", END)

# CRITICAL: pass the checkpointer AND specify interrupt_before.
# interrupt_before=["human_review"] means the graph PAUSES before
# running the "human_review" node.
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"],
)

# ─── THREAD CONFIG — MULTI-USER SUPPORT ──────────────────────────────────────

# Each conversation/user gets a unique thread_id.
# The checkpointer uses this to store separate states for each thread.
# This is how you support multiple users simultaneously.

config_user_1 = {"configurable": {"thread_id": "user-alice-001"}}
config_user_2 = {"configurable": {"thread_id": "user-bob-002"}}

# ─── DEMO: APPROVED PATH ─────────────────────────────────────────────────────

print("=" * 60)
print("DEMO 1: Human approves the email draft")
print("=" * 60)

initial_state: EmailState = {
    "recipient":   "client@example.com",
    "topic":       "Project Status Update",
    "subject":     "",
    "body":        "",
    "approved":    False,
    "human_notes": "",
    "send_status": "",
}

# ── FIRST RUN: Graph executes until interrupt ──
print("\nStep 1: Starting graph (will pause at human_review)...")
# When the graph hits interrupt_before=["human_review"], it STOPS and returns.
# The returned state is whatever the state looks like AFTER draft_email ran.
state_at_pause = graph.invoke(initial_state, config_user_1)

print(f"\nGraph paused. Current draft:")
print(f"  Subject: {state_at_pause['subject']}")
print(f"  Body preview: {state_at_pause['body'][:100]}...")
print(f"  Approved: {state_at_pause['approved']}")

# ── HUMAN REVIEW STEP ──
print("\nStep 2: Human reviewing the draft...")
print("(Simulating human decision: APPROVE)")

# The human updates the state by calling graph.update_state().
# This modifies the persisted checkpoint for this thread.
graph.update_state(
    config_user_1,
    {
        "approved": True,
        "human_notes": "Looks good, approved as-is.",
    }
)

# ── SECOND RUN: Resume from checkpoint ──
print("\nStep 3: Resuming graph (human approved)...")
# Passing None as the first arg tells LangGraph: "don't add new input,
# just resume from the saved checkpoint."
final_state = graph.invoke(None, config_user_1)
print(f"\nFinal send status: {final_state['send_status']}")

# ─── DEMO: REJECTION PATH ────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("DEMO 2: Human rejects and requests revision")
print("=" * 60)

print("\nStep 1: Starting graph for user Bob (will pause at human_review)...")
state_at_pause_2 = graph.invoke(initial_state, config_user_2)

print(f"\nGraph paused. Subject: '{state_at_pause_2['subject']}'")

print("\nStep 2: Human rejecting draft with notes...")
graph.update_state(
    config_user_2,
    {
        "approved": False,
        "human_notes": "Too formal. Make it more friendly and add a deadline.",
    }
)

print("\nStep 3: Resuming (human rejected — will revise then send)...")
final_state_2 = graph.invoke(None, config_user_2)
print(f"\nFinal send status: {final_state_2['send_status']}")

# ─── INSPECTING CHECKPOINTED STATE ───────────────────────────────────────────

print("\n" + "=" * 60)
print("Inspecting checkpointed state for both threads:")
print("=" * 60)

for label, config in [("Alice", config_user_1), ("Bob", config_user_2)]:
    snapshot = graph.get_state(config)
    print(f"\n{label}'s final state:")
    print(f"  send_status  : {snapshot.values.get('send_status')}")
    print(f"  approved     : {snapshot.values.get('approved')}")
    print(f"  human_notes  : {snapshot.values.get('human_notes')}")

# ─── PATTERN SUMMARY ─────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Human-in-the-Loop Pattern Summary:")
print("=" * 60)
steps = [
    "1. compile(checkpointer=..., interrupt_before=['node_name'])",
    "2. graph.invoke(initial_state, config)  → pauses, returns state",
    "3. Human reads current state (graph.get_state(config))",
    "4. Human updates state (graph.update_state(config, new_values))",
    "5. graph.invoke(None, config)           → resumes from checkpoint",
    "6. Thread ID in config separates different users/sessions",
]
for step in steps:
    print(f"  {step}")

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Add a second interrupt point: interrupt_before=["human_review", "send_email"].
#   Now the human gets TWO chances to review: once to approve the draft,
#   and once more right before it actually sends.
#   Test both the approve-approve and approve-cancel paths.

# Exercise 2:
#   Add a "revision_count" key to EmailState (starts at 0).
#   revise_email should increment it.
#   If revision_count >= 2 and the human still hasn't approved,
#   route to a new "escalate" node instead of revise_email.
#   escalate should set send_status = "escalated_to_manager".

# Exercise 3 (Architecture question):
#   You're building a travel booking agent that:
#     1. Searches for flights and hotels
#     2. Selects the best options
#     3. Books them (charges a credit card — irreversible!)
#   At which node(s) would you add interrupt_before?
#   What keys would you put in the TypedDict?
#   What would the human see at the interrupt, and what can they change?
