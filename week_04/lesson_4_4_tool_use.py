# Lesson 4.4 — OpenAI Tool Use (Function Calling)
# Python for AI Engineers | Week 4
#
# CONCEPT:
#   Tool use (function calling) lets the LLM request that your code executes
#   a function and returns the result. The LLM never runs code itself — it just
#   says "call get_product with id=3" and you do it, returning the result.
#   This bridges the gap between static LLM knowledge and live data.
#
# KOTLIN EQUIVALENT:
#   Like defining an interface the AI can call — the LLM is the client,
#   your function is the implementation.
#   Similar to defining @FunctionDefinition in Spring AI or
#   @Tool in LangChain4j.
#
# PHP EQUIVALENT:
#   Like an OpenAPI spec the LLM reads to know which endpoints exist,
#   then your controller handles execution. The LLM picks the route,
#   PHP runs the code.

from __future__ import annotations

import os
import json
from pathlib import Path
from dotenv import load_dotenv

_this_dir = Path(__file__).parent
load_dotenv(_this_dir / ".env")
load_dotenv(_this_dir.parent / ".env")   # also check root

_HAS_KEY = bool(os.getenv("OPENAI_API_KEY"))
if not _HAS_KEY:
    print("WARNING: OPENAI_API_KEY not set. Live examples will be skipped.")
    print("Add OPENAI_API_KEY to your .env file.\n")

# ─── THE TOOL USE FLOW ────────────────────────────────────────────────────────

# 1. You define tools as JSON schemas in the `tools` parameter.
# 2. You send: messages + tools → OpenAI API.
# 3. Model response may contain `tool_calls` instead of (or with) text.
# 4. You execute the function(s) specified in tool_calls.
# 5. You append the tool result as a message with role="tool".
# 6. You call the API again — the model uses the result to form its answer.
#
#  User message + tool defs
#         ↓
#   [OpenAI API]
#         ↓
#   tool_calls: [{id, name, arguments}]
#         ↓
#   Your code executes the function
#         ↓
#   Append tool result → call API again
#         ↓
#   [OpenAI API] → final human-readable answer


# ─── DEFINING TOOL SCHEMAS ───────────────────────────────────────────────────

# A tool is a dict with type="function" and a function definition.
# The function definition is a JSON Schema describing name, description, parameters.
# The description is crucial — the LLM reads it to decide when to call the tool.

PRODUCTS_DB: dict[int, dict] = {
    1: {"id": 1, "name": "Wireless Headphones", "price": 79.99, "category": "electronics", "in_stock": True},
    2: {"id": 2, "name": "Mechanical Keyboard", "price": 149.99, "category": "electronics", "in_stock": False},
    3: {"id": 3, "name": "Standing Desk Mat",   "price": 45.00, "category": "office",       "in_stock": True},
    4: {"id": 4, "name": "Ergonomic Chair",      "price": 399.00,"category": "office",       "in_stock": True},
    5: {"id": 5, "name": "USB-C Hub",            "price": 35.99, "category": "electronics", "in_stock": True},
}

# Tool definitions — these are passed to the API as-is
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_product",
            "description": (
                "Look up a product by its numeric ID. "
                "Returns product name, price, category, and stock status."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "The unique numeric ID of the product (e.g. 1, 2, 3).",
                    }
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Search for products by category. "
                "Returns a list of matching products with names and prices."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Product category to filter by (e.g. 'electronics', 'office').",
                    }
                },
                "required": ["category"],
            },
        },
    },
]


# ─── IMPLEMENTING THE ACTUAL FUNCTIONS ───────────────────────────────────────

# These are your real functions — the LLM never runs these directly.
# You call them when the LLM requests it, then send the result back.

def get_product(product_id: int) -> dict:
    """Look up a product by ID. Returns the product or an error dict."""
    product = PRODUCTS_DB.get(product_id)
    if product is None:
        return {"error": f"Product with id {product_id} not found"}
    return product


def search_products(category: str) -> dict:
    """Return all products in a given category."""
    matches = [p for p in PRODUCTS_DB.values() if p["category"].lower() == category.lower()]
    if not matches:
        return {"error": f"No products found in category '{category}'"}
    return {"category": category, "count": len(matches), "products": matches}


# Dispatcher: maps function name → actual Python function
FUNCTION_MAP = {
    "get_product": get_product,
    "search_products": search_products,
}


def execute_tool_call(tool_call) -> str:
    """
    Execute a single tool call from the API response.
    Returns the result as a JSON string (required by the OpenAI API).
    """
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)   # API sends args as JSON string

    if name not in FUNCTION_MAP:
        result = {"error": f"Unknown function: {name}"}
    else:
        try:
            result = FUNCTION_MAP[name](**arguments)
        except Exception as e:
            result = {"error": str(e)}

    return json.dumps(result)


# ─── SINGLE TOOL CALL EXAMPLE ────────────────────────────────────────────────

