# Week 6 Quiz — LangChain Agents

Test your understanding of agents, tools, the ReAct pattern, and memory.

---

## Questions

**Q1.** What is the fundamental difference between a LangChain chain and a LangChain agent?

<details><summary>Answer</summary>

**Chain**: A fixed, predetermined sequence of steps. Every input follows the same path.
```
Input → Step1 → Step2 → Step3 → Output
```
Like a Spring `@Service` with hardcoded method calls, or a Laravel pipeline.

**Agent**: The LLM dynamically decides which steps to take (and in what order) based on the input.
```
Input → [LLM thinks] → [picks tool A] → [sees result] → [picks tool B] → [Final Answer]
```
Like a while-loop where the LLM decides each iteration's action.

**When to use chains**: You know exactly what steps are needed (summarization, translation, fixed transformations).
**When to use agents**: The task requires reasoning about what to do (research, Q&A with tools, multi-step analysis).
</details>

---

**Q2.** Describe the ReAct loop. What does each step mean?

<details><summary>Answer</summary>

ReAct = **Re**asoning + **Act**ing. The LLM outputs in this structured format:

```
Thought:      I need to find the population of Malaysia.
Action:       web_search
Action Input: "Malaysia population 2024"
Observation:  Malaysia has approximately 33 million people.
Thought:      I have the information needed.
Final Answer: Malaysia's population is approximately 33 million people.
```

- **Thought**: The LLM's reasoning about what to do next
- **Action**: Which tool to call
- **Action Input**: What to pass to the tool
- **Observation**: The tool's output (fed back to the LLM)
- **Final Answer**: When the LLM determines it has enough info to answer

The `AgentExecutor` parses this text output, calls the actual tool, and feeds the result back as "Observation". This loops until "Final Answer" appears or `max_iterations` is hit.
</details>

---

**Q3.** What is `max_iterations` in `AgentExecutor` and why is it important?

<details><summary>Answer</summary>

`max_iterations` limits how many tool calls an agent can make before giving up.

```python
AgentExecutor(agent=agent, tools=tools, max_iterations=10)
```

**Why it matters**: Without this limit, a confused agent could loop forever, repeatedly calling tools and burning API credits. Some failure modes:
- LLM gets confused and keeps calling the same tool
- Tool always returns "not found" but LLM keeps trying variations
- LLM can't synthesize an answer and keeps searching

**In production**: Set this conservatively (10-15). Log when the limit is hit so you can debug.

Kotlin equivalent: A while loop with a counter: `var iterations = 0; while (iterations++ < maxIterations && !isDone) { ... }`
</details>

---

**Q4.** What are the two most important parts of a LangChain tool definition?

<details><summary>Answer</summary>

1. **The name** — the LLM uses this as an identifier to select the tool
2. **The docstring (description)** — the LLM reads this to understand when and how to use the tool

Example of a good tool description:
```python
@tool
def lookup_product(sku: str) -> str:
    """
    Looks up a product in the inventory database by its SKU code.
    Use this when the user asks about product pricing, availability, or details.
    Input: the product SKU code (e.g., 'LAPTOP-001', 'PHONE-002').
    Returns: product name, price, and stock level.
    """
```

**Bad description** = agent doesn't know when to use the tool or what to pass as input.
**Good description** = agent reliably picks the right tool and passes correct arguments.

Think of it like writing API documentation for the LLM.
</details>

---

**Q5.** What is `StructuredTool.from_function()` and when do you use it instead of `@tool`?

<details><summary>Answer</summary>

`@tool` works great for tools with a single string input.
`StructuredTool` is needed when your tool requires multiple inputs with specific types.

```python
class CurrencyConvertInput(BaseModel):
    amount: float = Field(..., description="Amount to convert")
    from_currency: str = Field(..., description="Source currency (e.g., 'USD')")
    to_currency: str = Field(..., description="Target currency (e.g., 'MYR')")

currency_converter = StructuredTool.from_function(
    func=convert_currency,
    name="currency_converter",
    description="Converts money between currencies.",
    args_schema=CurrencyConvertInput,
)
```

With `StructuredTool`, the LLM generates a JSON object matching the Pydantic schema, which is type-validated before your function is called.

Kotlin equivalent: A data class `data class ToolInput(val amount: Double, val from: String, val to: String)` parsed from the LLM's JSON output.
Laravel equivalent: A FormRequest with typed input fields.
</details>

---

**Q6.** Why is agent memory trickier than chain memory?

<details><summary>Answer</summary>

**Chain memory** is simple: the conversation history is just another variable in the prompt template:
```python
# In a chain prompt:
MessagesPlaceholder("history")  # history goes right here, predictably
```

**Agent memory is trickier** because:

1. The ReAct prompt already has a fixed structure: `{tools}`, `{tool_names}`, `{input}`, `{agent_scratchpad}`. There's no `{history}` slot by default.

2. The `agent_scratchpad` (current tool calls and observations) is separate from conversation history — they're both "previous context" but must be kept separate.

3. The agent prompt needs to clearly distinguish:
   - `chat_history` = previous conversation turns (what the human said before)
   - `agent_scratchpad` = current turn's tool calls (what tools returned this turn)

**Solution**: Use `create_openai_tools_agent` (modern approach) with a custom prompt that includes `MessagesPlaceholder("chat_history")`, or use `RunnableWithMessageHistory` carefully.
</details>

---

**Q7.** When should you return an error string from a tool vs raise an exception?

<details><summary>Answer</summary>

**Return an error string** (recommended):
```python
@tool
def divide(expression: str) -> str:
    try:
        a, b = expression.split("/")
        if float(b) == 0:
            return "Error: Cannot divide by zero. Please provide a non-zero denominator."
        return str(float(a) / float(b))
    except ValueError:
        return f"Error: Could not parse '{expression}'. Format: 'number / number'"
```

**Why**: The agent can READ the error string and potentially recover — try a different approach, ask for clarification, or explain the problem to the user.

**Raising an exception** causes the `AgentExecutor` to see a generic "Tool execution error" message, which is harder for the agent to reason about.

**Only raise exceptions** for truly unrecoverable errors (like missing API keys) that should halt execution entirely.
</details>

---

**Q8.** You have a research agent that's been running for 10 turns and the conversation history is growing large. What strategies exist to prevent hitting the LLM's context window limit?

<details><summary>Answer</summary>

Three main strategies:

**1. Sliding window (simplest)**
Keep only the last N messages:
```python
history = history[-20:]  # Keep last 10 turns (20 messages)
```
Risk: loses early context entirely.

**2. Summarization (smart)**
Periodically summarize old messages into a single summary message:
```python
summary = llm.invoke([HumanMessage(f"Summarize this conversation: {history[:10]}")])
history = [SystemMessage(summary.content)] + history[10:]
```
Preserves the meaning of old turns while reducing token count.

**3. Vector store memory (advanced)**
Store all messages in a vector DB. On each turn, retrieve only the most semantically relevant past messages:
```python
# Only include messages relevant to the current question
relevant = vector_store.similarity_search(current_question, k=5)
history = relevant  # Not chronological — relevance-based
```
Best for very long sessions.

**Practical recommendation**: Use sliding window for simple agents, summarization for long research sessions.
</details>
