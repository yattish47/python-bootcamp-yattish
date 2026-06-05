# Exercise 1 — FizzBuzz
# Week 1 | Python for AI Engineers
#
# Print numbers 1 to 50.
# - Multiples of 3: print "Fizz"
# - Multiples of 5: print "Buzz"
# - Multiples of both 3 and 5: print "FizzBuzz"
# - Otherwise: print the number
#
# Expected output (first 15 lines):
# 1
# 2
# Fizz
# 4
# Buzz
# Fizz
# 7
# 8
# Fizz
# Buzz
# 11
# Fizz
# 13
# 14
# FizzBuzz
# ...

# YOUR CODE HERE


for i in range(1,51):
    if i % 3 == 0 and i % 5 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)












# ─── SOLUTION (remove before sharing) ────────────────────────────────────────
# for i in range(1, 51):
#     if i % 15 == 0:
#         print("FizzBuzz")
#     elif i % 3 == 0:
#         print("Fizz")
#     elif i % 5 == 0:
#         print("Buzz")
#     else:
#         print(i)
