# Week 6 — LangChain Agents

## Setup

```bash
pip install langchain langchain-openai langchain-community tavily-python python-dotenv
```

Create a `.env` file in `week_06/`:
```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...   # Optional — get free tier at https://tavily.com
```

If no `TAVILY_API_KEY`, lessons fall back to **DuckDuckGo** (no API key needed).

---

## Lessons

| File | Topic |
|---|---|
| `lesson_6_1_agent_intro.py` | What agents are, ReAct loop, AgentExecutor |
| `lesson_6_2_builtin_tools.py` | TavilySearch, DuckDuckGo, Wikipedia, Calculator |
| `lesson_6_3_custom_tools.py` | @tool decorator, StructuredTool, Pydantic validation in tools |
| `lesson_6_4_agent_memory.py` | Memory with agents, chat_history, reasoning traces |

---

## Agent vs Chain: What's the Difference?

| | Chain | Agent |
|---|---|---|
| **Execution** | Fixed sequence of steps | LLM decides which steps to take |
| **Tools** | No tools (or fixed tools in fixed order) | LLM chooses from a toolbox |
| **Loops** | Runs once | Loops until the task is done |
| **Predictable?** | Yes — same input, same path | No — LLM decides dynamically |
| **Use when** | You know exactly what steps are needed | The task requires reasoning about what to do |

### Analogy
- **Chain** = a recipe (fixed steps: chop, fry, plate)
- **Agent** = a chef (decides what to cook based on available ingredients, adjusts when something goes wrong)

---

## The ReAct Loop

Agents follow the **ReAct** pattern (Reasoning + Acting):

```
Question → Thought → Action → Observation → Thought → Action → ... → Final Answer
```

Example for "What is the population of Malaysia?":
```
Thought: I need to search for the current population of Malaysia.
Action: TavilySearch("Malaysia population 2024")
Observation: Malaysia has approximately 33 million people as of 2024.
Thought: I have the answer now.
Final Answer: Malaysia's population is approximately 33 million people.
```

---

## Framework Comparison

### vs Spring Boot (Kotlin)
- `AgentExecutor` ≈ a `@Service` with a decision loop
- Tools ≈ `@Component` beans the agent can call
- Tool descriptions ≈ API documentation that the LLM reads
- Memory ≈ a `ConcurrentHashMap` storing conversation state

### vs Laravel (PHP)
- AgentExecutor ≈ a Laravel job that dispatches other jobs based on LLM output
- Tools ≈ Laravel Actions or Service classes
- Tool registry ≈ Laravel's service container, but the LLM picks what to call
