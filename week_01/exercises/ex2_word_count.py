# Exercise 2 — Word Count
# Week 1 | Python for AI Engineers
#
# Given a string of text, count how many times each word appears.
# Print results sorted by frequency (highest first).
# Ignore punctuation and case (treat "Hello" and "hello" as the same word).
#
# Expected output for the sample text below:
# the: 4
# a: 3
# quick: 2
# ...

import string

text = """
The quick brown fox jumps over the lazy dog.
The dog barked at the fox. A fox is a quick animal.
A dog is a loyal animal.
"""

# Hints:
# 1. text.lower() — lowercase everything
# 2. text.translate(str.maketrans("", "", string.punctuation)) — strip punctuation
# 3. text.split() — split into words
# 4. Use a dict to count, or look up collections.Counter
# 5. sorted(d.items(), key=lambda x: x[1], reverse=True) — sort by value

# YOUR CODE HERE


# ─── SOLUTION (remove before sharing) ────────────────────────────────────────
# from collections import Counter
#
# cleaned = text.lower().translate(str.maketrans("", "", string.punctuation))
# words = cleaned.split()
# counts = Counter(words)
# for word, count in counts.most_common():
#     print(f"{word}: {count}")
