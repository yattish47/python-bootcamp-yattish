# Lesson 8.4 — Tools in CrewAI
# CONCEPT: Tools extend what agents can DO beyond just generating text.
#           Agents with tools can search the web, read files, write files,
#           run code, query databases, and call APIs.
#           Assign tools to agents using the 'tools' parameter — only
#           give each agent the tools it actually needs (least privilege).
#
# KOTLIN EQUIVALENT: Like injecting specific @Repository or @RestTemplate
#                    beans into each @Service. A "SearchService" gets a
#                    SearchClient, not a FileWriter. Dependency injection
#                    scoped to actual needs.
#
# PHP EQUIVALENT: Like injecting specific services into each controller.
#                 A ResearchController gets SearchService + HttpClient.
#                 A ReportController gets FileSystem + PdfGenerator.
#                 You don't inject everything into everything.

# ─── IMPORTS ─────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

load_dotenv()

# ─── TOOLS OVERVIEW ──────────────────────────────────────────────────────────

print("=" * 60)
print("Tool categories in CrewAI:")
print("=" * 60)

tool_categories = [
    ("Built-in crewai-tools", [
        "SerperDevTool    — Google search via Serper API (needs SERPER_API_KEY)",
        "ScrapeWebsiteTool — Scrape content from a URL",
        "FileReadTool     — Read files from disk",
        "FileWriterTool   — Write files to disk",
        "DirectoryReadTool— List files in a directory",
        "YoutubeVideoSearchTool — Search YouTube",
    ]),
    ("LangChain tools (compatible)", [
        "Any @tool decorated function from LangChain",
        "DuckDuckGoSearchRun — web search (no API key needed)",
        "Wikipedia tool",
        "Custom tools you've already built in LangChain",
    ]),
    ("Custom tools", [
        "Any class inheriting from crewai.tools.BaseTool",
        "Any function decorated with @tool from langchain",
    ]),
]

for category, tools_list in tool_categories:
    print(f"\n  {category}:")
    for tool in tools_list:
        print(f"    - {tool}")

# ─── USING BUILT-IN CREWAI-TOOLS ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("Pattern 1: Built-in crewai-tools")
print("=" * 60)

# Attempt to import crewai-tools; show fallback message if not installed
try:
    from crewai_tools import FileReadTool, FileWriterTool

    file_reader = FileReadTool()
    file_writer = FileWriterTool()

    print("  crewai-tools imported successfully.")
    print("  Available: FileReadTool, FileWriterTool")

    # Assign to agents that need them
    editor_agent_with_tools = Agent(
        role="Document Editor",
        goal="Review and improve written documents for clarity and accuracy",
        backstory=(
            "You are a meticulous editor with 10 years of experience in technical "
            "publishing. You focus on clarity, consistency, and factual accuracy."
        ),
        tools=[file_reader, file_writer],  # can READ existing docs and WRITE edits
        verbose=False,
        allow_delegation=False,
    )

    print(f"\n  Editor agent has {len(editor_agent_with_tools.tools)} tool(s): FileReadTool, FileWriterTool")

except ImportError:
    print("  crewai-tools not installed. Run: pip install crewai-tools")
    print("  Continuing with custom tools demonstration...")

# ─── CUSTOM TOOL WITH LANGCHAIN @tool DECORATOR ──────────────────────────────

print("\n" + "=" * 60)
print("Pattern 2: Custom tool using @tool decorator (LangChain-compatible)")
print("=" * 60)

# LangChain's @tool decorator creates a tool that CrewAI agents can use.
# The docstring becomes the tool's description — the LLM reads it to decide
# when to use the tool.

from langchain.tools import tool

@tool("DuckDuckGoSearch")
def mock_search_tool(query: str) -> str:
    """
    Search the web for information about a given query.
    Use this to find current information, facts, news, or data
    that you don't already know. Input should be a specific search query string.
    """
    # In production, use DuckDuckGoSearchRun or SerperDevTool
    # This mock returns structured fake results for demo purposes
    return (
        f"Search results for '{query}':\n"
        f"  1. [example.com] Overview article covering key aspects of {query}\n"
        f"  2. [docs.python.org] Official documentation related to {query}\n"
        f"  3. [github.com] Open source projects implementing {query}\n"
        f"  Summary: {query} is a significant topic with active development "
        f"and multiple practical use cases in modern software engineering."
    )

@tool("DatabaseQuery")
def mock_database_tool(query: str) -> str:
    """
    Query the internal product database for statistics and metrics.
    Use this to get user counts, revenue figures, or product performance data.
    Input should be a natural language description of what metric you need.
    """
    return (
        f"Database query for '{query}':\n"
        f"  total_records: 15_420\n"
        f"  last_updated: 2024-01-15\n"
        f"  relevant_metric: 42.7% improvement over previous period\n"
        f"  confidence: high"
    )

print(f"  Created custom tools: {mock_search_tool.name}, {mock_database_tool.name}")
print(f"  Tool descriptions (used by LLM to decide when to call them):")
print(f"    mock_search_tool: '{mock_search_tool.description[:60]}...'")

# ─── PRINCIPLE OF LEAST PRIVILEGE ────────────────────────────────────────────

print("\n" + "=" * 60)
print("Principle of Least Privilege — Give each agent ONLY what it needs")
print("=" * 60)

# Wrong approach: give every agent every tool
# → agents get confused about when to use which tool
# → unexpected behavior when an agent uses the wrong tool
# → harder to debug
# → more expensive (each tool call costs tokens)

# Correct approach: scope tools tightly to each agent's role

