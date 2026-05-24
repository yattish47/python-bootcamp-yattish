# Week 3 Quiz — Power Features + LangChain

Test your understanding of decorators, async/await, LangChain chains, and conversation memory.

---

**Question 1**
What does `@functools.wraps(func)` do inside a decorator, and why should you always include it?

<details>
<summary>Answer</summary>

`@functools.wraps(func)` copies the wrapped function's `__name__`, `__doc__`, `__module__`, and other metadata onto the wrapper function. Without it, all decorated functions would appear to have the name `wrapper` when inspected, breaking tools like debuggers, loggers, and documentation generators. Always include it to preserve the original function's identity.

</details>

---

**Question 2**
What is the difference between a decorator and a decorator factory? Write the skeleton of each.

<details>
<summary>Answer</summary>

A **decorator** takes a function and returns a function:
```python
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(): ...
```

A **decorator factory** takes configuration arguments and returns a decorator (one extra level of nesting):
```python
def retry(max_attempts=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    pass
        return wrapper
    return decorator

@retry(max_attempts=5)
def flaky(): ...
```

</details>

---

**Question 3**
Explain why `asyncio.gather()` makes LLM API calls faster. What would happen if you called three APIs sequentially with `await` instead?

<details>
<summary>Answer</summary>

`asyncio.gather()` schedules all coroutines to run **concurrently** on the event loop. When coroutine A is waiting for the network (blocked on I/O), the event loop switches to coroutine B, then C. So all three API calls are in-flight at the same time. Total time ≈ the slowest single call.

With sequential `await`:
```python
r1 = await call_api("prompt 1")   # waits 1s
r2 = await call_api("prompt 2")   # waits another 1s
r3 = await call_api("prompt 3")   # waits another 1s
# Total: ~3s
```
With `gather()`:
```python
r1, r2, r3 = await asyncio.gather(
    call_api("prompt 1"),
    call_api("prompt 2"),
    call_api("prompt 3"),
)
# Total: ~1s
```

</details>

---

**Question 4**
What does the `|` pipe operator do in LangChain? What Python feature makes this possible?

<details>
<summary>Answer</summary>

The `|` operator in LCEL (LangChain Expression Language) composes two Runnables into a chain where the output of the left side becomes the input of the right side:

```python
chain = prompt | llm | parser
# chain.invoke(inputs) == parser(llm(prompt.invoke(inputs)))
```

This is possible because LangChain's `Runnable` base class implements the **`__or__`** dunder method. When Python evaluates `a | b`, it calls `a.__or__(b)` which returns a new `RunnableSequence` that calls them in order.

</details>

---

**Question 5**
A LangChain `ChatPromptTemplate` contains a `MessagesPlaceholder(variable_name="chat_history")`. What gets substituted there, and where does it come from?

<details>
<summary>Answer</summary>

The `MessagesPlaceholder` is replaced at invocation time by the list of `BaseMessage` objects stored under the key `"chat_history"` in the input dict. When using `RunnableWithMessageHistory`, the wrapper automatically loads the `ChatMessageHistory` for the given `session_id` and injects its `.messages` list into that placeholder before the prompt reaches the LLM.

So the final prompt sent to the LLM includes: system message → all previous human/AI turns → the new human message.

</details>

---

**Question 6**
What is a generator function, and why is it better than returning a list for streaming AI responses?

<details>
<summary>Answer</summary>

A generator function uses `yield` to produce values one at a time, pausing execution between each yield. It returns a generator object rather than computing all values upfront.

For streaming AI responses:
- A **list** would require the entire response to be received and stored in memory before any token is shown to the user — adding perceived latency.
- A **generator** (or async generator) yields each token/chunk as it arrives, so the user sees text appearing in real time even while the model is still generating.

LangChain's `.stream()` method returns a generator-like iterator for exactly this reason.

```python
# Streaming — user sees tokens immediately
for chunk in chain.stream({"input": "hello"}):
    print(chunk, end="", flush=True)
```

</details>

---

**Question 7**
What is the purpose of `session_id` in `RunnableWithMessageHistory`? How would you use it in a multi-user app?

<details>
<summary>Answer</summary>

`session_id` is the key used to look up (or create) a user's `ChatMessageHistory` from the session store. Each unique `session_id` gets its own isolated conversation history.

In a multi-user app you'd derive `session_id` from something that uniquely identifies a user's conversation thread:

```python
# REST API endpoint example
def chat_endpoint(user_id: str, thread_id: str, message: str) -> str:
    session_id = f"{user_id}:{thread_id}"
    config = {"configurable": {"session_id": session_id}}
    return chain_with_memory.invoke({"input": message}, config=config)
```

This ensures user A's conversation never leaks into user B's context.

</details>

---

**Question 8**
Your LangChain chain does: `prompt | llm | StrOutputParser()`. The LLM returns an `AIMessage`. Trace what happens to that object at each step.

<details>
<summary>Answer</summary>

1. **`prompt.invoke(inputs)`** — `ChatPromptTemplate` substitutes variables and produces a `ChatPromptValue` (a wrapper around a list of `BaseMessage` objects).

2. **`llm.invoke(chat_prompt_value)`** — `ChatOpenAI` sends the messages to the OpenAI API and returns an **`AIMessage`** object with `.content` holding the text and `.response_metadata` holding token counts, model name, etc.

3. **`StrOutputParser().invoke(ai_message)`** — extracts and returns `ai_message.content` as a plain Python `str`.

So the final result of `chain.invoke(...)` is a `str`, not an `AIMessage`. This is why `StrOutputParser` is the last step in most simple chains.

</details>
