# Lesson 3.2 — Async / Await
# Python for AI Engineers | Week 3
#
# CONCEPT:
#   `async def` defines a coroutine — a function that can pause (await) without
#   blocking the thread. asyncio is Python's event loop that schedules coroutines.
#   LLM API calls are I/O-bound: the CPU sits idle waiting for the network.
#   Async lets you fire off multiple API calls concurrently and await them all.
#
# KOTLIN EQUIVALENT:
#   `async def` ≈ `suspend fun`
#   `await`     ≈ the implicit suspension in a suspend function
#   `asyncio.gather()` ≈ `awaitAll()` / `async { }.await()` in coroutines
#   `asyncio.run()` ≈ `runBlocking { }` as the entry point
#
# PHP EQUIVALENT:
#   PHP has no native async/await. ReactPHP / Amp exist for event-loop async,
#   but they're rarely used in practice. PHP typically relies on horizontal
#   scaling (multiple processes/requests) rather than in-process concurrency.
#   For AI projects in PHP you'd generally just make synchronous HTTP calls.

from __future__ import annotations

import asyncio
import time

# ─── BASIC ASYNC / AWAIT ─────────────────────────────────────────────────────

# A coroutine function — calling it returns a coroutine object, NOT a result.
# You must `await` it (inside another async fn) or run it with asyncio.run().

async def greet(name: str) -> str:
    await asyncio.sleep(0.1)      # non-blocking pause (simulates network I/O)
    return f"Hello, {name}!"


async def main_basic():
    message = await greet("Yattish")
    print(message)                # Hello, Yattish!


asyncio.run(main_basic())


# ─── WHY ASYNC MATTERS FOR LLM CALLS ─────────────────────────────────────────

# Synchronous version: calls happen one after another → 3× slower
def sync_llm_call(prompt: str) -> str:
    time.sleep(1.0)               # simulate 1 second API latency
    return f"Response to: {prompt}"


def run_sync_calls():
    start = time.perf_counter()
    results = [
        sync_llm_call("prompt 1"),
        sync_llm_call("prompt 2"),
        sync_llm_call("prompt 3"),
    ]
    elapsed = time.perf_counter() - start
    print(f"Sync: {len(results)} calls took {elapsed:.2f}s")   # ~3.00s


run_sync_calls()


# Async version: all 3 calls run concurrently → ~1× latency
async def async_llm_call(prompt: str) -> str:
    await asyncio.sleep(1.0)      # same simulated latency, but non-blocking
    return f"Response to: {prompt}"


async def run_async_calls():
    start = time.perf_counter()
    results = await asyncio.gather(
        async_llm_call("prompt 1"),
        async_llm_call("prompt 2"),
        async_llm_call("prompt 3"),
    )
    elapsed = time.perf_counter() - start
    print(f"Async: {len(results)} calls took {elapsed:.2f}s")  # ~1.00s
    for r in results:
        print(" ", r)


asyncio.run(run_async_calls())


# ─── asyncio.gather() IN DEPTH ───────────────────────────────────────────────

# gather() runs coroutines concurrently and collects results in order.
# If any coroutine raises, gather() raises that exception by default.
# Use return_exceptions=True to collect exceptions as values instead.

async def might_fail(label: str, should_fail: bool) -> str:
    await asyncio.sleep(0.2)
    if should_fail:
        raise ValueError(f"{label} failed!")
    return f"{label} succeeded"


async def gather_with_errors():
    results = await asyncio.gather(
        might_fail("task-1", False),
        might_fail("task-2", True),    # this one raises
        might_fail("task-3", False),
        return_exceptions=True,        # don't let one failure cancel others
    )
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"  task-{i}: ERROR — {result}")
        else:
            print(f"  task-{i}: {result}")


print("\ngather with errors:")
asyncio.run(gather_with_errors())


# ─── PRACTICAL EXAMPLE — CONCURRENT OPENAI CALLS ─────────────────────────────

# This shows the real pattern you'd use with the OpenAI async client.
# We simulate it here without actually calling the API so no key is needed.

async def call_openai_simulated(prompt: str, model: str = "gpt-4o-mini") -> dict:
    """Simulates an async OpenAI chat completion call."""
    await asyncio.sleep(0.8)          # realistic API latency
    return {
        "prompt": prompt,
        "model": model,
        "response": f"AI answer to '{prompt[:30]}...'",
    }


