# Lesson 6.2 — Built-in LangChain Tools: Web Search, Wikipedia, Calculator
# CONCEPT: Pre-built tools that give agents real-world capabilities
# KOTLIN EQUIVALENT: @Component beans that make HTTP calls to external APIs
# PHP EQUIVALENT: Laravel service classes injected into controllers/jobs

# ─── AVAILABLE BUILT-IN TOOLS ─────────────────────────────────────────────────
#
# LangChain comes with many pre-built tools:
#   TavilySearchResults    — AI-optimized web search (recommended, needs API key)
#   DuckDuckGoSearchRun    — Free web search, no API key needed (rate-limited)
#   WikipediaQueryRun      — Search Wikipedia
#   LLMMathChain           — Use LLM to solve math problems
#   PythonREPLTool         — Execute Python code (dangerous in production!)
#   FileManagementToolkit  — Read/write files
#   RequestsGetTool        — Make HTTP GET requests
#
# The LLM reads each tool's name and description to decide which to use.
# This means: GOOD DOCSTRINGS = BETTER AGENT BEHAVIOR

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain import hub
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Install: pip install langchain langchain-openai")

# ─── TOOL 1: TAVILY SEARCH ────────────────────────────────────────────────────
#
# TavilySearch is the recommended search tool for LangChain agents.
# It returns structured, LLM-friendly search results.
# Free tier: 1000 searches/month at https://tavily.com
#
# Kotlin: @Component class TavilySearchTool(val apiKey: String) : Tool {
#     override fun run(query: String): String = tavilyClient.search(query)
# }

def get_tavily_tool():
    """Return TavilySearchResults if API key is available, else None."""
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        return None
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        return TavilySearchResults(
            max_results=3,
            description=(
                "A web search engine. Use this to find current information, facts, news, "
                "or answers to questions about the real world. "
                "Input should be a search query string."
            ),
        )
    except ImportError:
        print("Install: pip install langchain-community tavily-python")
        return None

# ─── TOOL 2: DUCKDUCKGO SEARCH ────────────────────────────────────────────────
#
# DuckDuckGo search — no API key needed. Free but rate-limited.
# Good for development and learning.
# Install: pip install duckduckgo-search

def get_duckduckgo_tool():
    """Return DuckDuckGoSearchRun tool, or None if not installed."""
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        return DuckDuckGoSearchRun(
            description=(
                "A web search engine. Use this to find current information, news, or facts. "
                "Input should be a search query string."
            )
        )
    except ImportError:
        print("Install: pip install duckduckgo-search langchain-community")
        return None

# ─── TOOL 3: WIKIPEDIA ────────────────────────────────────────────────────────
#
# Wikipedia tool — searches Wikipedia and returns a summary.
# No API key needed.
# Install: pip install wikipedia

def get_wikipedia_tool():
    """Return WikipediaQueryRun tool, or None if not installed."""
    try:
        from langchain_community.tools import WikipediaQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper
        return WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(
                top_k_results=2,
                doc_content_chars_max=2000,  # Limit output length
            ),
            description=(
                "A wrapper around Wikipedia. Useful for looking up factual information, "
                "historical facts, definitions, and descriptions of people, places, and concepts. "
                "Input should be a search query."
            ),
        )
    except ImportError:
        print("Install: pip install wikipedia langchain-community")
        return None

# ─── TOOL 4: CALCULATOR ───────────────────────────────────────────────────────
#
# Simple math tool using eval() (demo only; use asteval/sympy in production)

if LANGCHAIN_AVAILABLE:
    from langchain_core.tools import tool

    @tool
    def calculator(expression: str) -> str:
        """
        Evaluates a mathematical expression and returns the result.
        Use for arithmetic, percentages, powers, and simple calculations.
        Examples: '2 + 2', '15 * 0.20', '100 / 4', '2 ** 10'
        """
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"{expression} = {result}"
        except Exception as e:
            return f"Could not evaluate '{expression}': {e}"

