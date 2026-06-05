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

# dataclass method
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    grade: int

def getTopStudents(students: list[Student], min_grade: int = 80)-> list[str]:
    filtered_students = [student for student in students if student.grade >= min_grade]
    sorted_students = sorted(filtered_students, key=lambda s:s.grade, reverse=True)
    return [f"{s.name} ({s.grade})" for s in sorted_students]
        

students = [Student("Ali", 92), Student("Bob", 75), Student("Charlie", 88), Student("Diana", 95), Student("Eve", 61)]

print(getTopStudents(students))
print(getTopStudents(students, min_grade = 90))

# dict method
students2 = {"Ali": 92, "Bob": 75, "Charlie": 88, "Diana": 95, "Eve": 61}

def getTopStudents2(students2: dict[str, int], min_grade: int = 80)-> list[str]:
    filtered_students = {k : v for k,v in students2.items() if v >= min_grade}
    sorted_students = sorted(filtered_students.items(), key=lambda s:s[1], reverse=True)
    return [f"{s[0]} ({s[1]})" for s in sorted_students]


print(getTopStudents2(students2))
print(getTopStudents2(students2, min_grade = 90))


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