if _HAS_KEY:
    from openai import OpenAI
    client = OpenAI()

    print("=== Single tool call example ===\n")

    messages = [
        {"role": "user", "content": "What is the price of product #3?"}
    ]

    # Step 1: Send message + tools to the API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",   # let the model decide when to use tools
    )

    message = response.choices[0].message
    print(f"Model response type: {response.choices[0].finish_reason}")
    # finish_reason = "tool_calls" means the model wants to call a function

    if message.tool_calls:
        for tc in message.tool_calls:
            print(f"  Tool requested: {tc.function.name}({tc.function.arguments})")

        # Step 2: Execute all requested tool calls
        messages.append(message)   # append the assistant's tool_call request

        for tc in message.tool_calls:
            tool_result = execute_tool_call(tc)
            print(f"  Tool result: {tool_result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_result,
            })

        # Step 3: Send tool results back — get final answer
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
        )
        print(f"\nFinal answer: {final_response.choices[0].message.content}\n")


# ─── FULL TOOL CALL LOOP ─────────────────────────────────────────────────────

# Production pattern: keep looping until finish_reason != "tool_calls"
# The model may request multiple rounds of tool calls before answering.

def run_tool_loop(user_message: str, verbose: bool = True) -> str:
    """
    Send a user message and handle tool calls in a loop until the model
    produces a final text response.
    """
    if not _HAS_KEY:
        return "[API key not set — skipping live example]"

    from openai import OpenAI
    client = OpenAI()

    messages = [{"role": "user", "content": user_message}]
    iteration = 0

    while True:
        iteration += 1
        if verbose:
            print(f"  [loop iteration {iteration}]")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        choice = response.choices[0]
        messages.append(choice.message)

        if choice.finish_reason == "stop":
            # Model gave a final text response — we're done
            return choice.message.content

        if choice.finish_reason == "tool_calls":
            # Execute all requested tool calls and append results
            for tc in choice.message.tool_calls:
                result = execute_tool_call(tc)
                if verbose:
                    print(f"    Called: {tc.function.name}({tc.function.arguments})")
                    print(f"    Result: {result}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
            # Continue loop — model will process the tool results
            continue

        # Unexpected finish reason
        break

    return "[Unexpected end of tool loop]"


if _HAS_KEY:
    print("=== Tool loop: product search ===\n")
    answer = run_tool_loop("Which office products do you have?")
    print(f"\nAnswer: {answer}\n")

    print("=== Tool loop: out of stock check ===\n")
    answer = run_tool_loop("Is the Mechanical Keyboard available? What's its price?")
    print(f"\nAnswer: {answer}\n")


# ─── MULTIPLE TOOLS EXAMPLE ──────────────────────────────────────────────────

# Add a weather tool to show the model choosing between tools

WEATHER_DB: dict[str, dict] = {
    "kuala lumpur": {"temp_c": 32, "condition": "Partly cloudy", "humidity": 78},
    "london":        {"temp_c": 14, "condition": "Overcast",      "humidity": 82},
    "new york":      {"temp_c": 22, "condition": "Sunny",         "humidity": 45},
}

MULTI_TOOLS = TOOLS + [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'Kuala Lumpur', 'London'",
                    }
                },
                "required": ["city"],
            },
        },
    },
]


def get_weather(city: str) -> dict:
    """Return weather for a city."""
    data = WEATHER_DB.get(city.lower())
    if data is None:
        return {"error": f"No weather data for '{city}'"}
    return {"city": city, **data}


MULTI_FUNCTION_MAP = {**FUNCTION_MAP, "get_weather": get_weather}

print("Tool schema preview (get_product):")
print(json.dumps(TOOLS[0]["function"], indent=2))


# ─── PARALLEL TOOL CALLS ─────────────────────────────────────────────────────

# Modern OpenAI models can request MULTIPLE tool calls in a single response.
# The tool_calls list may contain 2+ items — execute all of them.

# Example: "What's the price of product 1 and product 2?"
# Model may return: tool_calls = [get_product(1), get_product(2)]
# You execute both, append both results, then call the API once more.

# This is already handled in execute_tool_call + run_tool_loop above —
# the `for tc in choice.message.tool_calls` loop handles all of them.


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 — ADD A NEW TOOL
#   Add a third tool: `get_low_stock_products()` (no parameters) that returns
#   all products where in_stock is False. Add the tool schema to TOOLS,
#   implement the function, add it to FUNCTION_MAP, and test it with a message
#   like "Which products are out of stock right now?"

# Exercise 2 — TOOL CALL WITHOUT LIVE API
#   Write a `mock_tool_loop(user_message, mock_tool_response)` function that
#   simulates the tool call flow WITHOUT actually calling OpenAI. It should:
#   1. Pretend the model requested a tool call with mock_tool_response as arguments.
#   2. Execute the real function (get_product or search_products).
#   3. Print what the final answer would be based on the tool result.
#   This is useful for testing your tool implementations without API costs.

# Exercise 3 — STRUCTURED OUTPUT TOOL
#   Create a tool called `classify_intent(user_message: str)` that returns
#   a structured dict: {"intent": "...", "confidence": 0.0-1.0, "entities": []}.
#   Instead of implementing this as Python code, write a prompt that asks the
#   LLM to fill in the structure, and call it using tool_choice="required" to
#   force the model to always call the tool (structured output via function calling).
