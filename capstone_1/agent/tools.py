"""
LangChain tools for the ShopPy customer support agent.

Three tools:
  - search_faq       : searches the FAQ dataset by keyword matching
  - get_order_status : looks up an order by ID
  - create_support_ticket : simulates ticket creation
"""

import json
import random
import string
from pathlib import Path

from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent.parent / "data"


def _load_faq() -> list[dict]:
    with open(_DATA_DIR / "faq.json", "r") as f:
        return json.load(f)


def _load_orders() -> list[dict]:
    with open(_DATA_DIR / "orders.json", "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Tool 1: FAQ search
# ---------------------------------------------------------------------------

@tool
def search_faq(query: str) -> str:
    """
    Search the ShopPy FAQ knowledge base for answers to common questions.

    Use this tool whenever a customer asks about policies, shipping, returns,
    payments, account issues, discount codes, or product availability.

    Args:
        query: The customer's question or a short description of the topic.

    Returns:
        The best matching FAQ answer, or a message indicating nothing was found.
    """
    faqs = _load_faq()
    query_lower = query.lower()

    # Score each FAQ entry by how many of its keywords appear in the query
    scores: list[tuple[int, dict]] = []
    for entry in faqs:
        score = sum(1 for kw in entry["keywords"] if kw in query_lower)
        # Also do a rough substring match on the question itself
        if any(word in entry["question"].lower() for word in query_lower.split()):
            score += 1
        scores.append((score, entry))

    scores.sort(key=lambda x: x[0], reverse=True)
    best_score, best_match = scores[0]

    if best_score == 0:
        return (
            "No FAQ entry found for that query. "
            "You may want to create a support ticket for further assistance."
        )

    return (
        f"FAQ: {best_match['question']}\n\n"
        f"Answer: {best_match['answer']}"
    )


# ---------------------------------------------------------------------------
# Tool 2: Order status lookup
# ---------------------------------------------------------------------------

@tool
def get_order_status(order_id: str) -> str:
    """
    Look up the status and details of a customer order by its order ID.

    Use this tool whenever a customer asks about an order, its shipping status,
    delivery date, tracking number, or what items they ordered.

    Args:
        order_id: The order ID string, e.g. "ORD-001". Case-insensitive.

    Returns:
        A formatted summary of the order, or an error message if not found.
    """
    orders = _load_orders()
    order_id_clean = order_id.strip().upper()

    for order in orders:
        if order["order_id"].upper() == order_id_clean:
            items_str = ", ".join(
                f"{item['name']} x{item['quantity']} (${item['price']:.2f})"
                for item in order["items"]
            )

            tracking_info = (
                f"Tracking: {order['tracking_number']} via {order['carrier']}"
                if order.get("tracking_number")
                else "Tracking: Not yet available"
            )

            delivery_info = (
                f"Estimated delivery: {order['estimated_delivery']}"
                if order.get("estimated_delivery")
                else "Estimated delivery: N/A"
            )

            return (
                f"Order ID: {order['order_id']}\n"
                f"Customer: {order['customer_name']}\n"
                f"Status: {order['status'].upper()}\n"
                f"Items: {items_str}\n"
                f"Order Total: ${order['total']:.2f}\n"
                f"{delivery_info}\n"
                f"{tracking_info}"
            )

    return (
        f"Order '{order_id}' was not found. "
        "Please double-check the order ID (format: ORD-001) and try again."
    )


# ---------------------------------------------------------------------------
# Tool 3: Support ticket creation
# ---------------------------------------------------------------------------

def _generate_ticket_id() -> str:
    """Generate a random ticket ID like TKT-A3F9B."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"TKT-{suffix}"


@tool
def create_support_ticket(issue: str, customer_email: str) -> str:
    """
    Create a support ticket for an issue that cannot be resolved by FAQ or order lookup.

    Use this tool when:
    - The customer has a complex complaint or problem.
    - The issue requires human review.
    - The customer explicitly asks to speak to a human or file a complaint.

    Args:
        issue: A short description of the customer's problem.
        customer_email: The customer's email address for follow-up.

    Returns:
        A confirmation message with the new ticket ID.
    """
    ticket_id = _generate_ticket_id()

    # In a real system this would write to a database or call a ticketing API.
    # Here we just log it to the console for demonstration.
    print(f"\n[TICKET CREATED] {ticket_id} | Email: {customer_email} | Issue: {issue}\n")

    return (
        f"Support ticket created successfully!\n"
        f"Ticket ID: {ticket_id}\n"
        f"We've logged your issue: \"{issue}\"\n"
        f"Our support team will contact you at {customer_email} within 24 hours.\n"
        f"Please save your ticket ID ({ticket_id}) for future reference."
    )
