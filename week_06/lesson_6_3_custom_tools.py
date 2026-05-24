# Lesson 6.3 — Custom Tools: @tool, StructuredTool, Pydantic Validation
# CONCEPT: Build your own tools that agents can call — from simple functions to complex APIs
# KOTLIN EQUIVALENT: @Component Tool classes with validated inputs
# PHP EQUIVALENT: Laravel Action classes with typed parameters

# ─── WHY CUSTOM TOOLS? ────────────────────────────────────────────────────────
#
# Built-in tools cover general tasks (search, Wikipedia).
# Custom tools let agents interact with YOUR systems:
#   - Your database
#   - Your internal APIs
#   - Business logic (pricing, scheduling, CRM lookups)
#   - File operations
#   - Third-party APIs
#
# The LLM READS the tool's name and docstring to decide when to use it.
# This is the most important thing to get right.
#
# Kotlin: @Component class PriceCalculatorTool : Tool {
#     override fun name() = "price_calculator"
#     override fun description() = "Calculates final price after discount and tax"
#     override fun run(input: String): String = ...
# }

import json
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain_core.tools import tool, StructuredTool
    from langchain import hub
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Install: pip install langchain langchain-openai")

# ─── METHOD 1: @tool DECORATOR (simplest) ────────────────────────────────────
#
# Best for: simple tools with a single string input
# The function's docstring becomes the tool's description.
# The LLM reads this docstring to decide when to call the tool.
#
# Kotlin: @Component class UppercaseTool : StringTool() { override fun run(s: String) = s.uppercase() }
# Laravel: class UppercaseAction { public function handle(string $text): string { return strtoupper($text); } }

if LANGCHAIN_AVAILABLE:
    @tool
    def get_weather(city: str) -> str:
        """
        Gets the current weather for a city.
        Use this when the user asks about weather conditions in any location.
        Input: the city name (e.g., 'Kuala Lumpur', 'Tokyo', 'New York').
        """
        # In a real implementation, call a weather API like OpenWeatherMap
        # Here we return mock data for demonstration
        mock_weather = {
            "kuala lumpur": "Sunny, 32°C, humidity 80%",
            "tokyo": "Partly cloudy, 22°C, humidity 60%",
            "london": "Rainy, 15°C, humidity 85%",
            "new york": "Clear, 18°C, humidity 55%",
        }
        city_lower = city.lower()
        if city_lower in mock_weather:
            return f"Weather in {city}: {mock_weather[city_lower]}"
        return f"Weather in {city}: Sunny, 28°C, humidity 70% (mock data)"

    @tool
    def get_current_time(timezone: str = "UTC") -> str:
        """
        Returns the current date and time.
        Use this when the user asks what time or date it is.
        Input: timezone name (e.g., 'UTC', 'Asia/Kuala_Lumpur', 'America/New_York').
        If unsure, use 'UTC'.
        """
        now = datetime.now()
        return f"Current time ({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S')}"

# ─── METHOD 2: STRUCTURED TOOL — MULTIPLE INPUTS ─────────────────────────────
#
# When a tool needs multiple inputs (not just a single string),
# use StructuredTool.from_function() with a Pydantic input schema.
#
# The LLM will output structured JSON arguments that match the schema.
#
# Kotlin: @Component class CurrencyTool(val baseCurrency: String, val targetCurrency: String, val amount: Double)
# Laravel: class ConvertCurrencyRequest extends FormRequest { public function rules(): array }

