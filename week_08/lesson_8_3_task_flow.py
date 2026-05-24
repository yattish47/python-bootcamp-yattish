# Lesson 8.3 — Task Flow: Sequential, Hierarchical, and Context
# CONCEPT: Tasks are the unit of work in CrewAI. They can run sequentially
#           (one after another) or hierarchically (a manager delegates).
#           'context' makes one task's output the input of another.
#           'output_file' saves a task's result to disk.
#
# KOTLIN EQUIVALENT: Sequential = Spring Batch steps in a linear job.
#                    Hierarchical = an orchestration service that dynamically
#                    dispatches sub-tasks to worker services based on output.
#                    context=[task_a] = @Autowire the result of step A into step B.
#
# PHP EQUIVALENT: Sequential = a Laravel job chain (Job::withChain([...])).
#                 Hierarchical = a queue worker that dispatches child jobs.
#                 context=[task] = passing the result of one queued job as the
#                 constructor argument of the next.

# ─── IMPORTS ─────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

load_dotenv()

# ─── TASK ATTRIBUTES — COMPLETE REFERENCE ────────────────────────────────────

print("=" * 60)
print("Task attributes reference:")
print("=" * 60)

attributes = [
    ("description",     "REQUIRED. What the agent must do. Be very specific."),
    ("expected_output", "REQUIRED. What a successful completion looks like."),
    ("agent",           "REQUIRED. Which agent is responsible for this task."),
    ("context",         "OPTIONAL. List of tasks whose output feeds this task."),
    ("output_file",     "OPTIONAL. File path to save this task's output."),
    ("async_execution", "OPTIONAL. Run task in parallel with others (bool)."),
    ("human_input",     "OPTIONAL. Pause and ask a human for input (bool)."),
]
for attr, desc in attributes:
    print(f"  {attr:<20} — {desc}")

# ─── DEMO AGENTS ─────────────────────────────────────────────────────────────

market_researcher = Agent(
    role="Market Research Analyst",
    goal="Gather comprehensive market data about technology sectors",
    backstory=(
        "You are a market research analyst with 5 years of experience in the "
        "technology sector. You excel at synthesizing information from multiple "
        "sources into clear, actionable market insights."
    ),
    verbose=False,
    allow_delegation=False,
)

strategy_analyst = Agent(
    role="Business Strategy Analyst",
    goal="Transform market research into actionable business strategies",
    backstory=(
        "You are a business strategist who has advised 20+ tech startups on "
        "go-to-market strategy. You specialize in competitive analysis and "
        "identifying market opportunities from raw research data."
    ),
    verbose=False,
    allow_delegation=False,
)

report_writer = Agent(
    role="Executive Report Writer",
    goal="Write clear executive summaries that enable fast decision-making",
    backstory=(
        "You are a communication specialist who has written hundreds of executive "
        "briefings for C-suite audiences. Your reports are concise, structured, "
        "and always lead with the most important insight."
    ),
    verbose=False,
    allow_delegation=False,
)

# ─── SEQUENTIAL PROCESS ──────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Pattern 1: Sequential Process")
print("  research → strategy → report")
print("=" * 60)

# In sequential mode, tasks run in the ORDER they appear in the tasks list.
# Each task's output is automatically passed to the next task as context.
# You don't need to specify context= for sequential — it's automatic.

research_task = Task(
    description=(
        "Research the current state of the Python AI/ML framework market. "
        "Cover: top 5 frameworks by adoption, their primary use cases, "
        "year-over-year growth trends, and key players behind each framework."
    ),
    expected_output=(
        "A structured research report with: (1) framework adoption rankings, "
        "(2) use case matrix, (3) growth trends with approximate percentages, "
        "(4) key organizations behind each framework."
    ),
    agent=market_researcher,
)

strategy_task = Task(
    description=(
        "Based on the market research, identify the top 3 strategic opportunities "
        "for a startup building AI developer tools. Analyze competitive gaps, "
        "underserved user segments, and positioning options."
    ),
    expected_output=(
        "A strategic analysis with: (1) top 3 opportunities ranked by potential, "
        "(2) competitive gap analysis for each, "
        "(3) recommended positioning for a new entrant."
    ),
    agent=strategy_analyst,
    # In sequential mode, this task automatically receives research_task's output.
    # If you want to be explicit, you can also use: context=[research_task]
)

report_task = Task(
    description=(
        "Write a 1-page executive summary combining the market research and "
        "strategic analysis. Suitable for a 5-minute investor briefing. "
        "Lead with the single most important insight."
    ),
    expected_output=(
        "A 300-word executive summary with: key market insight (1 paragraph), "
        "top opportunity (1 paragraph), recommended action (1 paragraph), "
        "and 3 supporting data points."
    ),
    agent=report_writer,
    output_file="week_08/project/output/market_report.md",  # save output to file
)

sequential_crew = Crew(
    agents=[market_researcher, strategy_analyst, report_writer],
    tasks=[research_task, strategy_task, report_task],
    process=Process.sequential,
    verbose=False,
)

print("\nSequential crew defined:")
print("  Task order: research_task → strategy_task → report_task")
print("  Output saved to: week_08/project/output/market_report.md")
print()
print("  How sequential works:")
print("    1. market_researcher runs research_task")
print("    2. strategy_analyst receives [research output] + strategy_task description")
print("    3. report_writer receives [research + strategy output] + report_task description")
print("    4. crew.kickoff() returns the final task's output")

