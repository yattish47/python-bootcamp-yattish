# Week 4 Quiz — Files, Errors, Tool Use

Test your understanding of file I/O, environment configuration, exception handling, and OpenAI function calling.

---

**Question 1**
What is the difference between `json.dump()` and `json.dumps()`? When would you use each?

<details>
<summary>Answer</summary>

- `json.dump(obj, file)` — writes JSON directly to a file object. Use when saving to disk.
- `json.dumps(obj)` — returns a JSON **string** (`s` = string). Use when you need the JSON as a Python string (e.g., to print it, send it over HTTP, or store it in a variable).

```python
# dump — to file
with open("data.json", "w") as f:
    json.dump({"key": "value"}, f, indent=2)

# dumps — to string
json_str = json.dumps({"key": "value"}, indent=2)
print(json_str)
```

Similarly, `json.load(file)` reads from a file object and `json.loads(string)` parses a string.

</details>

---

**Question 2**
Why should you always use `with open(...)` instead of `f = open(...); ...; f.close()`?

<details>
<summary>Answer</summary>

`with open(...)` is a context manager that guarantees `f.close()` is called even if an exception is raised inside the block. With the manual pattern:

```python
f = open("data.txt")
process(f)        # if this raises, f.close() is never called
f.close()         # this line is skipped on exception → file handle leak
```

With `with`:
```python
with open("data.txt") as f:
    process(f)    # even if this raises, f.__exit__ calls f.close()
```

On most operating systems, unclosed file handles are eventually cleaned up by the garbage collector, but in long-running processes (like AI agents) they accumulate and can exhaust the OS file descriptor limit.

</details>

---

**Question 3**
What does `load_dotenv()` actually do, and what happens if an environment variable is already set before `load_dotenv()` is called?

<details>
<summary>Answer</summary>

`load_dotenv()` reads a `.env` file and calls `os.environ.setdefault(key, value)` for each line (when `override=False`, which is the default). `setdefault` only sets the variable if it's **not already present**.

This is intentional: in CI/CD pipelines, real environment variables (injected by the platform) take precedence over `.env` files. This means:
- On a developer's machine: `.env` provides the values.
- On GitHub Actions / AWS: the platform-injected secrets win automatically.

Use `override=True` only if you explicitly want the `.env` file to overwrite existing variables.

</details>

---

**Question 4**
What is wrong with this exception handling code?

```python
try:
    result = call_api()
except:
    print("Something went wrong")
```

How would you fix it?

<details>
<summary>Answer</summary>

Two problems:

1. **Bare `except:`** catches *everything*, including `KeyboardInterrupt` (Ctrl+C), `SystemExit` (sys.exit()), and `GeneratorExit`. This means the user can never interrupt the program, and `sys.exit()` won't work.

2. **Silent swallowing** — the error is printed but not re-raised or logged properly, making debugging very difficult.

Fixed version:
```python
try:
    result = call_api()
except RateLimitError as e:
    print(f"Rate limit hit, retry after {e.retry_after}s")
    time.sleep(e.retry_after)
    result = call_api()       # retry once
except APIError as e:
    logger.error("API call failed", exc_info=True)
    raise                     # re-raise so the caller knows
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

Always catch the **most specific** exception first, and `Exception` last if needed.

</details>

---

**Question 5**
Explain the `raise X from Y` syntax. When would you use it?

<details>
<summary>Answer</summary>

`raise NewException(...) from original_exception` chains two exceptions together, preserving the original as the `__cause__` of the new one. The traceback shows both, making it clear what triggered the higher-level error.

Use it when you **catch a low-level exception and raise a higher-level one** with more context:

```python
def load_config(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {path}") from e
```

Without `from e`, the original traceback is lost (or shown as "During handling of the above exception…" in a confusing way). With `from e`, the traceback clearly shows:
```
json.JSONDecodeError: ...
The above exception was the direct cause of:
ConfigError: Invalid JSON in config.json
```

Use `raise X from None` to explicitly suppress the original exception when it would be confusing or expose internal details.

</details>

---

**Question 6**
Describe the complete tool use (function calling) flow step by step. What role does the LLM actually play, and what does your code do?

<details>
<summary>Answer</summary>

Complete flow:

1. **Define tools** — you write JSON schemas describing function names, descriptions, and parameter types.

2. **Send request** — you call the OpenAI API with `messages` + `tools`. The LLM reads the descriptions to understand what each tool does.

3. **Model decides** — if the LLM determines it needs real data, it returns a response with `finish_reason="tool_calls"` and a `tool_calls` list. Each item has: `id`, `function.name`, `function.arguments` (JSON string).

4. **Your code executes** — you parse the arguments, call the actual Python function, get the result. The LLM **never runs any code itself**.

5. **Append results** — you append the original assistant message (with tool_calls) to the conversation, then append a `{"role": "tool", "tool_call_id": ..., "content": result_json}` message for each call.

6. **Call API again** — you send the updated conversation back to the API. The model now has the tool results and generates the final human-readable response.

7. **Repeat if needed** — in some cases the model may request more tool calls (e.g., needing product ID before searching). Loop until `finish_reason="stop"`.

The LLM's role is **decision-making and natural language** — it decides *which* function to call with *what arguments*, then uses the result to compose a helpful answer. Your code does the actual data access.

</details>

---

**Question 7**
What is `pathlib.Path` and why is it preferred over using `os.path` string manipulation?

<details>
<summary>Answer</summary>

`pathlib.Path` is an object-oriented representation of filesystem paths introduced in Python 3.4. It's preferred because:

1. **Readable path joining** — `Path("home") / "docs" / "file.txt"` vs `os.path.join("home", "docs", "file.txt")`

2. **Built-in file operations** — `path.read_text()`, `path.write_text()`, `path.exists()`, `path.mkdir()` — no need to import multiple modules

3. **Cross-platform** — handles `/` vs `\` automatically; `Path("a/b")` works on both Windows and Unix

4. **Rich API** — `path.stem`, `path.suffix`, `path.parent`, `path.glob("*.py")`, `path.rglob("**/*.json")`

5. **Type safety** — Path objects can't be accidentally concatenated with plain strings, making bugs more obvious

```python
# Old way
import os
config_path = os.path.join(os.path.dirname(__file__), "config", "settings.json")
with open(config_path) as f:
    data = json.load(f)

# New way
config_path = Path(__file__).parent / "config" / "settings.json"
data = json.loads(config_path.read_text())
```

</details>
