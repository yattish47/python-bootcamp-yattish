# Week 8 Quiz — CrewAI: Multi-Agent Systems

Answer each question, then reveal the answer by reading the hidden text below.

---

## Question 1
What are the three core classes in CrewAI? Describe the purpose of each in one sentence.

<details>
<summary>Answer</summary>

1. **`Agent`** — An AI worker with a persona (role, goal, backstory) that shapes how the LLM responds when performing tasks.

2. **`Task`** — A unit of work that defines what needs to be done (description), what a good result looks like (expected_output), and which agent is responsible (agent).

3. **`Crew`** — The orchestrator that ties agents and tasks together and manages execution order (sequential or hierarchical).

```python
agent = Agent(role="...", goal="...", backstory="...")
task  = Task(description="...", expected_output="...", agent=agent)
crew  = Crew(agents=[agent], tasks=[task], process=Process.sequential)
result = crew.kickoff()
```
</details>

---

## Question 2
Why does the backstory of an Agent matter? What's the difference between a vague and a specific backstory?

<details>
<summary>Answer</summary>

The backstory is **injected directly into the LLM's system prompt** along with the role and goal. It shapes HOW the agent responds — not just what topic it addresses.

**Vague** backstory:
```
"You are a data analyst who works with data."
```
→ The LLM has no specific context → produces generic, mediocre responses.

**Specific** backstory:
```
"You are a Senior E-Commerce Data Analyst with 7 years of experience at
Fortune 500 retailers. You specialize in funnel analysis and CLV calculations.
You always frame findings in terms of revenue impact and challenge inconsistent data."
```
→ LLM has rich context → produces focused, expert-level responses with specific behaviors.

Key elements of a strong backstory: years of experience, domain specialization, companies/context, behavioral traits (how it communicates), and what it avoids.
</details>

---

## Question 3
What is the difference between `Process.sequential` and `Process.hierarchical` in CrewAI?

<details>
<summary>Answer</summary>

**`Process.sequential`**:
- Tasks run in the **exact order** they appear in the `tasks` list
- Each task's output is automatically passed to the next task as context
- You assign an agent to each task explicitly
- Predictable, auditable — best when the task order is clear and fixed

```python
Crew(tasks=[task_a, task_b, task_c], process=Process.sequential)
# Runs: task_a → task_b → task_c
```

**`Process.hierarchical`**:
- A **manager agent** (created automatically or specified) reads all tasks
- The manager dynamically decides which agent handles each task
- The manager can re-assign if output quality isn't satisfactory
- Requires `manager_llm="gpt-4o"` or `manager_agent=...`

```python
Crew(agents=[...], tasks=[...], process=Process.hierarchical, manager_llm="gpt-4o")
```

Use sequential when task order is clear. Use hierarchical when assignments are complex or when you need dynamic quality control.
</details>

---

## Question 4
What does the `context` parameter on a `Task` do? When would you use it explicitly instead of relying on sequential order?

<details>
<summary>Answer</summary>

`context=[task_a, task_b]` makes the **output of those tasks available as input** to the current task. The LLM receives: `[task_a output] + [task_b output] + current task description`.

In `Process.sequential`, this happens automatically (each task gets all previous outputs). You use `context=` explicitly when:

1. **Non-linear flow** — task C should get output of task A but NOT task B
2. **Parallel execution** — tasks with `async_execution=True` don't have automatic sequencing
3. **Clarity** — you want to be explicit about dependencies for readability

```python
# Task 3 depends on Tasks 1 and 2, but NOT task 2 alone
task_3 = Task(
    description="Synthesize research and metrics...",
    agent=writer,
    context=[research_task, data_task],  # explicit dependency
)
```
</details>

---

## Question 5
What is the principle of least privilege when assigning tools to agents? Why does it matter?

<details>
<summary>Answer</summary>

**Principle of least privilege** = give each agent **only the tools it actually needs** for its specific role, nothing more.

