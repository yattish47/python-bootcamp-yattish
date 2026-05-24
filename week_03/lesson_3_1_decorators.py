# Lesson 3.1 — Decorators, Context Managers, Generators
# Python for AI Engineers | Week 3
#
# CONCEPT:
#   Decorators wrap a function with extra behaviour without modifying its source.
#   Context managers guarantee setup/teardown around a block of code.
#   Generators produce values lazily — one at a time — using `yield`.
#
# KOTLIN EQUIVALENT:
#   Decorators ≈ extension functions + annotations (e.g., @Transactional, @Cacheable)
#   Context managers ≈ Kotlin's `use { }` (Closeable.use)
#   Generators ≈ Kotlin Sequences (`sequence { yield(x) }`)
#
# PHP EQUIVALENT:
#   Decorators ≈ PHP Attributes (#[Attribute]) + middleware wrappers
#   Context managers: no direct equivalent; closest is try/finally
#   Generators ≈ PHP `yield` inside a function returning Generator

import time
import functools
import contextlib
from typing import Callable, Generator, Any

# ─── DECORATORS ──────────────────────────────────────────────────────────────

# A decorator is just a function that takes a function and returns a function.
# The `@` syntax is shorthand for:  my_func = timer(my_func)

def timer(func: Callable) -> Callable:
    """Measure and print how long a function takes to run."""
    @functools.wraps(func)          # preserves __name__, __doc__ of the wrapped fn
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


@timer
def slow_operation(n: int) -> int:
    """Simulate work."""
    total = 0
    for i in range(n):
        total += i
    return total


result = slow_operation(1_000_000)
print(f"Result: {result}")
# [timer] slow_operation took 0.0421s
# Result: 499999500000

# ─── RETRY DECORATOR ─────────────────────────────────────────────────────────

# A decorator factory: outer function takes config, returns the actual decorator.
# This is the pattern for decorators that accept arguments.

def retry(max_attempts: int = 3, delay: float = 0.5, exceptions: tuple = (Exception,)):
    """Retry a function up to max_attempts times on failure."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    print(f"[retry] Attempt {attempt}/{max_attempts} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_error
        return wrapper
    return decorator


_call_count = 0

@retry(max_attempts=3, delay=0.1, exceptions=(ValueError,))
def flaky_api_call() -> str:
    """Simulates an API that fails the first two times."""
    global _call_count
    _call_count += 1
    if _call_count < 3:
        raise ValueError(f"Temporary API error (call #{_call_count})")
    _call_count = 0          # reset for re-use
    return "API response: success"


print(flaky_api_call())
# [retry] Attempt 1/3 failed: Temporary API error (call #1)
# [retry] Attempt 2/3 failed: Temporary API error (call #2)
# API response: success

# ─── STACKING DECORATORS ─────────────────────────────────────────────────────

# Decorators apply bottom-up: @timer wraps the result of @retry wrapping the fn.

@timer
@retry(max_attempts=2, delay=0.0)
def double_decorated(x: int) -> int:
    return x * 2

print(double_decorated(21))


# ─── CONTEXT MANAGERS ────────────────────────────────────────────────────────

# The `with` statement calls __enter__ on entry and __exit__ on exit
# (even if an exception is raised — like try/finally but cleaner).

class ManagedResource:
    """A custom context manager via __enter__ / __exit__ dunder methods."""

    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        print(f"[resource] Opening: {self.name}")
        return self           # value bound to `as` variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[resource] Closing: {self.name}")
        # Return True to suppress exceptions; False/None to let them propagate
        return False

    def do_work(self) -> str:
        return f"Working with {self.name}"


with ManagedResource("database-connection") as res:
    print(res.do_work())
# [resource] Opening: database-connection
# Working with database-connection
# [resource] Closing: database-connection


# ─── contextlib.contextmanager ────────────────────────────────────────────────

# Easier way to write context managers using a generator with a single yield.
# Everything before yield = __enter__; everything after = __exit__.

@contextlib.contextmanager
def timer_context(label: str) -> Generator:
    """Context manager version of a timer."""
    start = time.perf_counter()
    try:
        yield                  # code inside `with` block runs here
    finally:
        elapsed = time.perf_counter() - start
        print(f"[timer_context] {label}: {elapsed:.4f}s")


with timer_context("data processing"):
    data = [i ** 2 for i in range(500_000)]
    print(f"Processed {len(data)} items")
# Processed 500000 items
# [timer_context] data processing: 0.0312s


# ─── GENERATORS ──────────────────────────────────────────────────────────────

# A generator function uses `yield` instead of `return`.
# It returns a Generator object — values are produced one at a time (lazily).
# This is critical for streaming AI responses: you process each token as it arrives
# rather than waiting for the entire response before doing anything.

def count_up(start: int, end: int) -> Generator[int, None, None]:
    """Yield integers from start to end (lazy — no list created in memory)."""
    current = start
    while current <= end:
        yield current
        current += 1


gen = count_up(1, 5)
print(next(gen))   # 1  — generator pauses after yielding
print(next(gen))   # 2
print(next(gen))   # 3

for n in count_up(4, 6):
    print(n)       # 4, 5, 6


# ─── GENERATOR FOR SIMULATED STREAMING ───────────────────────────────────────

def simulate_streaming_response(text: str) -> Generator[str, None, None]:
    """
    Simulate an LLM streaming response: yield one word at a time.
    In real LangChain code you'd use chain.stream({}) which does the same thing.
    """
    words = text.split()
    for word in words:
        time.sleep(0.05)       # simulate network latency per token
        yield word + " "


print("Streaming response: ", end="", flush=True)
for token in simulate_streaming_response("Hello I am an AI assistant"):
    print(token, end="", flush=True)
print()   # newline


# ─── GENERATOR EXPRESSIONS ───────────────────────────────────────────────────

# Like list comprehensions but lazy — use () instead of []
squares_gen = (x ** 2 for x in range(1_000_000))   # no memory allocated yet
first_five = [next(squares_gen) for _ in range(5)]
print(first_five)   # [0, 1, 4, 9, 16]


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 — LOG DECORATOR
#   Write a decorator called `log_calls` that prints the function name,
#   the arguments it was called with, and the value it returned.
#   Apply it to a function `add(a, b)` and call add(3, 4).
#   Expected output:
#     [log] add called with args=(3, 4), kwargs={}
#     [log] add returned 7

# Exercise 2 — TEMP FILE CONTEXT MANAGER
#   Using @contextlib.contextmanager, write a context manager called
#   `temp_file(path)` that:
#     1. Creates a file at `path` on enter and yields the open file handle.
#     2. Deletes the file on exit (use pathlib.Path.unlink).
#   Demonstrate it writing "hello" to /tmp/test_cm.txt, then confirm the file
#   is gone after the with block.

# Exercise 3 — FIBONACCI GENERATOR
#   Write a generator function `fibonacci()` that yields the Fibonacci sequence
#   indefinitely (no upper bound). Use `itertools.islice` to print the first
#   15 numbers. Why is a generator better than building a list here?
