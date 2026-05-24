# Lesson 8.2 — Agent Roles: Shaping Agent Behavior
# CONCEPT: The role, goal, and backstory are not just metadata — they are
#           injected directly into the LLM's system prompt. A specific,
#           well-crafted backstory dramatically improves output quality.
#           Other agent parameters (verbose, allow_delegation, llm, max_iter)
#           give you fine-grained control over agent behavior.
#
# KOTLIN EQUIVALENT: Like configuring a Spring Bean with profiles — a vague
#                    @Service("helper") behaves differently than a precisely
#                    scoped @Service("payment-fraud-detector"). The more
#                    specific the configuration, the better the behavior.
#
# PHP EQUIVALENT: Like the difference between a Laravel service class named
#                 ContentHelper vs one named SEOOptimizedBlogPostGenerator.
#                 The specificity of the class definition shapes how developers
#                 (and LLMs) use it.

# ─── IMPORTS ─────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

load_dotenv()

# ─── ROLE, GOAL, BACKSTORY — WHAT THEY DO ────────────────────────────────────

# When CrewAI runs, it constructs a system prompt that includes ALL THREE:
#
#  "You are a [ROLE].
#   Your goal is to [GOAL].
#   Here's your background: [BACKSTORY]
#   Complete the following task: [TASK DESCRIPTION]"
#
# This is why specificity matters so much.
# A vague backstory = a generic, mediocre response.
# A specific backstory = a focused, expert-level response.

# ─── VAGUE VS SPECIFIC — SIDE BY SIDE COMPARISON ─────────────────────────────

print("=" * 60)
print("Comparing: Vague Agent vs Specific Agent")
print("=" * 60)

# ── VAGUE (bad) ──
vague_analyst = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory=(
        "You are a data analyst who works with data. "
        "You have experience with various types of data analysis."
    ),
    verbose=False,
    allow_delegation=False,
)

# ── SPECIFIC (good) ──
specific_analyst = Agent(
    role="Senior E-Commerce Data Analyst",
    goal=(
        "Identify revenue-impacting patterns in e-commerce metrics by correlating "
        "conversion rates, cart abandonment, and customer lifetime value data"
    ),
    backstory=(
        "You are a Senior Data Analyst with 7 years of experience at top e-commerce "
        "companies including two Series B startups and one Fortune 500 retailer. "
        "You specialize in funnel analysis and cohort-based CLV calculations. "
        "You always frame findings in terms of revenue impact and prioritize "
        "actionable recommendations over descriptive statistics. "
        "You are comfortable challenging assumptions and asking clarifying questions "
        "when data seems inconsistent."
    ),
    verbose=True,
    allow_delegation=False,
)

print("\nVague Agent Backstory:")
print(f"  '{vague_analyst.backstory}'")
print(f"  Character count: {len(vague_analyst.backstory)}")

print("\nSpecific Agent Backstory:")
print(f"  '{specific_analyst.backstory[:100]}...'")
print(f"  Character count: {len(specific_analyst.backstory)}")

print("\nKey differences:")
differences = [
    ("Role",       "Generic title",             "Specific title + seniority + domain"),
    ("Goal",       "Abstract verb phrase",       "Concrete metric + action + purpose"),
    ("Backstory",  "Circular (restates role)",   "Years, companies, specializations, behaviors"),
    ("Expected",   "Generic analysis output",    "Focused revenue-impact analysis"),
]
print(f"  {'Aspect':<12} {'Vague':<35} {'Specific'}")
print("  " + "-" * 70)
for aspect, vague_desc, specific_desc in differences:
    print(f"  {aspect:<12} {vague_desc:<35} {specific_desc}")

# ─── BACKSTORY WRITING GUIDELINES ────────────────────────────────────────────

print("\n" + "=" * 60)
print("How to write a strong agent backstory:")
print("=" * 60)

guidelines = [
    ("Years of experience", "Grounds the agent's expertise level"),
    ("Specific domain",     "Narrows the focus — prevents generic answers"),
    ("Company/context",     "Sets the scale and constraints they're used to"),
    ("Specializations",     "Tells it what sub-skills to emphasize"),
    ("Behavioral traits",   "Shapes HOW it responds (concise? challenger? collaborative?)"),
    ("What it avoids",      "Can specify anti-patterns ('You never use jargon without explanation')"),
]
for element, why in guidelines:
    print(f"  {element:<26} — {why}")

# ─── KEY AGENT PARAMETERS ────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Important Agent parameters:")
print("=" * 60)

# verbose=True — print the agent's step-by-step chain of thought
verbose_demo = Agent(
    role="Debugging Specialist",
    goal="Identify root causes of software bugs",
    backstory="You are a senior engineer who loves tracing bugs to their source.",
    verbose=True,   # You will see "Thought: ... Action: ... Observation: ..."
    allow_delegation=False,
)
print("\nverbose=True example:")
print("  When verbose=True, you see the agent's reasoning:")
print("  > Thought: I need to check the stack trace first")
print("  > Action: Analyze the provided error message")
print("  > Observation: The error occurs in line 42 due to a null reference")

