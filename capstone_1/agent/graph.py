"""
LangGraph agent for ShopPy customer support.

Uses `create_react_agent` (prebuilt ReAct loop) with three custom tools.
The graph is stateful: it tracks messages across turns via session history
managed by the FastAPI layer.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agent.tools import search_faq, get_order_status, create_support_ticket

load_dotenv()

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a helpful and friendly customer support agent for ShopPy, a modern online store.

Your job is to assist customers with:
- Questions about shipping, returns, payments, and store policies (use the search_faq tool)
- Order status and tracking inquiries (use the get_order_status tool)
- Creating support tickets for complex issues (use the create_support_ticket tool)

Guidelines:
- Always be polite, concise, and empathetic.
- Use the appropriate tool before answering — don't guess at policies or order details.
- If you cannot resolve an issue with the available tools, offer to create a support ticket.
- If the customer asks something completely unrelated to shopping or orders, politely redirect them.
- When asking for an order ID, remind the customer it has the format ORD-001.
"""

# ---------------------------------------------------------------------------
# Tools list
# ---------------------------------------------------------------------------

TOOLS = [search_faq, get_order_status, create_support_ticket]


# ---------------------------------------------------------------------------
# Public factory function
# ---------------------------------------------------------------------------

def create_agent():
    """
    Create and return a compiled LangGraph ReAct agent.

    The agent is stateless from LangGraph's perspective — conversation history
    is passed in as the `messages` list on every invocation. The FastAPI layer
    maintains session state.

    Returns:
        A compiled LangGraph graph (runnable via .invoke() or .stream()).
    """
    model_name = os.getenv("MODEL", "gpt-4o-mini")

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT,
    )

    return agent