# ─── BUILD AGENT WITH SEARCH + WIKIPEDIA + CALCULATOR ────────────────────────

def build_research_agent(verbose: bool = True) -> "AgentExecutor | None":
    """
    Build an agent with web search, Wikipedia, and calculator.

    Automatically uses Tavily if TAVILY_API_KEY is set, otherwise DuckDuckGo.

    Kotlin:
        val tools = listOf(searchTool, wikipediaTool, calculatorTool)
        val agent = AgentExecutor(llm, tools, maxIterations=15)
    """
    if not LANGCHAIN_AVAILABLE:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY in week_06/.env")
        return None

    # Build tool list — try Tavily first, fall back to DuckDuckGo
    tools = []

    tavily = get_tavily_tool()
    if tavily:
        tools.append(tavily)
        print("Using Tavily search")
    else:
        ddg = get_duckduckgo_tool()
        if ddg:
            tools.append(ddg)
            print("TAVILY_API_KEY not set — falling back to DuckDuckGo")
        else:
            print("WARNING: No search tool available")

    wiki = get_wikipedia_tool()
    if wiki:
        tools.append(wiki)

    if LANGCHAIN_AVAILABLE:
        tools.append(calculator)

    if not tools:
        print("No tools available. Install: pip install langchain-community duckduckgo-search wikipedia")
        return None

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    print(f"Agent ready with {len(tools)} tools: {[t.name for t in tools]}")

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=15,
        handle_parsing_errors=True,
    )

# ─── DEMO ─────────────────────────────────────────────────────────────────────

def demo_multiple_tools():
    """
    Demonstrate an agent using multiple tools to answer a question.

    The agent decides:
    - Wikipedia: for factual/encyclopedic info
    - Search: for current/recent info
    - Calculator: for math
    """
    agent = build_research_agent(verbose=True)
    if not agent:
        return

    questions = [
        # Calculator only
        "What is 15% of 2500, and what is 2500 * 1.15?",
        # Wikipedia
        "According to Wikipedia, when was Python programming language first released?",
        # Combined: search + calculator
        "What is the current population of Malaysia? Then calculate how many people that is per square kilometer, given Malaysia's area is 329,847 km².",
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

# ─── INSPECT TOOL METADATA ────────────────────────────────────────────────────
#
# The LLM sees each tool's name and description.
# This is how it decides which tool to use.
# Always write clear, specific descriptions!

def show_tool_descriptions():
    """Print what the LLM sees for each tool."""
    tools = []
    for getter in [get_tavily_tool, get_duckduckgo_tool, get_wikipedia_tool]:
        t = getter()
        if t:
            tools.append(t)

    if LANGCHAIN_AVAILABLE:
        tools.append(calculator)

    print("Tools the LLM can choose from:")
    print("-" * 40)
    for t in tools:
        print(f"Name: {t.name}")
        print(f"Description: {t.description[:150]}...")
        print()

if __name__ == "__main__":
    print("Lesson 6.2 — Built-in Tools")
    print()
    show_tool_descriptions()
    print()
    demo_multiple_tools()

# ─── EXERCISES ────────────────────────────────────────────────────────────────
# EXERCISE 1:
#   Run the agent with both the Wikipedia tool and DuckDuckGo tool active.
#   Ask: "What programming language was Guido van Rossum working on before Python?"
#   Observe which tool the agent picks. Is it Wikipedia or DuckDuckGo? Why?
#
# EXERCISE 2:
#   Add a `date_tool` that returns today's date as a string.
#   The LLM often doesn't know the current date — give it this tool.
#   Hint:
#       from datetime import date
#       @tool
#       def get_today_date(dummy: str = "") -> str:
#           "Returns today's date. Input is ignored."
#           return str(date.today())
#   Test: "What day is today? Calculate how many days until December 31."
#
# EXERCISE 3:
#   Modify the agent to use max_iterations=3.
#   Ask a complex multi-step question that normally requires 4+ tool calls.
#   What happens? What does the agent output when it hits the limit?
#   Then restore max_iterations=15.
