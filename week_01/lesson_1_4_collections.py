# Lesson 1.4 — Collections
# Python for AI Engineers | Week 1
#
# CONCEPT:
#   Python has 4 built-in collection types:
#   - list   → ordered, mutable sequence       (like Kotlin List / PHP array)
#   - dict   → key-value pairs                 (like Kotlin Map / PHP assoc array)
#   - set    → unordered, unique values        (like Kotlin Set)
#   - tuple  → ordered, IMMUTABLE sequence     (like Kotlin Pair/Triple or data class)
#
#   List comprehensions and dict comprehensions are Python's superpower —
#   they replace most for-loop data transformations in a single readable line.

from typing import Any

# ─── LIST ────────────────────────────────────────────────────────────────────

fruits = ["apple", "banana", "cherry"]
fruits.append("date")         # add to end
fruits.insert(0, "avocado")  # insert at index
fruits.remove("banana")      # remove by value
popped = fruits.pop()        # remove & return last item

print(fruits)
print(f"Length: {len(fruits)}")

# Indexing and slicing
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(nums[0])       # 0    — first
print(nums[-1])      # 9    — last
print(nums[2:5])     # [2, 3, 4]   — slice [start:stop]
print(nums[::2])     # [0, 2, 4, 6, 8]  — every 2nd element
print(nums[::-1])    # [9, 8, ... 0]    — reversed

# Check membership
print("apple" in fruits)   # True

# Sorting
scores = [3, 1, 4, 1, 5, 9, 2, 6]
print(sorted(scores))              # returns new sorted list
scores.sort(reverse=True)          # sorts in-place
print(scores)

# ─── DICT ────────────────────────────────────────────────────────────────────

# PHP: $user = ["name" => "Ali", "age" => 30];
# Kotlin: mapOf("name" to "Ali", "age" to 30)

user: dict[str, Any] = {
    "name": "Ali",
    "age": 30,
    "skills": ["Python", "Kotlin"]
}

print(user["name"])                  # Ali
print(user.get("email", "N/A"))     # N/A — safe get with default

user["email"] = "ali@example.com"   # add/update key
del user["age"]                     # delete key

# Iterate
for key, value in user.items():
    print(f"  {key}: {value}")

# Check key existence
if "email" in user:
    print("Email found")

# Merge two dicts (Python 3.9+)
defaults = {"theme": "dark", "lang": "en"}
settings = {"lang": "ms", "notifications": True}
merged = defaults | settings          # settings overrides defaults
print(merged)

# ─── SET ─────────────────────────────────────────────────────────────────────

# Unordered, no duplicates — useful for deduplication and membership tests
tags = {"python", "ai", "backend", "python"}   # duplicate removed
print(tags)

tags.add("fastapi")
tags.discard("backend")    # remove if present, no error if missing

a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print(a & b)               # {3, 4}  — intersection
print(a | b)               # {1, 2, 3, 4, 5, 6}  — union
print(a - b)               # {1, 2}  — difference

# ─── TUPLE ───────────────────────────────────────────────────────────────────

# Immutable — use for data that should not change
point = (3, 7)
rgb = (255, 128, 0)

x, y = point               # unpacking
r, g, b = rgb

print(f"x={x}, y={y}")
print(f"RGB: {r}, {g}, {b}")

# Tuples as dict keys (since they're hashable)
locations = {(0, 0): "origin", (1, 0): "east"}
print(locations[(0, 0)])   # origin

# ─── LIST COMPREHENSIONS ─────────────────────────────────────────────────────

# Pattern: [expression for item in iterable if condition]
# This is Python's most distinctive feature. Learn to read and write it fluently.

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Map: double each number
doubled = [n * 2 for n in numbers]
print(doubled)             # [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

# Filter: keep only even numbers
evens = [n for n in numbers if n % 2 == 0]
print(evens)               # [2, 4, 6, 8, 10]

