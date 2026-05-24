#!/usr/bin/env python3
"""
Week 4 Project — Tool Chatbot
==============================
A CLI chatbot that uses OpenAI function calling to query a product catalogue.
The LLM decides which tool(s) to call based on the user's question.

Available tools:
  get_product(product_id)      — look up a product by numeric ID
  search_products(category)    — list products in a category
  list_all_products()          — show the entire catalogue

Tool call flow:
  User asks question → model requests tool(s) → we execute → model answers

Commands:
  /help    Show command list
  /quit    Exit
  /tools   Show available tools

Usage:
  cd week_04
  python project/tool_chatbot.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# ─── ENV SETUP ────────────────────────────────────────────────────────────────

_project_dir = Path(__file__).parent        # week_04/project/
_week_dir = _project_dir.parent             # week_04/
_data_dir = _week_dir / "data"
_products_file = _data_dir / "products.json"

try:
    from dotenv import load_dotenv
    load_dotenv(_week_dir / ".env")
    load_dotenv(_week_dir.parent / ".env")  # also try root
except ImportError:
    print("Error: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not found.")
    print(f"Create {_week_dir / '.env'} with: OPENAI_API_KEY=sk-...")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai not installed. Run: pip install openai")
    sys.exit(1)

# ─── LOAD PRODUCT DATA ────────────────────────────────────────────────────────

def load_products() -> dict[int, dict]:
    """Load products from JSON file, keyed by id."""
    if not _products_file.exists():
        print(f"Warning: {_products_file} not found. Using empty catalogue.")
        return {}
    raw = json.loads(_products_file.read_text(encoding="utf-8"))
    return {item["id"]: item for item in raw}


PRODUCTS: dict[int, dict] = load_products()

# ─── TOOL FUNCTIONS ──────────────────────────────────────────────────────────

def get_product(product_id: int) -> dict:
    """Look up a single product by its numeric ID."""
    product = PRODUCTS.get(int(product_id))
    if product is None:
        return {
            "error": f"Product with id {product_id} not found.",
            "available_ids": sorted(PRODUCTS.keys()),
        }
    return product


def search_products(category: str) -> dict:
    """Return all products in the specified category."""
    matches = [
        p for p in PRODUCTS.values()
        if p["category"].lower() == category.strip().lower()
    ]
    if not matches:
        categories = sorted({p["category"] for p in PRODUCTS.values()})
        return {
            "error": f"No products in category '{category}'.",
            "available_categories": categories,
        }
    return {
        "category": category,
        "count": len(matches),
        "products": matches,
    }


def list_all_products() -> dict:
    """Return the complete product catalogue."""
    if not PRODUCTS:
        return {"error": "Product catalogue is empty."}
    by_category: dict[str, list] = {}
    for product in PRODUCTS.values():
        cat = product["category"]
        by_category.setdefault(cat, []).append(product)
    return {
        "total": len(PRODUCTS),
        "categories": by_category,
    }


# ─── TOOL SCHEMAS ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_product",
            "description": (
                "Look up a specific product by its numeric ID. "
                "Use this when the user asks about a particular product or mentions an ID number."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "The numeric product ID (e.g. 1, 2, 3).",
                    }
                },
                "required": ["product_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Search for products by category. "
                "Use this when the user asks what products exist in a category like 'electronics' or 'office'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Product category name, e.g. 'electronics' or 'office'.",
                    }
                },
                "required": ["category"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_all_products",
            "description": (
                "List all products in the catalogue, grouped by category. "
                "Use this when the user wants a full overview or asks what's available."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
]

# Map tool name → Python function
TOOL_FUNCTIONS = {
    "get_product": get_product,
    "search_products": search_products,
    "list_all_products": list_all_products,
}

# ─── TOOL EXECUTION ───────────────────────────────────────────────────────────

def execute_tool_call(tool_call) -> str:
    """Execute a tool call from the model and return result as JSON string."""
    name = tool_call.function.name
    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return json.dumps({"error": f"Invalid arguments JSON: {tool_call.function.arguments}"})

    if name not in TOOL_FUNCTIONS:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        result = TOOL_FUNCTIONS[name](**arguments)
    except TypeError as e:
        result = {"error": f"Bad arguments for {name}: {e}"}
    except Exception as e:
        result = {"error": str(e)}

    return json.dumps(result, default=str)

# ─── CHAT LOOP ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a helpful product assistant for an online store. You have access to tools
that let you look up the product catalogue in real time.

Rules:
- Always use tools to get product data — never make up prices or availability.
- When listing multiple products, present them in a clear, readable format.
- If a product is out of stock, say so clearly and suggest checking back later.
- Be concise but helpful.
"""

