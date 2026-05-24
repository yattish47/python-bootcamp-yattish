# Exercise 3 — Kotlin to Python Translation
# Week 1 | Python for AI Engineers
#
# Translate the Kotlin code below into equivalent Python.
# This tests your understanding of syntax mapping.
#
# ─── KOTLIN CODE ─────────────────────────────────────────────────────────────
#
#   data class Student(val name: String, val grade: Int)
#
#   fun getTopStudents(students: List<Student>, minGrade: Int = 80): List<String> {
#       return students
#           .filter { it.grade >= minGrade }
#           .sortedByDescending { it.grade }
#           .map { "${it.name} (${it.grade})" }
#   }
#
#   val students = listOf(
#       Student("Ali", 92),
#       Student("Bob", 75),
#       Student("Charlie", 88),
#       Student("Diana", 95),
#       Student("Eve", 61)
#   )
#
#   println(getTopStudents(students))
#   println(getTopStudents(students, minGrade = 90))
#
# ─── EXPECTED OUTPUT ─────────────────────────────────────────────────────────
#
#   ['Diana (95)', 'Ali (92)', 'Charlie (88)']
#   ['Diana (95)', 'Ali (92)']
#
# ─────────────────────────────────────────────────────────────────────────────

# Hints:
# - Use a dataclass or just a dict for Student
# - sorted() with key= and reverse=True replaces sortedByDescending
# - List comprehension replaces .filter().map()

# YOUR PYTHON CODE HERE


# ─── SOLUTION (remove before sharing) ────────────────────────────────────────
# from dataclasses import dataclass
#
# @dataclass
# class Student:
#     name: str
#     grade: int
#
# def get_top_students(students: list[Student], min_grade: int = 80) -> list[str]:
#     filtered = [s for s in students if s.grade >= min_grade]
#     sorted_students = sorted(filtered, key=lambda s: s.grade, reverse=True)
#     return [f"{s.name} ({s.grade})" for s in sorted_students]
#
# students = [
#     Student("Ali", 92),
#     Student("Bob", 75),
#     Student("Charlie", 88),
#     Student("Diana", 95),
#     Student("Eve", 61),
# ]
#
# print(get_top_students(students))
# print(get_top_students(students, min_grade=90))
