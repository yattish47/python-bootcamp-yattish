# Week 8 — CrewAI: Multi-Agent Systems

## Setup

```bash
pip install crewai crewai-tools python-dotenv
```

> **Note:** CrewAI requires **Python 3.10 or higher**.
> Check your version: `python3 --version`
> If you're on 3.9 or below, upgrade first.

Add your OpenAI key to a `.env` file in the project root:
```
OPENAI_API_KEY=sk-...
```

---

## Lessons

| File | Topic |
|------|-------|
| `lesson_8_1_crewai_intro.py` | Agent, Task, Crew — the three core classes |
| `lesson_8_2_agent_roles.py` | Role, goal, backstory — shaping agent behavior |
| `lesson_8_3_task_flow.py` | Sequential vs hierarchical, task context, output files |
| `lesson_8_4_tools_in_crews.py` | Attaching tools to agents, principle of least privilege |
| `project/research_crew.py` | Complete 3-agent research crew: Researcher → Writer → Editor |

---

## Key Concept

**CrewAI = multiple specialized AI agents working as a team.**

Each agent has:
- A **role** — what kind of expert it is ("Senior Data Analyst")
- A **goal** — what it's trying to achieve ("Provide accurate data insights")
- A **backstory** — its personality and context ("You have 10 years of experience...")

Tasks define **what needs to be done** and **who does it**. The Crew orchestrates execution.

```
Crew
 ├── Agent: Researcher  ──→  Task: Research the topic
 ├── Agent: Writer      ──→  Task: Write the article
 └── Agent: Editor      ──→  Task: Review and improve
```

---

## LangGraph vs CrewAI — When to Use Which

| Aspect | LangGraph | CrewAI |
|--------|-----------|--------|
| Control model | You define every transition explicitly | You describe roles/tasks, framework orchestrates |
| Best for | Complex workflows with custom branching logic | Multi-agent collaboration with specialized roles |
| State management | TypedDict flowing through nodes | Tasks pass output to each other via `context` |
| Human-in-the-loop | First-class feature (interrupt_before) | Possible but more manual |
| Debugging | Full trace of every node transition | Verbose mode shows agent reasoning |
| Mental model | Explicit state machine | Team of coworkers with job descriptions |

**Rule of thumb:**
- Need fine-grained control over every step → **LangGraph**
- Need a team of specialists that collaborate naturally → **CrewAI**
- Complex product with both patterns → **combine them** (LangGraph orchestrates, CrewAI sub-teams handle sub-tasks)

---

## Mental Model (for Kotlin/Spring developers)

CrewAI is like **defining microservices where each has a clear responsibility**:

- `Agent` = a microservice with a specific domain expertise
- `Task` = an API contract (what the service must produce)
- `Crew` = an orchestration layer (like a Kubernetes deployment or Spring Batch job)
- `Process.sequential` = pipeline pattern (each service calls the next)
- `Process.hierarchical` = event-driven pattern (manager dispatches to workers)
- `context=[task_a]` = the output of service A is an input to service B
