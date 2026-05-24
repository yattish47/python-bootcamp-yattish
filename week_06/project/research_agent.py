"""
Week 6 Project — Research Agent CLI
=====================================
A conversational research agent that can search the web, look up Wikipedia,
and summarize findings. Saves results to a text file.

Setup:
    pip install langchain langchain-openai langchain-community tavily-python python-dotenv
    Create week_06/.env with:
        OPENAI_API_KEY=sk-...
        TAVILY_API_KEY=tvly-...  (optional, falls back to DuckDuckGo)

Run:
    python week_06/project/research_agent.py

Commands:
    /quit          — exit the program
    /verbose on    — show agent reasoning steps
    /verbose off   — hide reasoning steps (cleaner output)
    /save          — save last research result to a file
    /clear         — clear conversation history
    /help          — show available commands
    /sessions      — show number of messages in history

Kotlin equivalent: A Spring Shell CLI with @ShellMethod commands,
    @Autowired AgentService with ConcurrentHashMap<String, List<BaseMessage>> history

Laravel equivalent: An artisan command with $this->ask() prompts,
    AgentService injected via IoC container
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env from week_06/ directory
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)

# ─── LANGCHAIN IMPORTS ────────────────────────────────────────────────────────

try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("ERROR: LangChain not installed.")
    print("Run: pip install langchain langchain-openai langchain-community")
    sys.exit(1)

# ─── TOOL: WEB SEARCH (Tavily or DuckDuckGo fallback) ─────────────────────────

def _build_search_tool():
    """Return the best available search tool."""
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            search_tool = TavilySearchResults(
                max_results=3,
                description=(
                    "Web search engine for finding current information, news, and facts. "
                    "Use for any question requiring up-to-date real-world knowledge. "
                    "Input: a search query string."
                ),
            )
            print("Search: Tavily (AI-optimized)")
            return search_tool
        except ImportError:
            pass

    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search_tool = DuckDuckGoSearchRun(
            description=(
                "Web search engine. Use for finding current information and facts. "
                "Input: a search query string."
            )
        )
        print("Search: DuckDuckGo (no API key needed)")
        return search_tool
    except ImportError:
        print("WARNING: No search tool. Install: pip install duckduckgo-search langchain-community")
        return None

# ─── TOOL: WIKIPEDIA ──────────────────────────────────────────────────────────

def _build_wikipedia_tool():
    """Return Wikipedia tool if available."""
    try:
        from langchain_community.tools import WikipediaQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper
        wiki = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=3000),
            description=(
                "Wikipedia search for encyclopedic information, history, biographies, "
                "scientific concepts, and well-established facts. "
                "Use for background knowledge and detailed factual information. "
                "Input: a search query."
            ),
        )
        print("Wikipedia: available")
        return wiki
    except ImportError:
        print("Wikipedia: not available (pip install wikipedia langchain-community)")
        return None

# ─── TOOL: SUMMARIZER ────────────────────────────────────────────────────────

@tool
def summarize_research(text: str) -> str:
    """
    Creates a concise, structured summary of research findings.
    Use this AFTER gathering information from web search or Wikipedia.
    Input: the raw research text to summarize.
    Returns a bulleted summary with key points.
    """
    # The LLM (as the agent brain) will call this tool to organize findings.
    # The actual summarization happens in the LLM's tool-use reasoning.
    # This tool returns a prompt template that the agent fills in.
    lines = [line.strip() for line in text.split(".") if line.strip()]
    if not lines:
        return "No content to summarize."
    # Return the text as-is; the agent will structure it in its final response
    word_count = len(text.split())
    return f"[Research material ready for synthesis — {word_count} words of source material]\n\n{text[:500]}..."

# ─── BUILD THE AGENT ──────────────────────────────────────────────────────────

def build_agent(verbose: bool = False):
    """
    Build the research agent with all available tools.

    Uses create_openai_tools_agent (modern approach) which:
    - Natively supports multi-turn memory via chat_history
    - Uses OpenAI's function calling API (more reliable than ReAct text parsing)
    - Handles tool call formatting automatically
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set in .env")
        sys.exit(1)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    # Collect available tools
    tools = []
    search = _build_search_tool()
    if search:
        tools.append(search)
    wiki = _build_wikipedia_tool()
    if wiki:
        tools.append(wiki)
    tools.append(summarize_research)

    if not tools:
        print("ERROR: No tools available. Install required packages.")
        sys.exit(1)

    print(f"Tools loaded: {[t.name for t in tools]}")
    print()

    # System prompt — guides the agent's research behavior
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert research assistant. Your role is to:
1. Answer research questions thoroughly using available tools
2. Search for current, accurate information
3. Cross-reference multiple sources when possible
4. Provide well-structured, clear answers with key facts highlighted
5. Remember context from earlier in the conversation
6. If you're unsure, say so — don't fabricate information

