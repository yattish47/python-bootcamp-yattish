# Week 2 — OOP + Your First LLM Call

This week you'll learn Python's object system, then make your first real call to an AI model.
By the end you'll have a working CLI chatbot powered by the OpenAI API.

---

## Setup

```bash
cd python_learning/week_02
python -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv
```

Create a `.env` file in `week_02/`:
```
OPENAI_API_KEY=sk-...your-key-here...
```

Get your key at: https://platform.openai.com/api-keys

---

## Lessons

| # | File | Topics |
|---|------|--------|
| 2.1 | `lesson_2_1_classes.py` | class, `__init__`, methods, inheritance, `@property` |
| 2.2 | `lesson_2_2_dataclasses.py` | dataclasses, Pydantic models |
| 2.3 | `lesson_2_3_modules.py` | imports, packages, `__init__.py` |
| 2.4 | `lesson_2_4_openai_intro.py` | OpenAI SDK, chat completions, prompt basics |

**Mini-project:** `project/simple_chatbot.py` — your first AI chatbot

---

## Kotlin → Python OOP Mapping

| Concept | Kotlin | Python |
|---------|--------|--------|
| Class | `class Dog(val name: String)` | `class Dog: def __init__(self, name: str)` |
| Data class | `data class Dog(val name: String)` | `@dataclass class Dog: name: str` |
| Constructor | `Dog("Rex")` | `Dog("Rex")` |
| Method | `fun bark() = println("Woof")` | `def bark(self): print("Woof")` |
| Property getter | `val upper get() = name.uppercase()` | `@property def upper(self): return self.name.upper()` |
| Inheritance | `class Poodle : Dog(name)` | `class Poodle(Dog):` |
| Override | `override fun bark()` | `def bark(self):` (no keyword needed) |
| Companion obj | `companion object { fun create() }` | `@classmethod def create(cls)` |
| `toString()` | `override fun toString()` | `def __repr__(self)` / `def __str__(self)` |

## PHP → Python OOP Mapping

| Concept | PHP | Python |
|---------|-----|--------|
| Class | `class Dog { public string $name; }` | `class Dog: def __init__(self, name: str)` |
| Constructor | `public function __construct()` | `def __init__(self)` |
| `$this` | `$this->name` | `self.name` |
| Inheritance | `class Poodle extends Dog` | `class Poodle(Dog):` |
| Static method | `public static function create()` | `@staticmethod def create()` |
| `__toString` | `public function __toString()` | `def __str__(self)` |
