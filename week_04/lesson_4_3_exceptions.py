# Lesson 4.3 — Exception Handling
# Python for AI Engineers | Week 4
#
# CONCEPT:
#   Python uses try/except/else/finally. Catching specific exceptions is
#   critical — bare `except` catches EVERYTHING including keyboard interrupts.
#   AI apps fail in interesting ways: rate limits, timeouts, JSON parse errors,
#   API quota exceeded. Proper exception handling makes your agent resilient.
#
# KOTLIN EQUIVALENT:
#   try { } catch (e: SpecificException) { } finally { }
#   throw IllegalArgumentException("msg")
#   All exceptions are unchecked in Kotlin (no checked exceptions like Java)
#
# PHP EQUIVALENT:
#   try { } catch (SpecificException $e) { } finally { }
#   throw new RuntimeException("msg", 0, $previous)
#   Custom exceptions: class MyException extends RuntimeException {}

from __future__ import annotations

# ─── BASIC try / except ───────────────────────────────────────────────────────

def parse_number(text: str) -> float:
    """Convert a string to float, raising a clear error on failure."""
    try:
        return float(text)
    except ValueError as e:
        print(f"  [parse_number] Cannot convert '{text}' to float: {e}")
        return 0.0


print(parse_number("3.14"))    # 3.14
print(parse_number("abc"))     # prints error, returns 0.0
print(parse_number("1_000"))   # 1000.0 — Python allows underscores in numeric literals


# ─── MULTIPLE EXCEPT CLAUSES ─────────────────────────────────────────────────

def read_config_value(config: dict, key: str) -> str:
    """Demonstrate catching multiple specific exceptions."""
    try:
        value = config[key]           # might raise KeyError
        return str(value).strip()     # might raise AttributeError
    except KeyError:
        print(f"  Key '{key}' not found in config")
        return ""
    except (TypeError, AttributeError) as e:
        # Catching multiple types together
        print(f"  Bad config value for '{key}': {e}")
        return ""


print(read_config_value({"model": "gpt-4o"}, "model"))     # gpt-4o
print(read_config_value({"model": "gpt-4o"}, "missing"))   # KeyError path
print(read_config_value({"model": None}, "model"))          # AttributeError path


# ─── else AND finally ────────────────────────────────────────────────────────

# else:    runs only if NO exception was raised in try
# finally: ALWAYS runs — used for cleanup (close files, release locks, etc.)

def safe_divide(a: float, b: float) -> float | None:
    try:
        result = a / b
    except ZeroDivisionError:
        print("  Cannot divide by zero")
        return None
    else:
        # Only reached if no exception — result is available here
        print(f"  Division succeeded: {a} / {b} = {result}")
        return result
    finally:
        # Always runs — good for cleanup
        print("  [finally] Division operation complete")


print("\nDivision examples:")
safe_divide(10, 2)
safe_divide(10, 0)


# ─── raise ─── RAISING EXCEPTIONS ─────────────────────────────────────────────

def validate_age(age: int) -> None:
    """Demonstrate raising exceptions with clear messages."""
    if not isinstance(age, int):
        raise TypeError(f"age must be int, got {type(age).__name__}")
    if age < 0:
        raise ValueError(f"age cannot be negative: {age}")
    if age > 150:
        raise ValueError(f"age {age} is unrealistically large")


try:
    validate_age(-5)
except ValueError as e:
    print(f"\nValidation error: {e}")

try:
    validate_age("twenty")
except TypeError as e:
    print(f"Type error: {e}")


# ─── raise ... from ... — EXCEPTION CHAINING ────────────────────────────────

# When you catch one exception and raise a different one, use `raise X from Y`
# to preserve the original cause. This shows both in the traceback.

class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


def load_api_key(env_var: str) -> str:
    """Load an API key, wrapping the underlying error with context."""
    import os
    value = os.getenv(env_var)
    if not value:
        original = KeyError(f"Environment variable '{env_var}' not set")
        raise ConfigError(
            f"Cannot initialise AI client: {env_var} is missing. "
            f"Add it to your .env file."
        ) from original
    return value


try:
    key = load_api_key("NONEXISTENT_KEY")
except ConfigError as e:
    print(f"\nConfigError: {e}")
    print(f"Caused by: {e.__cause__}")


# ─── CUSTOM EXCEPTION CLASSES ─────────────────────────────────────────────────

# For AI applications, define a hierarchy of custom exceptions.
# This lets callers catch at the right level of specificity.

class AIAppError(Exception):
    """Base exception for all AI application errors."""
    pass


