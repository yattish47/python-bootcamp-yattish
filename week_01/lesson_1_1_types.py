# Lesson 1.1 — Variables & Types
# Python for AI Engineers | Week 1
#
# CONCEPT:
#   Python is dynamically typed — you don't declare types, the interpreter infers them.
#   But you CAN add type hints (: int, : str) for clarity and IDE support.
#   Type hints are checked by tools like mypy/Pylance but NOT enforced at runtime.
#
# KOTLIN:  val name: String = "Ali"   (compile-time enforced)
# PHP:     $name = "Ali";             (no types by default)
# PYTHON:  name: str = "Ali"          (hint only, not enforced)

# ─── BASIC TYPES ─────────────────────────────────────────────────────────────

x: int = "helo"
y: int = 33
price: float = 9.99
name: str = "Ali"
is_active: bool = True
nothing: None = None     # PHP's null, Kotlin's null

print(type(x))           # <class 'int'>
print(type(name))        # <class 'str'>
print(type(nothing))     # <class 'NoneType'>

# ─── DYNAMIC TYPING ──────────────────────────────────────────────────────────

# Python lets you reassign to a different type (unlike Kotlin)
value = 10
value = "now I'm a string"   # valid in Python, would be a compile error in Kotlin
print(value)

# ─── STRINGS ─────────────────────────────────────────────────────────────────

first = "Python"
last = 'Engineer'          # single or double quotes — same thing

# f-strings (like Kotlin's string templates or PHP's interpolation)
greeting = f"Hello, {first} {last}!"
print(greeting)            # Hello, Python Engineer!

# Multi-line strings
paragraph = """
This is a
multi-line string.
"""

# Useful string methods
msg = "  hello world  "
print(msg.strip())         # "hello world"
print(msg.upper())         # "  HELLO WORLD  "
print(msg.replace("world", "Python"))

# ─── TYPE CONVERSION ─────────────────────────────────────────────────────────

# Like Kotlin's .toInt(), .toString()
num_str = "42"
num = int(num_str)         # str → int
back = str(num)            # int → str
ratio = float(num)         # int → float

print(num + 1)             # 43
print(f"Value is {back}")  # Value is 42

# ─── NONE (null) ─────────────────────────────────────────────────────────────

user = None

# Check for None with `is None` (not == None)
if user is None:
    print("No user found")

# Optional type hint
#   -> Optional[str]   # returns str OR None
#   -> str             # always returns a str (never None)

#   Why import it? Optional isn't a built-in keyword — it lives in Python's typing module (standard library, no install needed). You import it to use it as a type hint.
#   Note: In Python 3.10+ you can skip the import and write it more cleanly:
#   def find_user(user_id: int) -> str | None:   # modern style
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Ali"
    return None            # explicit None return

result = find_user(99)
print(result)              # None

# ─── CONSTANTS ───────────────────────────────────────────────────────────────

# Python has no `const` keyword. Convention: ALL_CAPS means "don't change this"
MAX_RETRIES = 3
API_VERSION = "v1"

# ─── MULTIPLE ASSIGNMENT ─────────────────────────────────────────────────────

a, b, c = 1, 2, 3          # tuple unpacking — like destructuring
print(a, b, c)             # 1 2 3

print(x,y)
x, y = y, x                # swap without a temp variable (Python idiom)
print(x,y)

# ─── PRINT WITH FORMATTING ───────────────────────────────────────────────────

score = 95.678
print(f"Score: {score:.2f}")   # Score: 95.68  (2 decimal places)
print(f"{'Name':<10} {'Score':>10} last")  # left/right align in f-strings

print(type(42)), print(type(3.14)), print(type(True))

# ─── EXERCISES ───────────────────────────────────────────────────────────────
# Try these before moving to lesson 1.2.

# Exercise 1:
#   Create variables for a user profile: name (str), age (int), balance (float),
#   is_admin (bool). Print them using an f-string in one line.
name : str = "Yattish"
age : int = 25
balance : float = 10.22
is_admin : bool = True

print(f"Hello I'm {name}, my age is {age}, and my bank balance is {balance}, and I am an {'admin' if is_admin else 'non-admin'}")

# Exercise 2:
#   Write a function `safe_divide(a: float, b: float) -> Optional[float]`
#   that returns None if b is 0, otherwise returns a / b.
#   Test it with safe_divide(10, 2) and safe_divide(10, 0).
def safe_divide(a: float, b: float) -> float | None:
    if b == 0:
        return None 
    else: 
        return a/b

print(safe_divide(10,2))
print(safe_divide(10,0))


# ⏺ Python uses : to mean "block starts here" — it replaces the { from Kotlin/PHP.

#   // Kotlin
#   if (x > 0) {
#       println("positive")
#   }
#   // PHP
#   if ($x > 0) {
#       echo "positive";
#   }
#   # Python
#   if x > 0:
#       print("positive")

#   The : + indentation replaces { + }. Python has no closing brace — the block ends when indentation goes back.

#   Same rule applies to else, elif, for, while, def, class — anything that starts a block ends with :.

# Exercise 3:
#   Given the string "  Python is awesome!  ", produce exactly:
#   "PYTHON IS AWESOME!" (stripped and uppercased)
python_string: str = "  Python is awesome!  "

print(python_string.strip())
print(python_string.upper())
print(python_string.strip().upper())



