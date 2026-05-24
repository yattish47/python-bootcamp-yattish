# Lesson 8.1 — CrewAI Introduction: Agent, Task, Crew
# CONCEPT: CrewAI organizes AI work around three core classes.
#           Agent = a specialized AI worker with a role, goal, and backstory.
#           Task  = a unit of work with a description, expected output, and assigned agent.
#           Crew  = the team orchestrator that runs tasks in order.
#
# KOTLIN EQUIVALENT: Like defining microservices. Each Agent is a service with
#                    a clearly defined responsibility (role/goal). Tasks are
#                    like API endpoints on that service. Crew is the service
#                    mesh or orchestration layer.
#
# PHP EQUIVALENT: Like defining specialized classes in a Laravel application.
#                 Agent = a Service class with a specific domain.
#                 Task  = a method call specification (what to do + expected return).
#                 Crew  = a workflow that chains those service calls together.

# ─── IMPORTANT SETUP NOTE ────────────────────────────────────────────────────
#
# CrewAI makes REAL LLM API calls. These examples are structured to run
# correctly but will fail without a valid OPENAI_API_KEY in your .env file.
# The code is complete and correct — just add your key to use it.
#
# To test without an API key: read through the code and study the structure.
# The key learning here is HOW to define Agents, Tasks, and Crews.

# ─── IMPORTS ─────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv

load_dotenv()  # loads OPENAI_API_KEY from .env

# CrewAI core imports
from crewai import Agent, Task, Crew, Process

# ─── THE THREE CORE CLASSES ──────────────────────────────────────────────────

# ┌─────────────────────────────────────────────────────────────────────────┐
# │  AGENT                                                                  │
# │  An Agent is an AI worker with a persona. The role, goal, and          │
# │  backstory are injected into the system prompt — they shape HOW the    │
# │  LLM responds. Think of it as giving the LLM a job title, KPIs,       │
# │  and a performance review history.                                      │
# └─────────────────────────────────────────────────────────────────────────┘

# ┌─────────────────────────────────────────────────────────────────────────┐
# │  TASK                                                                   │
# │  A Task defines WHAT needs to be done. It specifies:                   │
# │  - description:     The detailed instructions (like a Jira ticket)     │
# │  - expected_output: What a successful result looks like                │
# │  - agent:           Which agent is responsible for this task           │
# └─────────────────────────────────────────────────────────────────────────┘

# ┌─────────────────────────────────────────────────────────────────────────┐
# │  CREW                                                                   │
# │  A Crew ties agents and tasks together. It manages:                    │
# │  - Which agents are on the team                                        │
# │  - Which tasks need to be completed                                    │
# │  - The process type (sequential: A → B → C, or hierarchical)          │
# └─────────────────────────────────────────────────────────────────────────┘

# ─── CREATING AGENTS ─────────────────────────────────────────────────────────

# Agent 1: Researcher
# Role defines the persona. Goal defines the objective. Backstory gives context.

researcher = Agent(
    role="Technology Researcher",
    goal="Find accurate, comprehensive information about a given technology topic",
    backstory=(
        "You are a meticulous technology researcher with 8 years of experience "
        "analyzing software trends, frameworks, and tools. You always verify facts "
        "from multiple angles and present balanced, objective findings. You focus "
        "on practical implications rather than hype."
    ),
    verbose=True,        # show agent's step-by-step reasoning
    allow_delegation=False,  # this agent won't delegate to others
)

# Agent 2: Technical Writer
# A different persona, different strengths, different goal.

writer = Agent(
    role="Technical Content Writer",
    goal="Transform technical research into clear, engaging content for developers",
    backstory=(
        "You are a senior technical writer who spent 5 years as a software developer "
        "before moving to content creation. You bridge the gap between complex "
        "technical details and practical developer needs. Your writing is precise, "
        "uses concrete examples, and avoids unnecessary jargon."
    ),
    verbose=True,
    allow_delegation=False,
)

# ─── CREATING TASKS ──────────────────────────────────────────────────────────

# Task 1: Assigned to the researcher
# 'description' is the detailed prompt for what to do.
# 'expected_output' tells the LLM what a complete result looks like.

research_task = Task(
    description=(
        "Research the key differences between LangGraph and LangChain's AgentExecutor. "
        "Cover: (1) when to use each, (2) how they handle state, (3) their strengths "
        "and limitations, (4) a real-world use case for each. Be specific and factual."
    ),
    expected_output=(
        "A structured research report with 4 sections: Use Cases, State Management, "
        "Strengths/Limitations, and Real-World Examples. Each section should be "
        "2-3 paragraphs with concrete, actionable information."
    ),
    agent=researcher,   # this task is assigned to the researcher agent
)