if LANGCHAIN_AVAILABLE:
    class CurrencyConvertInput(BaseModel):
        """Input schema for currency conversion.

        The LLM uses this to know what arguments to provide.
        Good field descriptions = LLM picks correct values.
        """
        amount: float = Field(..., description="The amount to convert (e.g., 100.0)")
        from_currency: str = Field(..., description="Source currency code (e.g., 'USD', 'MYR', 'EUR')")
        to_currency: str = Field(..., description="Target currency code (e.g., 'USD', 'MYR', 'EUR')")

    def _convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
        """
        Mock currency converter. In production: call an FX API like exchangerate-api.com.

        Kotlin: currencyClient.convert(ConvertRequest(amount, from, to))
        Laravel: Http::get('https://api.exchangerate.host/convert', [...])
        """
        # Mock exchange rates relative to USD
        rates = {
            "USD": 1.0, "MYR": 4.65, "EUR": 0.92, "GBP": 0.79,
            "JPY": 149.5, "SGD": 1.34, "AUD": 1.54, "CAD": 1.36,
        }
        from_c = from_currency.upper()
        to_c = to_currency.upper()

        if from_c not in rates:
            return f"Unknown currency: {from_currency}"
        if to_c not in rates:
            return f"Unknown currency: {to_currency}"

        # Convert via USD as intermediate
        usd_amount = amount / rates[from_c]
        target_amount = usd_amount * rates[to_c]

        return (
            f"{amount} {from_c} = {target_amount:.4f} {to_c} "
            f"(rate: 1 {from_c} = {rates[to_c]/rates[from_c]:.4f} {to_c})"
        )

    currency_converter = StructuredTool.from_function(
        func=_convert_currency,
        name="currency_converter",
        description=(
            "Converts an amount from one currency to another. "
            "Use this for any currency conversion questions. "
            "Supports: USD, MYR, EUR, GBP, JPY, SGD, AUD, CAD."
        ),
        args_schema=CurrencyConvertInput,
    )

# ─── METHOD 3: TOOL THAT READS FROM A JSON "DATABASE" ─────────────────────────
#
# Demonstrates a tool that looks up structured data.
# In production: replace the JSON file with a real DB query.
#
# Kotlin: @Component class ProductLookupTool(val productRepo: ProductRepository)
# Laravel: class ProductLookupAction { public function handle(string $sku): string }

# In-memory "product database" (simulates reading from a file or DB)
PRODUCT_DB = {
    "LAPTOP-001": {"name": "ProBook X1", "price": 3500.00, "stock": 15, "category": "Laptops"},
    "PHONE-002": {"name": "Galaxy S24", "price": 2800.00, "stock": 42, "category": "Phones"},
    "MOUSE-003": {"name": "LogiFlow M3", "price": 89.00, "stock": 200, "category": "Accessories"},
    "MONITOR-004": {"name": "UltraWide 34", "price": 1200.00, "stock": 8, "category": "Monitors"},
}

if LANGCHAIN_AVAILABLE:
    @tool
    def lookup_product(sku: str) -> str:
        """
        Looks up a product in the inventory database by its SKU.
        Returns the product name, price (in MYR), and current stock level.
        Input: the product SKU code (e.g., 'LAPTOP-001', 'PHONE-002').
        If the SKU is not found, returns a not-found message.
        """
        sku_upper = sku.strip().upper()
        product = PRODUCT_DB.get(sku_upper)
        if not product:
            available = ", ".join(PRODUCT_DB.keys())
            return f"Product '{sku}' not found. Available SKUs: {available}"
        return (
            f"SKU: {sku_upper} | Name: {product['name']} | "
            f"Price: MYR {product['price']:.2f} | Stock: {product['stock']} units"
        )

    @tool
    def list_products_by_category(category: str) -> str:
        """
        Lists all products in a given category.
        Input: category name (e.g., 'Laptops', 'Phones', 'Accessories', 'Monitors').
        Returns product SKUs and names in that category.
        """
        cat_lower = category.lower()
        matches = [
            f"{sku}: {p['name']} (MYR {p['price']:.2f})"
            for sku, p in PRODUCT_DB.items()
            if p["category"].lower() == cat_lower
        ]
        if not matches:
            categories = list({p["category"] for p in PRODUCT_DB.values()})
            return f"No products found in '{category}'. Available categories: {categories}"
        return f"Products in {category}:\n" + "\n".join(matches)

# ─── ERROR HANDLING IN TOOLS ──────────────────────────────────────────────────
#
# Two approaches for tool errors:
#
# Option A: Return an error string — agent sees the error and tries to recover
# Option B: Raise an exception — agent sees "Tool execution error" and may retry
#
# Recommendation: Return error strings. The agent can understand and react to them.
# Raising exceptions is harder for the agent to handle gracefully.
#
# Kotlin: return "Error: $message" vs throw RuntimeException(message)
# Laravel: return "Error: $message" vs throw new ToolException($message)