# Map + Filter: square of even numbers
even_squares = [n ** 2 for n in numbers if n % 2 == 0]
print(even_squares)        # [4, 16, 36, 64, 100]

# Strings
words = ["hello", "world", "python"]
upper_words = [w.upper() for w in words]
print(upper_words)         # ['HELLO', 'WORLD', 'PYTHON']

# ─── DICT COMPREHENSIONS ─────────────────────────────────────────────────────

# Pattern: {key_expr: value_expr for item in iterable}

names = ["Ali", "Bob", "Charlie"]
name_lengths = {name: len(name) for name in names}
print(name_lengths)        # {'Ali': 3, 'Bob': 3, 'Charlie': 7}

# Invert a dict
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
print(inverted)            # {1: 'a', 2: 'b', 3: 'c'}

# ─── USEFUL BUILT-IN FUNCTIONS ───────────────────────────────────────────────

prices = [10.5, 3.2, 7.8, 15.0, 2.1]
print(f"sum={sum(prices):.2f}")
print(f"min={min(prices)}, max={max(prices)}")
print(f"avg={sum(prices)/len(prices):.2f}")

# zip — pair up two lists (like Kotlin's zip)
names = ["Ali", "Bob", "Charlie"]
scores = [88, 95, 72]
paired = list(zip(names, scores))
print(paired)              # [('Ali', 88), ('Bob', 95), ('Charlie', 72)]

# zip into a dict
score_dict = dict(zip(names, scores))
print(score_dict)          # {'Ali': 88, 'Bob': 95, 'Charlie': 72}


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Given: products = [{"name": "Laptop", "price": 1200}, {"name": "Mouse", "price": 25},
#                      {"name": "Monitor", "price": 350}, {"name": "Keyboard", "price": 80}]
#   Using a list comprehension, extract only the names of products under $100.
products = [{"name": "Laptop", "price": 1200}, {"name": "Mouse", "price": 25}, {"name": "Monitor", "price": 350}, {"name": "Keyboard", "price": 80}]

product_name = [product["name"] for product in products if product["price"] < 100]
print(product_name)


# Exercise 2:
#   Given a list of words, use a dict comprehension to build a frequency map:
#   words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
#   Expected: {"apple": 3, "banana": 2, "cherry": 1}
#   Hint: use words.count(word)

words = ["apple", "banana", "apple", "cherry", "banana", "apple"]

words_count = {word : words.count(word) for word in words }
print(words_count)

# No, it does iterate each time — words.count(word) scans the entire list every time it's called. So for "apple" appearing 3 times, it scans the full list 3 times.

#   The iterations look like this:
#   word = "apple"  → words.count("apple") scans whole list → 3
#   word = "banana" → words.count("banana") scans whole list → 2
#   word = "apple"  → words.count("apple") scans whole list → 3  (again, wasted)
#   word = "cherry" → words.count("cherry") scans whole list → 1
#   word = "banana" → words.count("banana") scans whole list → 2  (again, wasted)
#   word = "apple"  → words.count("apple") scans whole list → 3  (again, wasted)

#   It gives the right answer because dict keys are unique — duplicate keys just overwrite each other. So even though "apple" is processed 3 times, the dict only keeps one "apple":
#   3 entry.

#   It works, but it's inefficient. The cleaner way (which you'll see in real code) uses collections.Counter:
#   from collections import Counter
#   words_count = Counter(words)   # scans the list exactly once


# Exercise 3:
#   Write a function `unique_sorted(items: list) -> list` that removes duplicates
#   from a list and returns the result sorted. Use set() and sorted().
#   unique_sorted([3, 1, 4, 1, 5, 9, 2, 6, 5, 3]) → [1, 2, 3, 4, 5, 6, 9]

def unique_sorted(items: list)-> list:
    unique = set(items)
    sorted_item = sorted(unique)
    return sorted_item

print(unique_sorted([3, 1, 4, 1, 5, 9, 2, 6, 5, 3]))
