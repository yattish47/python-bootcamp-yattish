# Lesson 2.3 — Modules & Project Structure
# Python for AI Engineers | Week 2
#
# CONCEPT:
#   In Python, every .py file is a module. A folder with an __init__.py is a package.
#   This is how you organize larger projects — similar to Kotlin packages or PHP namespaces.
#
# KOTLIN:  package com.example.utils  →  import com.example.utils.StringUtils
# PHP:     namespace App\Utils;        →  use App\Utils\StringUtils;
# PYTHON:  utils/strings.py            →  from utils.strings import StringUtils

# ─── IMPORTING ───────────────────────────────────────────────────────────────

# Standard library imports
import os
import sys
import json
import math
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

# Import specific names
from math import pi, sqrt, ceil

print(pi)          # 3.14159...
print(sqrt(16))    # 4.0
print(ceil(3.2))   # 4

# Import with alias (common for long names)
import datetime as dt
now = dt.datetime.now()
print(now)

# ─── STANDARD LIBRARY HIGHLIGHTS ─────────────────────────────────────────────

# os — file system, environment
print(os.getcwd())                        # current directory
print(os.path.exists("README.md"))        # True/False
env_var = os.getenv("HOME", "/tmp")       # like System.getenv() in Kotlin

# pathlib — modern path handling (prefer this over os.path)
current = Path(".")
home = Path.home()
readme = Path("README.md")
print(readme.exists())
print(readme.suffix)     # ".md"
print(readme.stem)       # "README"

# json — serialize/deserialize
data = {"name": "Ali", "age": 30, "skills": ["Python", "AI"]}
json_str = json.dumps(data, indent=2)
print(json_str)
parsed = json.loads(json_str)
print(parsed["name"])

# datetime
now = datetime.now()
tomorrow = now + timedelta(days=1)
print(now.strftime("%Y-%m-%d %H:%M"))
print(tomorrow.strftime("%A, %d %B %Y"))

# ─── COMMON THIRD-PARTY IMPORTS (you'll use these in AI projects) ─────────────

# These are imported when the packages are installed:
#
#   from openai import OpenAI                        # Week 2
#   from dotenv import load_dotenv                   # Week 2
#   from langchain_openai import ChatOpenAI          # Week 3
#   from langchain_core.prompts import ChatPromptTemplate  # Week 3
#   from fastapi import FastAPI, HTTPException       # Week 5
#   from pydantic import BaseModel                   # Week 2+
#   from langgraph.graph import StateGraph           # Week 7
#   from crewai import Agent, Task, Crew             # Week 8

# ─── PROJECT STRUCTURE PATTERN ───────────────────────────────────────────────
#
# A well-organized Python AI project looks like this:
#
#   my_project/
#   ├── .env                   ← API keys (NEVER commit this)
#   ├── .gitignore             ← should include .env and .venv/
#   ├── requirements.txt       ← pip freeze > requirements.txt
#   ├── main.py                ← entry point
#   ├── config.py              ← settings loaded from .env
#   └── src/
#       ├── __init__.py
#       ├── agents/
#       │   ├── __init__.py
#       │   └── research_agent.py
#       ├── tools/
#       │   ├── __init__.py
#       │   └── search_tool.py
#       └── models/
#           ├── __init__.py
#           └── schemas.py     ← Pydantic models

# ─── CONFIG PATTERN (you'll use this every week) ─────────────────────────────

# config.py pattern — load once, import everywhere
#
#   from dotenv import load_dotenv
#   import os
#
#   load_dotenv()
#
#   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#   if not OPENAI_API_KEY:
#       raise RuntimeError("OPENAI_API_KEY not set in .env")
#
#   MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
#   MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

# ─── __ALL__ — CONTROLLING EXPORTS ───────────────────────────────────────────

# In a module, __all__ defines what `from module import *` exports.
# You don't need this often but you'll see it in library code.
#
# utils.py:
#   __all__ = ["helper_one", "helper_two"]   # only these are "public"

# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Using only the standard library (os, pathlib, datetime):
#   Write a function `file_info(filepath: str) -> dict` that returns:
#   { "exists": bool, "size_bytes": int, "extension": str, "modified": str (ISO format) }
#   Test it on this lesson file itself.

# Exercise 2:
#   Write a function `load_json_safe(filepath: str) -> Optional[dict]`
#   that returns None (instead of raising an exception) if the file doesn't exist
#   or contains invalid JSON.

# Exercise 3:
#   Using datetime, write a function `days_until(target_date_str: str) -> int`
#   that takes a date string in "YYYY-MM-DD" format and returns how many days
#   until that date (negative if in the past).
#   days_until("2030-01-01") → some positive number