if LANGCHAIN_AVAILABLE:
    @tool
    def divide_numbers(expression: str) -> str:
        """
        Divides two numbers. Input format: 'numerator / denominator' (e.g., '10 / 2').
        Returns the result or an error message if division by zero.
        """
        try:
            parts = expression.split("/")
            if len(parts) != 2:
                return f"Invalid format. Use: 'number / number'. Got: '{expression}'"
            numerator = float(parts[0].strip())
            denominator = float(parts[1].strip())
            if denominator == 0:
                # Return error string — agent can understand "division by zero"
                return "Error: Cannot divide by zero. Please provide a non-zero denominator."
            return f"{numerator} / {denominator} = {numerator / denominator}"
        except ValueError as e:
            return f"Error: Could not parse numbers from '{expression}'. Details: {e}"

# ─── BUILD AGENT WITH ALL CUSTOM TOOLS ───────────────────────────────────────

def build_custom_tools_agent(verbose: bool = True):
    """Build an agent equipped with all our custom tools."""
    if not LANGCHAIN_AVAILABLE:
        return None
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in week_06/.env")
        return None

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [
        get_weather,
        get_current_time,
        currency_converter,
        lookup_product,
        list_products_by_category,
        divide_numbers,
    ]
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    print(f"Custom agent ready with tools: {[t.name for t in tools]}")

    return AgentExecutor(
        agent=agent, tools=tools, verbose=verbose,
        max_iterations=10, handle_parsing_errors=True,
    )

# ─── DEMO ─────────────────────────────────────────────────────────────────────

def demo_custom_tools():
    agent = build_custom_tools_agent(verbose=True)
    if not agent:
        return

    questions = [
        "What's the weather like in Kuala Lumpur?",
        "Convert 500 USD to MYR",
        "Look up product LAPTOP-001. What is its price in USD? (1 USD = 4.65 MYR)",
        "List all products in the Phones category",
        "What is the current time?",
    ]

    for q in questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        print('='*60)
        try:
            result = agent.invoke({"input": q})
            print(f"\nAnswer: {result['output']}")
        except Exception as e:
            print(f"Error: {e}")

# ─── BEST PRACTICES SUMMARY ───────────────────────────────────────────────────
#
# 1. CLEAR NAMES: Use descriptive names. "lookup_product" > "get_data"
#    The LLM uses the name to decide which tool to call.
#
# 2. SPECIFIC DOCSTRINGS: Tell the LLM exactly when and how to use the tool.
#    "Use this for..." and "Input should be..." are crucial phrases.
#
# 3. HANDLE ERRORS GRACEFULLY: Return error strings, not exceptions.
#    The agent needs to read the error to recover.
#
# 4. LIMIT SCOPE: Each tool should do ONE thing well.
#    Don't make a "do_everything" tool.
#
# 5. VALIDATE INPUTS: Use Pydantic schemas for complex inputs.
#    The LLM might pass wrong types; validate and return a clear error.

if __name__ == "__main__":
    print("Lesson 6.3 — Custom Tools")
    print()
    demo_custom_tools()

# ─── EXERCISES ────────────────────────────────────────────────────────────────
# EXERCISE 1:
#   Create a @tool called `calculate_discount` that takes:
#       original_price: float and discount_percentage: float
#   Returns the discounted price and the amount saved.
#   Example input format: "500.00, 20" → "Discounted price: 400.00 MYR (saved: 100.00 MYR)"
#   Hint: Use StructuredTool with a Pydantic schema for the two-argument input.
#
# EXERCISE 2:
#   Create a @tool called `check_stock` that takes a SKU and a quantity,
#   and returns whether there's enough stock for the order.
#   Use the PRODUCT_DB above.
#   The LLM should be able to ask "Can I order 20 units of LAPTOP-001?"
#
# EXERCISE 3:
#   Intentionally write a tool with a BAD docstring (vague, no usage instructions).
#   Then test: does the agent use it correctly?
#   Then fix the docstring and test again.
#   Write your observations as comments. This teaches you why docstrings matter.