# allow_delegation=True — agent can hand off work to other crew members
# Use carefully: can cause unexpected behavior if the crew isn't set up for it
print("\nallow_delegation=True:")
print("  The agent can say 'I need help with this — delegating to [other agent]'")
print("  Useful for a manager agent in hierarchical process")
print("  Default: False — agents work independently on their assigned tasks")

# max_iter — prevents runaway agents
# Default is 25 iterations; for simple tasks, set lower to save tokens
print("\nmax_iter parameter:")
print("  Limits how many LLM calls an agent makes per task")
print("  Default: 25 — for simple tasks, use max_iter=5 to save API costs")
print("  If an agent hits max_iter before completing, it returns best attempt")

# llm — assign a specific model to each agent
print("\nllm parameter:")
print("  Assign different models to different agents based on task complexity:")
print("  - Research agent (complex reasoning): gpt-4o")
print("  - Formatter agent (simple task):      gpt-4o-mini")
print("  This lets you balance quality and cost per task")

# ─── PRACTICAL EXAMPLE: CONTENT TEAM ────────────────────────────────────────

print("\n" + "=" * 60)
print("Practical example: A content creation team")
print("=" * 60)

# Each agent has a very specific role with behaviors that prevent overlap
# and ensure each one does exactly what's needed.

seo_researcher = Agent(
    role="SEO Keyword Research Specialist",
    goal=(
        "Identify high-value, low-competition keywords that drive organic traffic "
        "for B2B SaaS content"
    ),
    backstory=(
        "You are an SEO specialist with 6 years of experience in B2B SaaS content "
        "strategy. You have deep knowledge of search intent categorization (informational, "
        "navigational, transactional) and keyword clustering. You focus exclusively on "
        "metrics: search volume, keyword difficulty, and commercial intent score. "
        "You NEVER recommend keywords without data to back them up."
    ),
    verbose=False,
    allow_delegation=False,
    max_iter=10,    # limit iterations for cost control
)

content_writer = Agent(
    role="B2B SaaS Content Writer",
    goal=(
        "Write SEO-optimized, authoritative blog posts that rank on page 1 and "
        "convert readers into trial signups"
    ),
    backstory=(
        "You are a content writer who spent 3 years as a product manager at a SaaS "
        "company before becoming a writer. You understand buyer psychology, write in "
        "a clear and direct style (Flesch-Kincaid grade 8-10), and naturally integrate "
        "target keywords without stuffing. You always include a clear CTA aligned to "
        "the article's intent."
    ),
    verbose=False,
    allow_delegation=False,
    max_iter=15,
)

print("\nContent team agents defined:")
print(f"  1. {seo_researcher.role}")
print(f"     Goal: {seo_researcher.goal[:60]}...")
print(f"  2. {content_writer.role}")
print(f"     Goal: {content_writer.goal[:60]}...")

# Example tasks for this team
seo_task = Task(
    description=(
        "Research the top 10 keywords for the topic 'Python async programming'. "
        "Focus on keywords with developer intent and medium competition."
    ),
    expected_output=(
        "A table of 10 keywords with: keyword phrase, estimated monthly searches, "
        "difficulty (1-100), intent type, and a brief note on why to target it."
    ),
    agent=seo_researcher,
)

writing_task = Task(
    description=(
        "Using the SEO research provided, write a 1,200-word blog post targeting "
        "the primary keyword. Include: an engaging intro, 3-4 H2 sections, "
        "a practical code example, and a CTA for a Python course."
    ),
    expected_output=(
        "A complete blog post with title, meta description, all H2 headers, "
        "body content with keyword integration, and a closing CTA. "
        "Format in Markdown."
    ),
    agent=content_writer,
)

content_crew = Crew(
    agents=[seo_researcher, content_writer],
    tasks=[seo_task, writing_task],
    process=Process.sequential,
    verbose=False,
)

print("\nCrew ready. To run:")
print("  result = content_crew.kickoff()")
print("  (Requires OPENAI_API_KEY)")

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 (Rewrite the vague agent):
#   The vague_analyst agent above has a generic backstory.
#   Rewrite it for this specific context:
#     - Domain: Healthcare appointment scheduling system
#     - The analyst needs to find patterns in no-show rates
#     - The output should help clinic managers take action
#   Write a role (< 10 words), goal (1-2 sentences), and backstory (3-5 sentences).

# Exercise 2 (Identify the behavioral traits):
#   Look at the specific_analyst backstory above.
#   List EVERY behavioral trait it encodes, for example:
#     - "comfortable challenging assumptions" → will push back on bad data
#   Find at least 4 traits. For each one, explain how it changes the LLM's behavior.

# Exercise 3 (max_iter cost analysis):
#   Suppose each agent iteration = 1 LLM call at $0.0015/call.
#   Your crew has 3 agents, each with max_iter=25 (default).
#   Calculate the worst-case cost per crew.kickoff().
#   Now recalculate with max_iter=8 for simple tasks and max_iter=15 for complex ones.
#   What's the savings percentage?