researcher_agent = Agent(
    role="Research Specialist",
    goal="Find comprehensive, accurate information on technical topics",
    backstory=(
        "You are a technical researcher with expertise in finding and "
        "synthesizing information from diverse sources. You use search tools "
        "to verify facts and gather current data."
    ),
    tools=[mock_search_tool],   # ONLY search — no file access needed
    verbose=False,
    allow_delegation=False,
)

data_analyst_agent = Agent(
    role="Data Analyst",
    goal="Extract and interpret business metrics from internal data sources",
    backstory=(
        "You are a data analyst specializing in product analytics. You query "
        "internal databases to extract meaningful metrics and trends."
    ),
    tools=[mock_database_tool],  # ONLY database — no web search needed
    verbose=False,
    allow_delegation=False,
)

writer_agent = Agent(
    role="Technical Writer",
    goal="Synthesize research into clear, well-structured documents",
    backstory=(
        "You are a technical writer who synthesizes complex information into "
        "clear documentation. You focus on structure and clarity."
    ),
    tools=[],  # NO tools — writers synthesize, they don't search or query
    verbose=False,
    allow_delegation=False,
)

print("\n  Agent → Tools mapping:")
print(f"    researcher_agent  → [{mock_search_tool.name}]       (search only)")
print(f"    data_analyst_agent→ [{mock_database_tool.name}]  (DB only)")
print(f"    writer_agent      → [] (no tools needed for writing)")

print("\n  Why this matters:")
reasons = [
    "Agents with fewer tools make better decisions about when to use them",
    "Easier to debug — you know exactly which tools each agent can invoke",
    "Cheaper — fewer tool call attempts = fewer LLM tokens consumed",
    "More secure — a writer agent can't accidentally write to the database",
    "Clearer separation of concerns — mirrors good software architecture",
]
for reason in reasons:
    print(f"    - {reason}")

# ─── FULL CREW WITH TOOLS ─────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Full crew: Researcher (search) → Data Analyst (DB) → Writer (no tools)")
print("=" * 60)

research_with_tools_task = Task(
    description=(
        "Research the current state of Python AI frameworks (LangChain, LangGraph, "
        "CrewAI, AutoGen). Use your search tool to find current adoption data, "
        "key features, and community sentiment."
    ),
    expected_output=(
        "A research summary with: adoption metrics for each framework, "
        "key strengths, weaknesses, and notable recent developments."
    ),
    agent=researcher_agent,
)

data_analysis_task = Task(
    description=(
        "Query the database for our internal usage statistics of AI frameworks "
        "in our product. How many users, what growth trend?"
    ),
    expected_output=(
        "Internal metrics: user count by framework, growth rate, "
        "and top user segments."
    ),
    agent=data_analyst_agent,
)

synthesis_task = Task(
    description=(
        "Combine the external research and internal metrics into a concise "
        "strategic brief recommending which AI framework our engineering team "
        "should standardize on."
    ),
    expected_output=(
        "A 300-word strategic brief with: recommendation, supporting rationale "
        "from both external research and internal data, and 3 next steps."
    ),
    agent=writer_agent,
    context=[research_with_tools_task, data_analysis_task],  # needs both inputs
)

full_crew = Crew(
    agents=[researcher_agent, data_analyst_agent, writer_agent],
    tasks=[research_with_tools_task, data_analysis_task, synthesis_task],
    process=Process.sequential,
    verbose=False,
)

print("\nCrew structure:")
print("  researcher_agent  → research_with_tools_task  (uses mock_search_tool)")
print("  data_analyst_agent → data_analysis_task      (uses mock_database_tool)")
print("  writer_agent      → synthesis_task            (no tools, uses context)")
print()
print("To run (requires OPENAI_API_KEY):")
print("  result = full_crew.kickoff()")
print("  print(result)")

# ─── REAL TOOLS QUICK REFERENCE ──────────────────────────────────────────────

print("\n" + "=" * 60)
print("Real tools you'll use in production:")
print("=" * 60)

real_tools = [
    ("SerperDevTool()",
     "from crewai_tools import SerperDevTool",
     "Google search. Needs SERPER_API_KEY env var."),

    ("DuckDuckGoSearchRun()",
     "from langchain_community.tools import DuckDuckGoSearchRun",
     "Web search, no API key needed. Slower but free."),

    ("FileReadTool()",
     "from crewai_tools import FileReadTool",
     "Read files from disk. Good for loading context docs."),

    ("FileWriterTool()",
     "from crewai_tools import FileWriterTool",
     "Write files to disk. Good for saving agent outputs."),

    ("ScrapeWebsiteTool()",
     "from crewai_tools import ScrapeWebsiteTool",
     "Scrape full page content from a URL."),
]

for tool_init, import_line, description in real_tools:
    print(f"\n  {tool_init}")
    print(f"    Import: {import_line}")
    print(f"    Use:    {description}")

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Write a custom @tool called "WeatherLookup" that:
#   - Takes a city name as input
#   - Returns a mock weather report dict as a formatted string
#   - Has a clear docstring explaining when to use it
#   Then create a "Travel Planner" agent with ONLY this tool.
#   Write the task that would use this agent.

# Exercise 2 (Least privilege):
#   You have 4 agents: researcher, code_generator, code_reviewer, deployer.
#   You have 5 tools: web_search, github_read, github_write, test_runner, deploy_api.
#   Apply the principle of least privilege:
#   - Which tools should each agent get?
#   - Which agent should get NO tools?
#   - What's the risk if you give every agent every tool?

# Exercise 3 (Custom tool):
#   Create a custom tool called "SlackNotifier" that:
#   - Accepts a message string and a channel string
#   - Prints the notification to console (mock — don't actually call Slack)
#   - Returns "Notification sent to #{channel}"
#   Attach it to a "Communications Agent" whose job is to notify stakeholders
#   when a research task is complete.
#   Write the full agent and task definitions.
