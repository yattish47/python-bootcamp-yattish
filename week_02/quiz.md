# Week 2 Quiz — OOP + First LLM Call
## Python for AI Engineers

**Instructions:** Answer all 8 questions before looking at the answers.

---

### Q1. What is the output?

```python
class Counter:
    count = 0

    def __init__(self):
        Counter.count += 1

c1 = Counter()
c2 = Counter()
c3 = Counter()
print(Counter.count)
```

a) `0`
b) `1`
c) `3`
d) Each instance has its own count, so `1`

---

### Q2. What does `@property` allow you to do?

a) Mark a method as private
b) Access a method like an attribute (without calling it with `()`)
c) Cache the result of a function
d) Make a class variable

---

### Q3. What is the output?

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1 == p2)
print(p1 is p2)
```

a) `True` then `True`
b) `True` then `False`
c) `False` then `False`
d) `False` then `True`

---

### Q4. Which of these correctly calls the OpenAI API?

```python
# Option A
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)

# Option B
response = client.complete(prompt="Hello", model="gpt-4o-mini")

# Option C
response = client.chat("Hello")
```

a) Option A
b) Option B
c) Option C
d) All three work

---

### Q5. In a chat completion, what is the "system" role used for?

a) Sending error messages to the model
b) Setting the AI's behavior, persona, and constraints
c) Passing function/tool results back
d) The API uses it internally — you should never set it

---

### Q6. What does `super().__init__(...)` do in a subclass?

a) Calls a method from a sibling class
b) Calls the parent class's `__init__` method
c) Creates a new instance of the parent class
d) Overrides the parent's constructor entirely

---

### Q7. You have this Pydantic model. What happens when you run the last line?

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float

p = Product(name="Widget", price="not-a-number")
```

a) `price` is set to `"not-a-number"` (Pydantic is flexible)
b) `price` is set to `0.0` (Pydantic uses a default)
c) A `ValidationError` is raised immediately
d) It works because Python is dynamically typed

---

### Q8. How do you maintain conversation context across multiple messages with the OpenAI API?

a) The API automatically remembers previous messages by session ID
b) You pass the full conversation history (all previous messages) in the `messages` list each time
c) You use the `memory=True` parameter
d) You store context in the model parameter field

---

## Answers

<details>
<summary>Click to reveal — only after answering all 8</summary>

| Q | Answer | Explanation |
|---|--------|-------------|
| 1 | **c** | `count` is a class variable. All instances share it. Each `__init__` increments the shared `Counter.count`. Result: 3. |
| 2 | **b** | `@property` lets you call `obj.method_name` without `()`, treating it like an attribute. |
| 3 | **b** | `@dataclass` auto-generates `__eq__` that compares field values → `True`. But they are two different objects in memory → `is` is `False`. |
| 4 | **a** | The correct OpenAI Python SDK v1 call. Option B and C are not real SDK methods. |
| 5 | **b** | The system message sets the model's persona, behavior, and constraints. It's the first message in the list and the model treats it as instructions. |
| 6 | **b** | `super().__init__(...)` calls the parent class's constructor so the parent's `__init__` logic runs. Without it, parent attributes aren't initialized. |
| 7 | **c** | Pydantic validates types at runtime. `"not-a-number"` can't be coerced to `float`, so it raises `ValidationError` immediately. |
| 8 | **b** | OpenAI's API is stateless. You must send the entire conversation history in the `messages` list with every request. The API does NOT store state between calls. |

**Score guide:**
- 8/8 — Ready for Week 3.
- 6–7/8 — Review the missed topic, then move on.
- <6/8 — Re-read lessons 2.1–2.4 before continuing.

</details>