```python
# Good: scoped tools
researcher = Agent(tools=[search_tool])      # only searches
analyst    = Agent(tools=[database_tool])    # only queries DB
writer     = Agent(tools=[])                 # no tools needed

# Bad: every agent gets everything
every_agent = Agent(tools=[search_tool, database_tool, file_writer, deploy_tool])
```

Why it matters:
- **Better decisions** — agents with fewer tools are clearer on when to use each one
- **Lower cost** — fewer spurious tool calls = fewer LLM tokens consumed
- **Easier debugging** — you know exactly which tools each agent can invoke
- **Security** — a writer agent can't accidentally trigger a database write or deployment
- **Separation of concerns** — mirrors good software architecture principles

This is the same principle as in Spring Security (method-level security) or Laravel Gates (policy-per-model).
</details>

---

## Question 6
How do you save a task's output to a file in CrewAI?

<details>
<summary>Answer</summary>

Use the `output_file` parameter on the `Task`:

```python
final_task = Task(
    description="Write a complete market analysis report.",
    expected_output="A 500-word Markdown report with 4 sections.",
    agent=writer_agent,
    output_file="reports/market_analysis.md",  # relative to working directory
)
```

After `crew.kickoff()` completes, CrewAI **automatically writes** the agent's output for that task to the specified file path. The directory must exist (or you must create it before running).

Useful for:
- Saving reports for human review
- Generating code files that will be used by other systems
- Creating documentation files
- Persisting results between crew runs
</details>

---

## Question 7
What does `allow_delegation=True` do on an Agent? When should you use it?

<details>
<summary>Answer</summary>

`allow_delegation=True` means the agent can **hand off work to another crew member** if it decides it needs help or that another agent is better suited for a sub-task.

When the agent uses delegation, it effectively says: "I'll ask [other agent] to handle this part."

**Use it for**:
- A manager/coordinator agent in a hierarchical process
- An agent that might encounter sub-tasks outside its expertise

**Default is `False`** — most specialist agents should NOT delegate. Delegation can cause:
- Unexpected behavior if the crew isn't designed for it
- Infinite delegation loops
- Harder debugging

```python
# Manager agent — should delegate
manager = Agent(role="Project Manager", allow_delegation=True, ...)

# Worker agents — should NOT delegate
researcher = Agent(role="Researcher", allow_delegation=False, ...)
writer     = Agent(role="Writer",     allow_delegation=False, ...)
```
</details>

---

## Question 8
Compare LangGraph and CrewAI. If you were building a production AI system that needed both complex branching logic AND multi-agent collaboration, how would you approach combining them?

<details>
<summary>Answer</summary>

| Aspect | LangGraph | CrewAI |
|--------|-----------|--------|
| Control | Explicit — you define every transition | Implicit — framework orchestrates |
| State management | TypedDict flowing through nodes | Tasks pass output via context |
| Best for | Complex conditional flows, loops, human-in-the-loop | Multi-agent collaboration, specialized roles |
| Debugging | Full trace of every node | verbose=True shows agent reasoning |
| Human-in-the-loop | First-class (interrupt_before) | Possible via human_input=True on tasks |

**Combining them in production:**

Use **LangGraph as the outer orchestrator** and **CrewAI as a node** within the graph:

```python
# LangGraph node that delegates to a CrewAI sub-crew
def run_research_crew(state: AgentState) -> dict:
    crew = build_research_crew(state["topic"])
    result = crew.kickoff()
    return {"research_output": str(result)}

# LangGraph handles the overall flow with branching and checkpoints
builder.add_node("run_research", run_research_crew)
builder.add_node("human_review", human_review_node)
# etc.
```

This gives you:
- LangGraph: routing, loops, human-in-the-loop checkpoints, overall state management
- CrewAI: specialized agent collaboration within a specific phase of the workflow

This pattern is common in production systems where you need both fine-grained control and multi-agent collaboration.
</details>