HELP_TEXT = """
Available commands:
  /help    Show this help message
  /tools   List available tools and their descriptions
  /quit    Exit the chatbot

Sample questions to try:
  "What products do you have?"
  "Tell me about product 2"
  "Do you have any office furniture?"
  "Is the USB-C Hub in stock?"
  "What's the cheapest electronic item?"
"""

MODEL = "gpt-4o-mini"


def show_tools() -> None:
    """Print a summary of available tools."""
    print("\nAvailable tools:")
    for tool in TOOLS:
        fn = tool["function"]
        params = list(fn["parameters"].get("properties", {}).keys())
        param_str = f"({', '.join(params)})" if params else "()"
        print(f"  {fn['name']}{param_str}")
        print(f"    {fn['description']}\n")


def chat_with_tools(client: OpenAI, conversation: list[dict], verbose: bool = False) -> str:
    """
    Run the tool-call loop for one user turn.
    Modifies `conversation` in place, appending assistant and tool messages.
    Returns the final assistant text response.
    """
    iteration = 0
    while True:
        iteration += 1
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversation,
            tools=TOOLS,
            tool_choice="auto",
        )

        choice = response.choices[0]
        conversation.append(choice.message)

        if choice.finish_reason == "stop":
            return choice.message.content or ""

        if choice.finish_reason == "tool_calls":
            if verbose:
                print()
            for tc in choice.message.tool_calls:
                if verbose:
                    print(f"  [tool] {tc.function.name}({tc.function.arguments})")
                result_str = execute_tool_call(tc)
                if verbose:
                    result_preview = result_str[:120] + ("..." if len(result_str) > 120 else "")
                    print(f"  [result] {result_preview}")
                conversation.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                })
            continue

        # Unexpected finish reason — bail out
        return f"[Unexpected finish reason: {choice.finish_reason}]"


def main() -> None:
    client = OpenAI()

    # Build initial conversation with system prompt
    conversation: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    product_count = len(PRODUCTS)
    categories = sorted({p["category"] for p in PRODUCTS.values()})

    print("=" * 60)
    print("  Product Assistant — Week 4 Project")
    print("  Powered by OpenAI Function Calling")
    print("=" * 60)
    print(f"  Model:      {MODEL}")
    print(f"  Products:   {product_count} items in {len(categories)} categories")
    print(f"  Categories: {', '.join(categories)}")
    print("  Type /help for commands, /quit to exit")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        # ── Commands ──────────────────────────────────────────────────────────

        if user_input.lower() in ("/quit", "/exit"):
            print("Goodbye!")
            break

        elif user_input.lower() == "/help":
            print(HELP_TEXT)
            continue

        elif user_input.lower() == "/tools":
            show_tools()
            continue

        elif user_input.startswith("/"):
            print(f"  Unknown command: {user_input}. Type /help.\n")
            continue

        # ── Chat ──────────────────────────────────────────────────────────────

        conversation.append({"role": "user", "content": user_input})

        try:
            answer = chat_with_tools(client, conversation, verbose=True)
            print(f"\nAssistant: {answer}\n")
        except KeyboardInterrupt:
            print("\n  [Response interrupted]\n")
            # Remove the user message we just added since it wasn't answered
            conversation.pop()
        except Exception as e:
            print(f"\n  [Error: {e}]\n")
            conversation.pop()  # Remove unanswered user message


if __name__ == "__main__":
    main()
