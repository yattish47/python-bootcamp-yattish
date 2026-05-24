# Week 1 — Python Foundations for Programmers

Welcome to Week 1. Since you already know Kotlin and PHP, this week focuses on
*mapping* Python to what you already know — not teaching programming from scratch.

**No packages to install this week.** Pure Python only.

---

## Lessons

| # | File | Topics |
|---|------|--------|
| 1.1 | `lesson_1_1_types.py` | Variables, types, type hints, dynamic typing |
| 1.2 | `lesson_1_2_control_flow.py` | if/elif/else, for/while, range |
| 1.3 | `lesson_1_3_functions.py` | def, default args, *args/**kwargs, lambda |
| 1.4 | `lesson_1_4_collections.py` | list, dict, set, tuple, comprehensions |

Run each lesson file directly: `python lesson_1_1_types.py`

---

## Kotlin → Python Cheat Sheet

| Concept | Kotlin | Python |
|---------|--------|--------|
| Variable | `val x: Int = 5` | `x: int = 5` |
| Mutable var | `var x = 5` | `x = 5` (all vars are mutable) |
| String | `"hello"` | `"hello"` or `'hello'` |
| String template | `"Hello $name"` | `f"Hello {name}"` |
| Null | `null` / `String?` | `None` / `Optional[str]` |
| Print | `println("hi")` | `print("hi")` |
| If expression | `val x = if (a) 1 else 2` | `x = 1 if a else 2` |
| For loop | `for (i in 0..9)` | `for i in range(10):` |
| Lambda | `{ x -> x * 2 }` | `lambda x: x * 2` |
| List | `listOf(1, 2, 3)` | `[1, 2, 3]` |
| Map | `mapOf("a" to 1)` | `{"a": 1}` |
| Class | `class Foo(val x: Int)` | `class Foo: def __init__(self, x: int)` |
| Data class | `data class Foo(val x: Int)` | `@dataclass class Foo: x: int` |

## PHP → Python Cheat Sheet

| Concept | PHP | Python |
|---------|-----|--------|
| Variable | `$name = "Ali"` | `name = "Ali"` (no `$`) |
| String interpolation | `"Hello $name"` | `f"Hello {name}"` |
| Array (list) | `[1, 2, 3]` | `[1, 2, 3]` |
| Associative array | `["a" => 1]` | `{"a": 1}` |
| Function | `function foo($x) {}` | `def foo(x):` |
| Null | `null` | `None` |
| Type check | `is_string($x)` | `isinstance(x, str)` |
| Echo | `echo "hi";` | `print("hi")` |
| Import | `require 'file.php';` | `import module` |

---

## After the Lessons

Complete the exercises in `exercises/` then take the `quiz.md`.
Don't look at the answers until you've attempted every question.