class APIError(AIAppError):
    """Raised when an LLM API call fails."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

    def is_retryable(self) -> bool:
        """Rate limits (429) and server errors (5xx) are worth retrying."""
        return self.status_code in (429, 500, 502, 503, 504)


class RateLimitError(APIError):
    """Raised specifically when the API rate limit is hit."""
    def __init__(self, retry_after: float | None = None):
        super().__init__("API rate limit exceeded", status_code=429)
        self.retry_after = retry_after


class TokenLimitError(APIError):
    """Raised when the context window is exceeded."""
    pass


class ParseError(AIAppError):
    """Raised when the LLM response cannot be parsed into expected format."""
    def __init__(self, message: str, raw_response: str = ""):
        super().__init__(message)
        self.raw_response = raw_response


# Demo: using the custom hierarchy
def simulate_api_call(fail_with: str | None = None) -> dict:
    """Simulates an AI API call that can fail in various ways."""
    if fail_with == "rate_limit":
        raise RateLimitError(retry_after=30.0)
    if fail_with == "token_limit":
        raise TokenLimitError("Context window exceeded", status_code=400)
    if fail_with == "parse":
        raise ParseError("Expected JSON, got prose", raw_response="Sure! Here is some text...")
    return {"content": "Hello, I'm an AI!"}


scenarios = [None, "rate_limit", "token_limit", "parse"]
print("\nCustom exception hierarchy demo:")
for scenario in scenarios:
    try:
        result = simulate_api_call(fail_with=scenario)
        print(f"  Success: {result['content']}")
    except RateLimitError as e:
        print(f"  RateLimit (retry after {e.retry_after}s): {e}")
    except TokenLimitError as e:
        print(f"  TokenLimit: {e}")
    except ParseError as e:
        print(f"  ParseError: {e}. Raw: {e.raw_response!r}")
    except AIAppError as e:
        print(f"  Generic AIAppError: {e}")


# ─── EXCEPTION HIERARCHY ─────────────────────────────────────────────────────

# BaseException
#   ├── SystemExit              ← raised by sys.exit()
#   ├── KeyboardInterrupt       ← Ctrl+C
#   ├── GeneratorExit           ← generator cleanup
#   └── Exception               ← catch THIS for user-defined errors
#       ├── ArithmeticError
#       │   └── ZeroDivisionError
#       ├── AttributeError
#       ├── ImportError
#       │   └── ModuleNotFoundError
#       ├── LookupError
#       │   ├── IndexError
#       │   └── KeyError
#       ├── OSError
#       │   └── FileNotFoundError
#       ├── TypeError
#       ├── ValueError
#       │   └── UnicodeDecodeError
#       └── RuntimeError
#           └── RecursionError
#
# NEVER use bare `except:` — it catches KeyboardInterrupt and SystemExit too!
# Use `except Exception:` if you need a catch-all.


# ─── CONTEXT MANAGERS AND EXCEPTIONS ─────────────────────────────────────────

# If an exception is raised inside a `with` block, __exit__ is still called.
# This is why `with open(...)` is safe — the file is always closed.

from pathlib import Path
import json

def safe_read_json(path: Path) -> dict:
    """Read a JSON file with proper exception handling."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        raise ParseError(
            f"Invalid JSON in {path}: {e.msg} at line {e.lineno}",
            raw_response=e.doc or "",
        ) from e
    except PermissionError:
        raise OSError(f"No read permission for: {path}")


import tempfile, os
# Test it
tmp = Path(tempfile.gettempdir())
good_json = tmp / "good.json"
bad_json = tmp / "bad.json"

good_json.write_text('{"key": "value"}')
bad_json.write_text('{ invalid json !!!')

print("\nJSON reading:")
try:
    data = safe_read_json(good_json)
    print(f"  Good file: {data}")
except Exception as e:
    print(f"  Error: {e}")

try:
    data = safe_read_json(bad_json)
except ParseError as e:
    print(f"  Bad JSON: {e}")

try:
    data = safe_read_json(Path("/tmp/nonexistent.json"))
except FileNotFoundError as e:
    print(f"  Missing file: {e}")


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 — RESILIENT API CALLER
#   Write a function `resilient_call(func, max_retries=3, backoff=1.0)` that:
#     - Calls func()
#     - On RateLimitError: waits backoff seconds, doubles backoff, retries
#     - On other APIError: raises immediately (not worth retrying)
#     - Returns the result if successful
#   Test it with a simulate_api_call that fails twice with RateLimitError
#   then succeeds.

# Exercise 2 — VALIDATE AND PARSE JSON RESPONSE
#   LLMs sometimes return malformed JSON. Write a function
#   `parse_llm_json(raw: str) -> dict` that:
#     1. Tries json.loads(raw).
#     2. If that fails, tries to strip markdown code fences (```json ... ```)
#        and parse again.
#     3. If that also fails, raises ParseError with the raw response attached.
#   Test with: valid JSON, JSON wrapped in markdown, and pure prose.

# Exercise 3 — EXCEPTION HIERARCHY
#   Design a custom exception hierarchy for a hypothetical product search API:
#     AppError (base)
#       ├── ProductNotFoundError (id: int)
#       ├── SearchError (query: str)
#       │     └── EmptyQueryError
#       └── DatabaseError (table: str)
#   Write functions that raise each type, then catch them at different levels
#   to demonstrate how hierarchy allows "catching at the right level".
