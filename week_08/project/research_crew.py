"""
Week 8 Project: Research Crew CLI
===================================
A complete 3-agent CrewAI research crew that:
  1. Researcher: gathers information on a given topic (mock or real search)
  2. Writer:     writes a structured article based on the research
  3. Editor:     reviews and improves the article for clarity and quality

Sequential process: Researcher → Writer → Editor
Output saved to: week_08/project/output/report.md

Usage:
  python3 week_08/project/research_crew.py
  python3 week_08/project/research_crew.py --topic "quantum computing basics"
  python3 week_08/project/research_crew.py --demo  (uses mock LLM, no API needed)

Requirements:
  pip install crewai crewai-tools python-dotenv
  OPENAI_API_KEY in .env (or set as environment variable)

Python 3.10+ required.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from crewai import Agent, Task, Crew, Process

# ─── OUTPUT DIRECTORY ─────────────────────────────────────────────────────────

# Resolve output dir relative to this file's location
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = str(OUTPUT_DIR / "report.md")

# ─── OPTIONAL TOOLS ──────────────────────────────────────────────────────────

def get_search_tool():
    """
    Try to get a real search tool. Fall back gracefully if not available.
    Priority: DuckDuckGo (free, no key) → mock tool
    """
    # Try DuckDuckGo first (no API key needed)
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        tool = DuckDuckGoSearchRun()
        print("[Setup] Using DuckDuckGoSearchRun for web search.")
        return tool
    except ImportError:
        pass

    # Try crewai-tools SerperDev (needs SERPER_API_KEY)
    try:
        from crewai_tools import SerperDevTool
        if os.getenv("SERPER_API_KEY"):
            tool = SerperDevTool()
            print("[Setup] Using SerperDevTool for web search.")
            return tool
    except ImportError:
        pass

    # Fallback: mock search tool
    print("[Setup] No real search tool available — using mock search tool.")
    return None

# ─── MOCK SEARCH TOOL (fallback) ─────────────────────────────────────────────

from langchain.tools import tool

@tool
def mock_web_search(query: str) -> str:
    """
    Search the web for information on a given topic.
    Use this to find facts, explanations, and current developments
    about the research topic. Input should be a specific search query.
    """
    # Mock response that simulates realistic search results
    return (
        f"Mock search results for: '{query}'\n\n"
        f"Source 1 (wikipedia.org): {query} is a significant field with "
        f"widespread applications in modern technology. Key developments have "
        f"occurred in the past decade, with major contributions from academic "
        f"institutions and technology companies.\n\n"
        f"Source 2 (arxiv.org): Recent research on {query} shows promising "
        f"results in practical applications. Studies indicate a 40% improvement "
        f"in efficiency compared to traditional approaches.\n\n"
        f"Source 3 (techcrunch.com): Industry adoption of {query} has accelerated "
        f"significantly. Leading companies are investing heavily in this space, "
        f"with several high-profile implementations announced in 2024.\n\n"
        f"Source 4 (docs.python.org): Python has excellent library support for "
        f"{query} with packages like numpy, scikit-learn, and specialized frameworks "
        f"available via pip.\n\n"
        f"Key facts: (1) Active open-source community, (2) Production-ready tools "
        f"available, (3) Growing job market demand, (4) Multiple learning resources."
    )

# ─── AGENTS ───────────────────────────────────────────────────────────────────

def build_researcher(search_tool=None) -> Agent:
    """Build the Researcher agent with appropriate search tool."""
    tools = [search_tool if search_tool is not None else mock_web_search]

    return Agent(
        role="Senior Research Analyst",
        goal=(
            "Conduct thorough research on the given topic and produce comprehensive, "
            "accurate findings that cover key concepts, current developments, and "
            "practical applications"
        ),
        backstory=(
            "You are a Senior Research Analyst with 8 years of experience in "
            "technology research. You have a talent for finding reliable sources, "
            "identifying the most important aspects of any topic, and presenting "
            "findings in a structured, objective manner. You always verify claims "
            "from multiple angles and highlight both strengths and limitations. "
            "You use search tools to gather current information and supplement "
            "it with your own expertise."
        ),
        tools=tools,
        verbose=True,
        allow_delegation=False,
        max_iter=8,
    )


def build_writer() -> Agent:
    """Build the Writer agent."""
    return Agent(
        role="Technical Content Writer",
        goal=(
            "Transform research findings into a clear, well-structured article "
            "that is informative, engaging, and accessible to a technical audience"
        ),
        backstory=(
            "You are a Technical Content Writer who spent 4 years as a software "
            "engineer before moving to technical writing. You excel at taking "
            "complex research and turning it into articles that developers actually "
            "want to read. Your writing style is direct and uses concrete examples. "
            "You structure content with clear headings, bullet points where appropriate, "
            "and always include a practical takeaway section."
        ),
        tools=[],   # writer synthesizes — no external tools needed
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )


def build_editor() -> Agent:
    """Build the Editor agent."""
    return Agent(
        role="Senior Content Editor",
        goal=(
            "Review and improve the article for accuracy, clarity, flow, and "
            "overall quality — ensuring it meets publication standards"
        ),
        backstory=(
            "You are a Senior Content Editor with 12 years of experience at "
            "technology publications. You have an eye for structural issues, "
            "unclear explanations, and missing context. You improve articles "
            "without changing their core message. You check that all claims are "
            "supported, that the article flows logically, and that it ends with "
            "a clear, actionable conclusion. You return the full improved article, "
            "not just notes."
        ),
        tools=[],   # editor works with text only
        verbose=True,
        allow_delegation=False,
        max_iter=8,
    )

# ─── TASKS ────────────────────────────────────────────────────────────────────

def build_tasks(topic: str, researcher: Agent, writer: Agent, editor: Agent):
    """Build all three tasks for the research crew."""

    research_task = Task(
        description=(
            f"Research the topic: '{topic}'\n\n"
            f"Your research must cover:\n"
            f"1. Core concepts and definitions — what is it and why does it matter?\n"
            f"2. Key components or sub-topics — what are the main areas within this field?\n"
            f"3. Current state and recent developments — what's happening now?\n"
            f"4. Practical applications — where is it used in the real world?\n"
            f"5. Challenges and limitations — what are the open problems?\n"
            f"6. Resources for deeper learning — where should someone go next?\n\n"
            f"Use your search tool to gather current, factual information."
        ),
        expected_output=(
            "A structured research report with 6 labeled sections matching the "
            "outline above. Each section should contain 2-4 concrete, factual "
            "points. Total length: 400-600 words. No fluff — only verified information."
        ),
        agent=researcher,
    )

    writing_task = Task(
        description=(
            f"Using the research provided, write a complete article about: '{topic}'\n\n"
            f"Article requirements:\n"
            f"- Title: clear and informative (not clickbait)\n"
            f"- Introduction: 1 paragraph that explains why this topic matters\n"
            f"- Body: 3-4 sections with H2 headers, covering the key aspects\n"
            f"- Code/example section: at least one practical example or illustration\n"
            f"- Conclusion: key takeaways and what the reader should do next\n\n"
            f"Tone: professional but accessible. Audience: intermediate developers.\n"
            f"Format: Markdown."
        ),
        expected_output=(
            "A complete Markdown article with: title (# heading), introduction, "
            "3-4 body sections with ## headers, at least one code block or "
            "practical example, and a conclusion with clear takeaways. "
            "Length: 600-900 words."
        ),
        agent=writer,
        context=[research_task],  # writer receives researcher's output
    )

    editing_task = Task(
        description=(
            f"Review and improve the article about '{topic}'.\n\n"
            f"Review checklist:\n"
            f"1. Accuracy: Are all claims correct and supported by the research?\n"
            f"2. Clarity: Are explanations easy to follow? Flag any jargon.\n"
            f"3. Structure: Does the article flow logically? Fix any structural issues.\n"
            f"4. Completeness: Are there gaps? Add brief additions where needed.\n"
            f"5. Conclusion: Does it end with clear, actionable advice?\n\n"
            f"Return the COMPLETE improved article in Markdown format.\n"
            f"Do not just return comments — return the full revised article."
        ),
        expected_output=(
            "The complete, improved article in Markdown format. Same structure "
            "as the input but with all issues fixed. The article should be "
            "polished and ready to publish. Include a one-line editor's note "
            "at the bottom summarizing the main changes made."
        ),
        agent=editor,
        context=[research_task, writing_task],  # editor sees both
        output_file=REPORT_PATH,  # save the final edited article
    )

    return research_task, writing_task, editing_task

# ─── CREW BUILDER ─────────────────────────────────────────────────────────────

def build_crew(topic: str):
    """Build and return the complete research crew."""
    print("\n[Setup] Building research crew...")

    # Get the best available search tool
    search_tool = get_search_tool()

    # Build agents
    researcher = build_researcher(search_tool)
    writer = build_writer()
    editor = build_editor()

    print("[Setup] Agents created: Researcher, Writer, Editor")

    # Build tasks
    research_task, writing_task, editing_task = build_tasks(
        topic, researcher, writer, editor
    )

    print("[Setup] Tasks created: research, writing, editing")

    # Assemble the crew
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, writing_task, editing_task],
        process=Process.sequential,
        verbose=True,
    )

    print("[Setup] Crew assembled. Process: sequential (Researcher → Writer → Editor)")
    return crew

# ─── DEMO MODE (no API key needed) ────────────────────────────────────────────

def run_demo(topic: str):
    """
    Demo mode: show the crew structure without calling the LLM.
    Useful when you don't have an API key yet.
    """
    print("\n" + "=" * 60)
    print("DEMO MODE — Crew structure (no API calls)")
    print("=" * 60)

    crew = build_crew(topic)

    print(f"\nTopic: '{topic}'")
    print(f"\nCrew configuration:")
    print(f"  Process: Sequential")
    print(f"  Agents:  {len(crew.agents)}")
    for i, agent in enumerate(crew.agents, 1):
        tool_names = [t.name if hasattr(t, 'name') else str(t) for t in agent.tools]
        tools_str = ", ".join(tool_names) if tool_names else "none"
        print(f"    {i}. {agent.role}")
        print(f"       Goal: {agent.goal[:60]}...")
        print(f"       Tools: [{tools_str}]")

    print(f"\n  Tasks:   {len(crew.tasks)}")
    for i, task in enumerate(crew.tasks, 1):
        agent_role = task.agent.role if task.agent else "manager"
        print(f"    {i}. {agent_role}")
        print(f"       Description: {task.description[:60]}...")

    print(f"\nOutput file: {REPORT_PATH}")
    print("\nTo run for real:")
    print("  1. Add OPENAI_API_KEY to your .env file")
    print("  2. Run: python3 week_08/project/research_crew.py")

# ─── MAIN EXECUTION ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Research Crew — AI-powered research, writing, and editing"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Research topic (e.g., 'quantum computing basics')",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (shows crew structure, no API calls)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  Research Crew — Week 8 Project")
    print("  CrewAI: Researcher → Writer → Editor")
    print("=" * 60)

    # Get topic
    if args.topic:
        topic = args.topic.strip()
    else:
        try:
            topic = input("\nEnter research topic: ").strip()
        except (EOFError, KeyboardInterrupt):
            topic = "Python type hints and type checking with mypy"
            print(f"\nUsing default topic: '{topic}'")

    if not topic:
        topic = "Python type hints and type checking with mypy"
        print(f"Using default topic: '{topic}'")

    print(f"\nTopic: '{topic}'")

    # Demo mode
    if args.demo:
        run_demo(topic)
        return

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n[Warning] OPENAI_API_KEY not found in environment.")
        print("  Running in demo mode instead.")
        print("  To run for real: add OPENAI_API_KEY to your .env file")
        run_demo(topic)
        return

    # Build and run the crew
    print("\n[Starting] Building crew and beginning research...")
    crew = build_crew(topic)

    try:
        print("\n[Running] crew.kickoff() — this may take 1-3 minutes...")
        print("  Watch the agent reasoning below:")
        print("-" * 60)

        result = crew.kickoff()

        print("\n" + "=" * 60)
        print("CREW COMPLETE")
        print("=" * 60)
        print(f"\nReport saved to: {REPORT_PATH}")
        print("\nFinal output preview:")
        print("-" * 60)
        output_str = str(result)
        print(output_str[:1000] + ("..." if len(output_str) > 1000 else ""))

        # Also print full result to console
        print("\n" + "=" * 60)
        print("FULL REPORT:")
        print("=" * 60)
        print(output_str)

    except Exception as e:
        print(f"\n[Error] Crew execution failed: {e}")
        print("\nCommon causes:")
        print("  - Invalid or rate-limited OPENAI_API_KEY")
        print("  - Network connectivity issue")
        print("  - Python version < 3.10 (CrewAI requires 3.10+)")
        print("\nRun with --demo flag to test without API calls.")
        sys.exit(1)


if __name__ == "__main__":
    main()
