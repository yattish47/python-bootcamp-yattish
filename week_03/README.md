# Week 3 — Power Features + LangChain

## Setup

```bash
pip install langchain langchain-openai
```

Create a `.env` file in this directory:

```
OPENAI_API_KEY=sk-...your-key-here...
```

---

## Lessons

| File | Topic | Key Concept |
|------|-------|-------------|
| `lesson_3_1_decorators.py` | Decorators, Context Managers, Generators | Functions wrapping functions; `with` blocks; `yield` |
| `lesson_3_2_async.py` | Async / Await | `asyncio`, `gather()`, concurrent LLM calls |
| `lesson_3_3_langchain_basics.py` | LangChain Basics | Chains, LCEL pipe operator, `ChatOpenAI` |
| `lesson_3_4_memory.py` | Conversation Memory | `ChatMessageHistory`, `RunnableWithMessageHistory` |

---

## What is LangChain?

**Raw OpenAI SDK** gives you direct access to the API — you send messages, you get a response. Simple, but you write all the boilerplate yourself: prompt templates, parsing output, chaining calls, managing memory.

**LangChain** is a framework of abstractions built *on top of* the OpenAI SDK (and many other LLM providers). It gives you:

- **Prompt templates** — reusable, parameterised prompts
- **Chains** — composable pipelines using the `|` pipe operator (LCEL)
- **Memory** — built-in patterns for conversation history
- **Integrations** — vector stores, document loaders, tools, agents
- **Model portability** — swap `ChatOpenAI` for `ChatAnthropic` or `ChatGoogleGenerativeAI` with one line

**When to use raw SDK:** simple one-off calls, tight control, minimal dependencies.
**When to use LangChain:** building conversational agents, RAG pipelines, multi-step chains, anything where you need memory or tool use at scale.

---

## Project

`project/memory_chatbot.py` — a full CLI chatbot with persistent conversation memory per session.

```bash
cd week_03
python project/memory_chatbot.py
```
