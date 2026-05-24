# Lesson 1.3 — Functions
# Python for AI Engineers | Week 1
#
# CONCEPT:
#   Python functions use `def`. Type hints are optional but highly recommended
#   (you'll need them for Pydantic and FastAPI later). Default arguments,
#   *args, and **kwargs give Python functions unusual flexibility.
#
# KOTLIN:  fun greet(name: String = "World"): String { return "Hello $name" }
# PHP:     function greet(string $name = "World"): string { return "Hello $name"; }
# PYTHON:  def greet(name: str = "World") -> str: return f"Hello {name}"

# ─── BASIC FUNCTIONS ─────────────────────────────────────────────────────────

def add(a: int, b: int) -> int:
    return a + b

print(add(3, 4))           # 7

# Multiple return values (returns a tuple — Python idiom)
def min_max(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)

low, high = min_max([3, 1, 9, 5])
print(f"min={low}, max={high}")   # min=1, max=9

# ─── DEFAULT ARGUMENTS ───────────────────────────────────────────────────────

# Like Kotlin default parameters
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

print(greet("Ali"))                    # Hello, Ali!
print(greet("Ali", "Selamat pagi"))   # Selamat pagi, Ali!

# ─── KEYWORD ARGUMENTS ───────────────────────────────────────────────────────

# Python lets you call any function with named arguments — very readable
def create_user(name: str, age: int, is_admin: bool = False) -> dict:
    return {"name": name, "age": age, "is_admin": is_admin}

user = create_user(name="Ali", age=30, is_admin=True)
user2 = create_user("Bob", 25)         # positional also works
print(user)
print(user2)

# ─── *ARGS — VARIABLE POSITIONAL ARGUMENTS ───────────────────────────────────

# Like Java/Kotlin varargs
def total(*amounts: float) -> float:
    return sum(amounts)

print(total(10.0, 20.5, 5.0))         # 35.5
print(total(1, 2, 3, 4, 5))           # 15

# ─── **KWARGS — VARIABLE KEYWORD ARGUMENTS ───────────────────────────────────

# Accepts any named arguments as a dict — very common in Python libraries
def log_event(event: str, **metadata):
    print(f"EVENT: {event}")
    for key, val in metadata.items():
        print(f"  {key}: {val}")

log_event("user_login", user_id=42, ip="192.168.1.1", success=True)
# EVENT: user_login
#   user_id: 42
#   ip: 192.168.1.1
#   success: True

# ─── COMBINING THEM ──────────────────────────────────────────────────────────

def full_example(required: str, *args, default: int = 0, **kwargs):
    print(f"required={required}, args={args}, default={default}, kwargs={kwargs}")

full_example("hello", 1, 2, 3, default=99, extra="data")

# ─── LAMBDA FUNCTIONS ────────────────────────────────────────────────────────

# Single-expression anonymous functions
# Kotlin: { x: Int -> x * 2 }
# PHP:    fn($x) => $x * 2

double = lambda x: x * 2
print(double(5))           # 10

# Common use: as a key for sorting
users = [{"name": "Charlie", "age": 30}, {"name": "Ali", "age": 25}, {"name": "Bob", "age": 35}]
sorted_users = sorted(users, key=lambda u: u["age"])
print([u["name"] for u in sorted_users])   # ['Ali', 'Charlie', 'Bob']

# ─── FIRST-CLASS FUNCTIONS ───────────────────────────────────────────────────

# Functions are objects in Python — pass them around like variables
def apply(func, value):
    return func(value)

print(apply(str.upper, "hello"))   # HELLO
print(apply(lambda x: x ** 2, 4)) # 16

# ─── TYPE HINTS WITH CALLABLE ────────────────────────────────────────────────

from typing import Callable

def run_twice(func: Callable[[int], int], value: int) -> int:
    return func(func(value))

print(run_twice(lambda x: x + 1, 5))   # 7

# ─── DOCSTRINGS ──────────────────────────────────────────────────────────────

def divide(a: float, b: float) -> float:
    """Return a divided by b. Raises ValueError if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

help(divide)               # prints the docstring


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Write a function `clamp(value: float, min_val: float, max_val: float) -> float`
#   that returns value clamped between min_val and max_val.
#   clamp(15, 0, 10) → 10
#   clamp(-5, 0, 10) → 0
#   clamp(7, 0, 10)  → 7

# Exercise 2:
#   Write a function `summarize(**stats)` that accepts any keyword arguments
#   and prints them as "key: value" pairs, sorted by key name.

# Exercise 3:
#   Use sorted() with a lambda to sort this list of strings by their LENGTH
#   (shortest first): words = ["banana", "fig", "apple", "kiwi", "strawberry"]