# Task 2: Assigned to the writer
# This task consumes the output of research_task (handled automatically in sequential mode)

write_task = Task(
    description=(
        "Using the research provided, write a developer-focused comparison guide for "
        "LangGraph vs AgentExecutor. The guide should help a Python developer who is "
        "familiar with web frameworks (like Django or FastAPI) decide which to use. "
        "Include code snippet placeholders (e.g., '# Example: define a StateGraph') "
        "to illustrate concepts."
    ),
    expected_output=(
        "A 400-600 word developer guide with: a clear recommendation section, "
        "a comparison table, and 2-3 code examples (can be pseudocode/comments). "
        "Tone: friendly technical blog post."
    ),
    agent=writer,       # this task is assigned to the writer agent
)

# ─── CREATING THE CREW ───────────────────────────────────────────────────────

# The Crew orchestrates execution.
# Process.sequential = tasks run in the ORDER they appear in the tasks list.
# The output of each task is available to subsequent tasks automatically.

crew = Crew(
    agents=[researcher, writer],   # all agents on this team
    tasks=[research_task, write_task],  # tasks in execution order
    process=Process.sequential,    # researcher goes first, then writer
    verbose=True,                  # show crew-level activity
)

# ─── RUNNING THE CREW ────────────────────────────────────────────────────────

print("=" * 60)
print("CrewAI Lesson 8.1 — Minimal 2-Agent Crew")
print("=" * 60)
print("Agents: Technology Researcher + Technical Content Writer")
print("Topic:  LangGraph vs AgentExecutor comparison")
print()
print("NOTE: This requires a valid OPENAI_API_KEY to actually run.")
print("      Study the code structure — that's the main learning goal.")
print("=" * 60)

# Uncomment to actually run (requires API key):
# result = crew.kickoff()
# print("\n" + "=" * 60)
# print("CREW OUTPUT:")
# print("=" * 60)
# print(result)

# ─── WHAT CREWAI DOES BEHIND THE SCENES ──────────────────────────────────────

print("\nWhat happens when crew.kickoff() runs:")
print()
steps = [
    "1. Task 1 starts: researcher agent receives 'Research LangGraph vs AgentExecutor'",
    "2. Researcher uses its role/goal/backstory as system prompt context",
    "3. Researcher may use tools (if any are attached) to gather information",
    "4. Researcher produces output matching 'expected_output' specification",
    "5. Task 2 starts: writer agent receives the research output + its own task",
    "6. Writer uses research output as context to write the developer guide",
    "7. Writer produces final output",
    "8. crew.kickoff() returns the final task's output",
]
for step in steps:
    print(f"  {step}")

# ─── KOTLIN BRIDGE ───────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Kotlin/Spring Mental Model:")
print("=" * 60)
mapping = [
    ("Agent",           "A Spring @Service with a focused domain responsibility"),
    ("Task",            "A method contract: what to call + what it must return"),
    ("Crew",            "A Spring Batch Job or workflow orchestrator"),
    ("Process.sequential", "A simple pipeline: step A must complete before step B"),
    ("crew.kickoff()", "jobLauncher.run(job, params) — start the workflow"),
    ("verbose=True",   "Enabling TRACE logging on a specific service"),
]
for concept, equivalent in mapping:
    print(f"  {concept:<25} ≈ {equivalent}")

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 (Design a Crew):
#   You're building a customer support system. Design a 3-agent crew:
#   - Agent 1 should classify the ticket type (billing, technical, general)
#   - Agent 2 should draft a response based on the classification
#   - Agent 3 should QA the response for tone and accuracy
#   For each agent, write out the role, goal, and backstory strings.
#   For each task, write description and expected_output.

# Exercise 2 (Design a Crew):
#   You're building a market research tool.
#   Design a 2-agent crew where:
#   - Agent 1 gathers raw data about a competitor product
#   - Agent 2 performs SWOT analysis on that data
#   What should each task's expected_output look like in detail?

# Exercise 3 (Code modification):
#   Add a third agent to the code above: an "Editor" who proofreads the
#   writer's output for grammar and clarity.
#   Add a third task assigned to the editor.
#   Update the crew's agents list and tasks list to include the editor.
#   What changes in the Crew constructor? What stays the same?