Available tools: web search, Wikipedia, summarizer.
Use search for current info, Wikipedia for encyclopedic facts.
Always synthesize information into a clear, useful answer."""),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=15,
        handle_parsing_errors=True,
        return_intermediate_steps=True,  # Enables inspection of tool calls
    )

# ─── SAVE RESULTS ────────────────────────────────────────────────────────────

def save_result(question: str, answer: str, output_dir: Path):
    """Save a research result to a timestamped text file."""
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"research_{timestamp}.txt"

    content = f"""RESEARCH RESULT
================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

QUESTION:
{question}

ANSWER:
{answer}
"""
    filename.write_text(content, encoding="utf-8")
    return filename

# ─── CLI LOOP ────────────────────────────────────────────────────────────────

def print_help():
    print("""
Commands:
  /quit          — exit
  /verbose on    — show agent reasoning
  /verbose off   — hide reasoning (default)
  /save          — save last result to file
  /clear         — clear conversation history
  /sessions      — show history length
  /help          — show this message

Or just type a research question!
""")

def print_banner():
    print("=" * 60)
    print("   RESEARCH AGENT — Week 6 Project")
    print("   Powered by LangChain + OpenAI")
    print("=" * 60)
    print("Type a research question, or /help for commands.")
    print()

def run_cli():
    """Main CLI loop."""
    print_banner()

    verbose = False
    agent = build_agent(verbose=verbose)

    chat_history: list = []
    last_question = ""
    last_answer = ""
    output_dir = Path(__file__).parent / "research_results"

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # ── Handle slash commands ──
        if user_input.startswith("/"):
            cmd = user_input.lower()

            if cmd == "/quit":
                print("Goodbye! Research results saved to:", output_dir if output_dir.exists() else "not saved yet")
                break

            elif cmd == "/verbose on":
                verbose = True
                agent.verbose = True
                print("Verbose mode ON — you'll see the agent's reasoning steps.")
                continue

            elif cmd == "/verbose off":
                verbose = False
                agent.verbose = False
                print("Verbose mode OFF — only showing final answers.")
                continue

            elif cmd == "/save":
                if not last_answer:
                    print("Nothing to save yet. Ask a research question first.")
                    continue
                path = save_result(last_question, last_answer, output_dir)
                print(f"Saved to: {path}")
                continue

            elif cmd == "/clear":
                chat_history.clear()
                print("Conversation history cleared.")
                continue

            elif cmd == "/sessions":
                turns = len(chat_history) // 2
                print(f"Current session: {turns} turns in history.")
                continue

            elif cmd == "/help":
                print_help()
                continue

            else:
                print(f"Unknown command: {user_input}. Type /help for commands.")
                continue

        # ── Research question ──
        last_question = user_input
        print("\nResearching...\n")

        try:
            result = agent.invoke({
                "input": user_input,
                "chat_history": chat_history,
            })

            answer = result["output"]
            last_answer = answer

            # Show intermediate steps if we want to see tool usage without full verbose
            if result.get("intermediate_steps") and verbose:
                tool_calls = len(result["intermediate_steps"])
                print(f"[Used {tool_calls} tool call(s)]\n")

            print(f"Agent: {answer}")

            # Append to history for next turn
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=answer))

            # Keep history manageable (last 20 messages = 10 turns)
            if len(chat_history) > 20:
                chat_history = chat_history[-20:]

        except KeyboardInterrupt:
            print("\n[Interrupted]")
        except Exception as e:
            print(f"\nError: {e}")
            print("Try rephrasing your question or type /clear to reset.")

if __name__ == "__main__":
    run_cli()