async def batch_classify(texts: list[str]) -> list[dict]:
    """
    Classify multiple texts concurrently.
    Real version would use: openai.AsyncOpenAI() and await client.chat.completions.create(...)
    """
    prompts = [f"Classify the sentiment of: {text}" for text in texts]
    tasks = [call_openai_simulated(p) for p in prompts]
    results = await asyncio.gather(*tasks)
    return list(results)


async def demo_batch():
    texts = [
        "I love this product!",
        "This is absolutely terrible.",
        "Meh, it's okay I guess.",
    ]
    start = time.perf_counter()
    results = await batch_classify(texts)
    elapsed = time.perf_counter() - start
    print(f"\nBatch classified {len(texts)} texts in {elapsed:.2f}s (concurrent)")
    for r in results:
        print(f"  [{r['model']}] {r['response']}")


asyncio.run(demo_batch())


# ─── REAL ASYNC OPENAI PATTERN (commented out — requires API key) ─────────────

# from openai import AsyncOpenAI
#
# async def real_concurrent_calls():
#     client = AsyncOpenAI()          # async client — same interface, all methods are coroutines
#
#     async def ask(question: str) -> str:
#         response = await client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": question}],
#         )
#         return response.choices[0].message.content
#
#     questions = ["What is 2+2?", "Name a colour.", "What is Python?"]
#     answers = await asyncio.gather(*[ask(q) for q in questions])
#     for q, a in zip(questions, answers):
#         print(f"Q: {q}\nA: {a}\n")
#
# asyncio.run(real_concurrent_calls())


# ─── ASYNC vs THREADING vs MULTIPROCESSING ───────────────────────────────────

# ┌──────────────────┬───────────────────────────────────────────────────────┐
# │ Approach         │ Best for                                              │
# ├──────────────────┼───────────────────────────────────────────────────────┤
# │ asyncio (async)  │ I/O-bound work: API calls, DB queries, file reads     │
# │                  │ Single thread, event loop switches between coroutines  │
# │                  │ Very low overhead, thousands of concurrent tasks OK   │
# ├──────────────────┼───────────────────────────────────────────────────────┤
# │ threading        │ I/O-bound, but with blocking libraries (no async      │
# │                  │ support). Actual OS threads — GIL limits true         │
# │                  │ parallelism for CPU work but fine for I/O.            │
# ├──────────────────┼───────────────────────────────────────────────────────┤
# │ multiprocessing  │ CPU-bound work: image processing, ML inference,       │
# │                  │ number crunching. Bypasses the GIL with separate      │
# │                  │ processes. Higher memory cost.                        │
# └──────────────────┴───────────────────────────────────────────────────────┘

# For AI agent projects: asyncio is almost always what you want.
# LLM API calls = network I/O = asyncio is the right tool.


# ─── asyncio.create_task() — FIRE AND DON'T WAIT ─────────────────────────────

async def background_logger(message: str) -> None:
    """Run this without blocking the main flow."""
    await asyncio.sleep(0.1)
    print(f"[bg] {message}")


async def main_with_task():
    # Schedule background_logger to run "soon" but don't await it yet
    task = asyncio.create_task(background_logger("logging in background"))

    # Main work continues immediately
    print("Main: doing important work...")
    await asyncio.sleep(0.2)
    print("Main: done.")

    await task   # ensure the background task finishes before we exit


asyncio.run(main_with_task())


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 — CONCURRENT FETCHER
#   Write an async function `fetch_all(urls: list[str])` that uses asyncio.gather
#   to "fetch" all URLs concurrently. Simulate each fetch with asyncio.sleep(0.5).
#   Return a list of strings like "Fetched: <url>".
#   Time the execution and confirm all N fetches complete in ~0.5s total
#   regardless of how many URLs you pass.

# Exercise 2 — ASYNC RETRY DECORATOR
#   Write an async decorator `async_retry(max_attempts=3)` that wraps an async
#   function and retries it on exception. Test it with an async function that
#   fails the first 2 calls then succeeds.
#   Hint: the wrapper must also be `async def`.

# Exercise 3 — PRODUCER / CONSUMER
#   Use asyncio.Queue to build a simple producer/consumer:
#     - producer() puts 5 items into a queue (simulating API results arriving)
#     - consumer() processes items from the queue as they arrive
#   Run both concurrently with asyncio.gather and print each item as processed.
