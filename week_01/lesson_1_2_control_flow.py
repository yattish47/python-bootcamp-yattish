# Lesson 1.2 — Control Flow
# Python for AI Engineers | Week 1
#
# CONCEPT:
#   Python uses indentation (4 spaces) instead of curly braces to define blocks.
#   No semicolons. No parentheses required around if/while conditions.
#   This trips up Kotlin and PHP developers at first — watch your indentation.
#
# KOTLIN:  if (x > 0) { ... }
# PHP:     if ($x > 0) { ... }
# PYTHON:  if x > 0:
#              ...

# ─── IF / ELIF / ELSE ────────────────────────────────────────────────────────

score = 75

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Grade: {grade}")   # Grade: C

# Inline ternary (like Kotlin's if expression)
# Kotlin:  val label = if (score >= 60) "Pass" else "Fail"
# PHP:     $label = $score >= 60 ? "Pass" : "Fail";
label = "Pass" if score >= 60 else "Fail"
print(label)               # Pass

# ─── COMPARISON & LOGICAL OPERATORS ─────────────────────────────────────────

# Python uses words, not symbols, for logic
# Kotlin: &&  ||  !      PHP: &&  ||  !
# Python: and  or  not

x, y = 5, 10

print(x > 3 and y < 20)   # True
print(x > 10 or y < 20)   # True
print(not x > 10)          # True

# Chained comparisons (Python-only)
age = 25
print(18 <= age <= 65)     # True — reads like math, no equivalent in Kotlin/PHP

# ─── FOR LOOPS ───────────────────────────────────────────────────────────────

# range(stop)         → 0, 1, ..., stop-1
# range(start, stop)  → start, ..., stop-1
# range(start, stop, step)

for i in range(5):
    print(i, end=" ")      # 0 1 2 3 4
print()

for i in range(2, 10, 2):
    print(i, end=" ")      # 2 4 6 8
print()

# Iterate over a list
languages = ["Python", "Kotlin", "PHP"]
for lang in languages:
    print(f"- {lang}")

# enumerate() gives index + value (like Kotlin's forEachIndexed)
for index, lang in enumerate(languages):
    print(f"{index}: {lang}")

# ─── WHILE LOOPS ─────────────────────────────────────────────────────────────

count = 0
while count < 3:
    print(f"count = {count}")
    count += 1             # no ++ operator in Python

# break and continue work the same as Kotlin/PHP
for i in range(10):
    if i == 3:
        continue           # skip 3
    if i == 6:
        break              # stop at 6
    print(i, end=" ")      # 0 1 2 4 5
print()

# ─── MATCH STATEMENT (Python 3.10+) ──────────────────────────────────────────

# Like Kotlin's `when` or PHP 8's `match`
status_code = 404

match status_code:
    case 200:
        msg = "OK"
    case 404:
        msg = "Not Found"
    case 500:
        msg = "Server Error"
    case _:                # default
        msg = "Unknown"

print(msg)                 # Not Found

# ─── TRUTHINESS ──────────────────────────────────────────────────────────────

# Python's "falsy" values: None, 0, 0.0, "", [], {}, set()
# Everything else is truthy

items = []
if not items:              # idiomatic — no need to write `len(items) == 0`
    print("List is empty")

user = None
if user:
    print("User exists")
else:
    print("No user")       # prints this


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Write a loop that prints the numbers 1–20.
#   For multiples of 3 print "Fizz", multiples of 5 print "Buzz",
#   multiples of both print "FizzBuzz", otherwise print the number.

# Exercise 2:
#   Given a list of temperatures in Celsius:
#   temps = [22, 35, 18, 40, 29, 15]
#   Print only temperatures above 30, prefixed with "HOT: ".

# Exercise 3:
#   Use a match statement that takes an HTTP method string ("GET", "POST",
#   "PUT", "DELETE") and prints what operation it represents.
#   Handle an unknown method with a default case.
