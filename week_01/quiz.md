# Week 1 Quiz — Python Foundations
## Python for AI Engineers

**Instructions:** Answer all 10 questions before looking at the answers.
Write your answers on paper or in a separate file — not below.

---

### Q1. What is the output of this code?

```python
x = 5
x = "hello"
print(type(x))
```

a) `<class 'int'>`
b) `<class 'str'>`
c) TypeError — can't reassign different types
d) `<class 'object'>`

b ✅
---

### Q2. What does this print?

```python
nums = [1, 2, 3, 4, 5]
print(nums[-2])
```

a) `4`
b) `5`
c) `2`
d) IndexError

d ❌ — correct answer is a. Negative indexing is valid: nums[-1]=5, nums[-2]=4.

---

### Q3. What is the output?

```python
result = [x ** 2 for x in range(5) if x % 2 != 0]
print(result)
```

a) `[1, 4, 9, 16, 25]`
b) `[1, 9]`
c) `[0, 1, 4, 9, 16]`
d) `[1, 9, 25]`

b ✅
---

### Q4. Which of these correctly checks if a variable is None?

a) `if x == None:`
b) `if x is None:`
c) `if not x:`
d) `if x === None:`

b ✅
---

### Q5. What does this function return when called as `greet()`?

```python
def greet(name: str = "World", greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"
```

a) `"Hello, !"`
b) `"Hello, World!"`
c) TypeError — missing required argument
d) `None`

b ✅
---

### Q6. What is the output?

```python
a = {"x": 1, "y": 2}
b = {"y": 99, "z": 3}
merged = a | b
print(merged["y"])
```

a) `2`
b) `99`
c) `KeyError`
d) `[2, 99]`

b ✅
---

### Q7. What does `*args` capture in this call?

```python
def show(*args):
    print(args)

show(1, 2, 3)
```

a) `[1, 2, 3]`
b) `(1, 2, 3)`
c) `{1, 2, 3}`
d) `{"args": [1, 2, 3]}`

a ❌ — correct answer is b. *args always captures a tuple (1, 2, 3), not a list.
---

### Q8. What is the output?

```python
words = ["cat", "elephant", "ox", "bee"]
shortest = min(words, key=len)
print(shortest)
```

a) `"cat"`
b) `"ox"`
c) `"bee"`
d) `"elephant"`

b ✅
---

### Q9. Which line produces the set `{1, 2, 3}`?

a) `s = set([1, 2, 3, 2, 1])`
b) `s = {1, 2, 3, 2, 1}`
c) Both a and b
d) Neither — sets must be initialized empty

b ❌ — correct answer is c. Both set([...]) and {...} deduplicate, so both produce {1, 2, 3}.
---

### Q10. What does this print?

```python
pairs = [(1, "a"), (2, "b"), (3, "c")]
for num, letter in pairs:
    print(f"{letter}{num}", end="")
```

a) `a1b2c3`
b) `1a2b3c`
c) `(1, a)(2, b)(3, c)`
d) TypeError

a ✅
---

## Answers

<details>
<summary>Click to reveal — only after you've answered all 10</summary>

| Q | Answer | Explanation |
|---|--------|-------------|
| 1 | **b** | Python allows reassigning to a different type. `x` is now a `str`. |
| 2 | **a** | Negative indexing: `nums[-1]` = 5, `nums[-2]` = 4. |
| 3 | **d** | `range(5)` = 0–4. Odd numbers are 1, 3. Their squares: 1, 9. Wait — 5 is not in range(5). Odd: 1, 3. Squares: 1, 9. But `range(5)` includes 0,1,2,3,4 → odd: 1,3 → squares 1,9. **Answer is b) [1, 9]**. |
| 4 | **b** | `is None` is the correct Python idiom. `== None` works but is discouraged. `not x` would also catch `0`, `""`, `[]`. |
| 5 | **b** | Both params have defaults. `greet()` → `"Hello, World!"` |
| 6 | **b** | `b` overrides `a` on shared keys. `merged["y"]` = 99. |
| 7 | **b** | `*args` is always a **tuple**, not a list. |
| 8 | **b** | `min(key=len)`: "ox" has length 2, the shortest. |
| 9 | **c** | Both `set([...])` and `{...}` deduplicate. Result is `{1, 2, 3}`. |
| 10 | **a** | Tuple unpacking in the for loop. `f"{letter}{num}"` → "a1", "b2", "c3". Combined: `a1b2c3`. |

**Correction for Q3:** The answer is **b) [1, 9]** not d. `range(5)` = [0,1,2,3,4], odd values are 1 and 3, squares are 1 and 9.

**Score guide:**
- 10/10 — Ready for Week 2. 
- 8–9/10 — Review the missed concepts, then move on.
- 6–7/10 — Re-read the lessons for your missed questions before Week 2.
- <6/10 — Work through all 4 lessons again and redo the exercises.

</details>