# ─── EXPLICIT TASK CONTEXT ───────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Pattern 2: Explicit Task Context")
print("  Use context= to cherry-pick which tasks feed a given task")
print("=" * 60)

# Sometimes you want task C to use output of task A but NOT task B.
# Use context=[task_a] to be explicit about dependencies.
# This is more precise than sequential's "pass everything" approach.

data_task = Task(
    description="Gather raw data about Python package download statistics for the past year.",
    expected_output="A table of top 20 packages with monthly download counts.",
    agent=market_researcher,
)

visualization_notes_task = Task(
    description="Suggest visualization types best suited for package download trend data.",
    expected_output="A list of 3-5 chart types with rationale for each.",
    agent=strategy_analyst,
    # This task ONLY gets data_task's output, not other task outputs
    context=[data_task],
)

executive_summary_task = Task(
    description=(
        "Write an executive summary of Python ecosystem health based on the "
        "download statistics research."
    ),
    expected_output="A 200-word executive summary with 3 key takeaways.",
    agent=report_writer,
    # This task gets BOTH data_task AND visualization notes
    context=[data_task, visualization_notes_task],
)

print("\nContext dependencies:")
print(f"  data_task             → no context (independent)")
print(f"  visualization_notes   → context=[data_task]")
print(f"  executive_summary     → context=[data_task, visualization_notes_task]")
print()
print("  Use context= when:")
print("    - You want to skip certain intermediate outputs")
print("    - You're running tasks in parallel (async_execution=True)")
print("    - Your flow is non-linear")

# ─── HIERARCHICAL PROCESS ────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Pattern 3: Hierarchical Process")
print("  A manager agent dynamically delegates to worker agents")
print("=" * 60)

# In hierarchical mode:
# - CrewAI automatically creates a "manager" agent
# - The manager receives all tasks and decides which agent handles each
# - The manager can re-assign if an agent's output isn't good enough
# - You do NOT need to assign agents to tasks in hierarchical mode
#   (the manager does it dynamically)

# Note: hierarchical requires either manager_llm or manager_agent to be set

hierarchical_task_1 = Task(
    description="Research Python web framework performance benchmarks (FastAPI vs Django vs Flask).",
    expected_output="Performance comparison table with requests/second, latency, and memory usage.",
    # No agent= specified — the manager will assign it dynamically
    agent=market_researcher,  # or use manager_agent approach
)

hierarchical_task_2 = Task(
    description="Write a technical comparison blog post based on the benchmark research.",
    expected_output="A 600-word technical blog post with a clear recommendation section.",
    agent=report_writer,
)

# For hierarchical, you would use:
# hierarchical_crew = Crew(
#     agents=[market_researcher, strategy_analyst, report_writer],
#     tasks=[hierarchical_task_1, hierarchical_task_2],
#     process=Process.hierarchical,
#     manager_llm="gpt-4o",  # the model for the manager agent
#     verbose=True,
# )
#
# The manager agent would:
# 1. Read both tasks
# 2. Assign task 1 to market_researcher (most appropriate)
# 3. Review the output
# 4. Assign task 2 to report_writer
# 5. Review final output for quality

print("\nHierarchical crew (code commented out — needs API key):")
print("  Crew(process=Process.hierarchical, manager_llm='gpt-4o')")
print()
print("  When to use hierarchical:")
print("    - Task assignments aren't obvious upfront")
print("    - You need quality review between steps")
print("    - Agents might need to collaborate on a single task")
print()
print("  When to stick with sequential:")
print("    - Task order is clear and fixed")
print("    - Each task clearly maps to one agent")
print("    - You want predictable, auditable execution")

# ─── OUTPUT FILES ────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Saving task output to files:")
print("=" * 60)

print("""
task_with_output = Task(
    description="Write a full market analysis report.",
    expected_output="A 500-word Markdown report with sections.",
    agent=report_writer,
    output_file="reports/market_analysis.md",  # relative to working directory
)

# After crew.kickoff(), the file will be created automatically.
# The file contains exactly what the agent produced for this task.
# Useful for: saving reports, generating code files, creating documents.
""")

# ─── PARSING CREW OUTPUT ─────────────────────────────────────────────────────

print("Accessing crew output:")
print("""
result = crew.kickoff()

# The result object has:
print(result.raw)          # raw string output from the final task
print(result.pydantic)     # structured output if output_pydantic was set on the task
print(result.json_dict)    # dict if output_json was set on the task

# For simple use cases:
print(str(result))         # just print the final output as a string
""")

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Design a 3-task sequential crew for a code review workflow:
#   Task 1: A "Code Analyzer" agent reviews Python code for bugs and style issues
#   Task 2: A "Security Reviewer" agent checks the same code for security vulnerabilities
#   Task 3: A "Tech Lead" agent synthesizes both reviews into a final PR feedback comment
#   Write out each Task definition (description, expected_output, agent, context).
#   Which tasks need context= and which get it automatically?

# Exercise 2:
#   Modify the executive_summary_task to save its output to a file called
#   "week_08/project/output/python_ecosystem_summary.md".
#   What other Task attribute might you want to change so the format
#   is suitable for a Markdown file?

# Exercise 3 (Architecture question):
#   You're building a legal document review system with 4 agents:
#   contract_parser, compliance_checker, risk_assessor, summary_writer.
#   Some tasks must run sequentially (parsing must finish before checking).
#   But compliance_checker and risk_assessor could run in parallel.
#   Sketch out the task flow:
#   - Which tasks use context= and which use sequential ordering?
#   - Which tasks would use async_execution=True?
#   - What goes in expected_output for each?
