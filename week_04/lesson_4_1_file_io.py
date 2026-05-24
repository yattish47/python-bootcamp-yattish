# Lesson 4.1 — File I/O and pathlib
# Python for AI Engineers | Week 4
#
# CONCEPT:
#   Python's built-in `open()` handles text and binary files.
#   `pathlib.Path` is the modern, object-oriented way to work with file paths —
#   it replaces os.path, os.getcwd(), and manual string concatenation.
#   The `json` module converts between Python dicts/lists and JSON text.
#
# KOTLIN EQUIVALENT:
#   open() / BufferedReader ≈ Python's open(); but Python is simpler — no
#   checked exceptions, no need to specify charset most of the time.
#   File("path").readText() ≈ Path("path").read_text()
#   Paths.get() / Path ≈ pathlib.Path
#
# PHP EQUIVALENT:
#   file_get_contents("path") ≈ Path("path").read_text()
#   file_put_contents("path", $data) ≈ Path("path").write_text(data)
#   json_decode / json_encode ≈ json.loads / json.dumps

from __future__ import annotations

import json
import tempfile
from pathlib import Path

# ─── READING AND WRITING TEXT FILES ──────────────────────────────────────────

# Always use `with open(...)` — it guarantees the file is closed even if an
# exception is raised (like Java's try-with-resources / Kotlin's use{}).

# Write a text file
tmp = Path(tempfile.gettempdir())
sample_file = tmp / "lesson_4_1_sample.txt"

with open(sample_file, "w", encoding="utf-8") as f:
    f.write("Line one\n")
    f.write("Line two\n")
    f.write("Line three\n")

print(f"Wrote to: {sample_file}")

# Read entire file as one string
with open(sample_file, "r", encoding="utf-8") as f:
    content = f.read()
print("Full content:")
print(content)

# Read line by line (memory-efficient for large files)
with open(sample_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        print(f"  Line {i}: {line.rstrip()}")

# Read all lines into a list
with open(sample_file, "r", encoding="utf-8") as f:
    lines = f.readlines()          # includes \n at end of each line
print(f"Lines: {lines}")

# Append to a file (mode "a" doesn't truncate)
with open(sample_file, "a", encoding="utf-8") as f:
    f.write("Line four (appended)\n")
print(f"Lines after append: {sum(1 for _ in open(sample_file))}")


# ─── FILE MODES CHEATSHEET ────────────────────────────────────────────────────

# | Mode | Meaning                                         |
# |------|-------------------------------------------------|
# | "r"  | Read (default) — file must exist                |
# | "w"  | Write — creates or truncates existing file      |
# | "a"  | Append — creates or appends to existing file   |
# | "x"  | Exclusive create — fails if file exists         |
# | "rb" | Read binary (images, PDFs, etc.)                |
# | "wb" | Write binary                                    |
# Add "+" for read+write: "r+" reads and writes without truncating


# ─── JSON FILES ───────────────────────────────────────────────────────────────

# json.dump() — Python object → JSON file
# json.load() — JSON file → Python object
# json.dumps() — Python object → JSON string (s = string)
# json.loads() — JSON string → Python object

data = {
    "users": [
        {"id": 1, "name": "Yattish", "role": "developer"},
        {"id": 2, "name": "Bot", "role": "assistant"},
    ],
    "settings": {"theme": "dark", "language": "en"},
}

json_file = tmp / "lesson_4_1_data.json"

# Write JSON
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"\nWrote JSON to: {json_file}")

# Read JSON
with open(json_file, "r", encoding="utf-8") as f:
    loaded = json.load(f)

print(f"Loaded {len(loaded['users'])} users")
print(f"First user: {loaded['users'][0]}")

# Pretty-print a dict as JSON string (useful for debugging)
print("\nPretty JSON string:")
print(json.dumps(data["settings"], indent=2))

# Round-trip: dict → string → back to dict
raw_json = '{"name": "Alice", "score": 42}'
obj = json.loads(raw_json)
print(f"\nParsed: {obj}, type: {type(obj['score'])}")


# ─── pathlib.Path — MODERN PATH HANDLING ─────────────────────────────────────

# Path objects are far nicer than string concatenation with os.path.join().

p = Path("/tmp")                        # absolute path
lesson_dir = Path(__file__).parent     # directory containing this script
home = Path.home()                     # /Users/username or /home/username
cwd = Path.cwd()                       # current working directory

print(f"\nCurrent file:   {Path(__file__)}")
print(f"Parent dir:     {lesson_dir}")
print(f"Home directory: {home}")

# Path arithmetic — use / to join paths (no os.path.join needed)
config_path = home / ".config" / "myapp" / "settings.json"
print(f"Config path:    {config_path}")

# Path properties
example = Path("/Users/yattish/Documents/data/report.csv")
print(f"\nname:    {example.name}")       # report.csv
print(f"stem:    {example.stem}")        # report
print(f"suffix:  {example.suffix}")      # .csv
print(f"parent:  {example.parent}")      # /Users/yattish/Documents/data
print(f"parts:   {example.parts}")       # ('/', 'Users', ...)

# Existence checks
print(f"\nDoes /tmp exist?     {Path('/tmp').exists()}")
print(f"Is /tmp a dir?       {Path('/tmp').is_dir()}")
print(f"Is /tmp a file?      {Path('/tmp').is_file()}")


# ─── READ / WRITE TEXT WITH pathlib ───────────────────────────────────────────

# Shortcuts — no need to open() for simple read/write

quick_file = tmp / "lesson_4_1_quick.txt"
quick_file.write_text("Hello from pathlib!\nLine 2\n", encoding="utf-8")
content = quick_file.read_text(encoding="utf-8")
print(f"\npathlib read: {content.strip()!r}")

# Read as bytes
raw_bytes = quick_file.read_bytes()
print(f"Byte length: {len(raw_bytes)}")


# ─── CREATING DIRECTORIES ────────────────────────────────────────────────────

new_dir = tmp / "lesson_4_1_subdir" / "nested"
new_dir.mkdir(parents=True, exist_ok=True)   # like mkdir -p
print(f"\nCreated dir: {new_dir}")

# Write a file inside it
(new_dir / "hello.txt").write_text("nested file content")


# ─── LISTING AND GLOBBING ────────────────────────────────────────────────────

# iterdir() — immediate children (like os.listdir)
print("\nFiles in /tmp (first 5 Python-related):")
tmp_path = Path("/tmp")
py_files = [p for p in tmp_path.iterdir() if p.suffix in (".py", ".txt")]
for p in py_files[:5]:
    print(f"  {p.name}")

# glob() — shell-style pattern matching in a directory
# rglob() — recursive glob (searches all subdirectories)
lesson_files = list(Path(__file__).parent.glob("lesson_*.py"))
print(f"\nLesson files found: {len(lesson_files)}")
for f in sorted(lesson_files):
    print(f"  {f.name}")

# rglob — find all .json files anywhere under week_04/
week04_dir = Path(__file__).parent
json_files = list(week04_dir.rglob("*.json"))
print(f"\nJSON files under week_04/: {[f.name for f in json_files]}")


# ─── WALKING A DIRECTORY TREE ────────────────────────────────────────────────

def list_tree(root: Path, indent: int = 0) -> None:
    """Recursively print a directory tree."""
    prefix = "  " * indent
    for item in sorted(root.iterdir()):
        if item.name.startswith(".") or item.name == "__pycache__":
            continue
        size = f" ({item.stat().st_size}B)" if item.is_file() else "/"
        print(f"{prefix}{item.name}{size}")
        if item.is_dir():
            list_tree(item, indent + 1)


print(f"\nDirectory tree of week_04/:")
list_tree(Path(__file__).parent)


# ─── PRACTICAL PATTERN — SAFE JSON READ ──────────────────────────────────────

def read_json(path: Path) -> dict | list:
    """Read a JSON file, returning an empty dict if it doesn't exist."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict | list, indent: int = 2) -> None:
    """Write a Python object to a JSON file, creating parent dirs if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent), encoding="utf-8")


# Demo
test_path = tmp / "lesson_4_1_test.json"
write_json(test_path, {"key": "value", "numbers": [1, 2, 3]})
loaded_data = read_json(test_path)
print(f"\nround-trip JSON: {loaded_data}")
missing = read_json(Path("/tmp/does_not_exist.json"))
print(f"Missing file returns: {missing!r}")


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 — CSV LOGGER
#   Write a function `log_event(event: dict, log_file: Path)` that appends
#   the event as a JSON line to log_file (one JSON object per line — "JSONL" format).
#   Write 5 events with different timestamps and data. Then write a function
#   `read_events(log_file: Path) -> list[dict]` that reads all events back.

# Exercise 2 — FILE SEARCH
#   Write a function `find_files(root: Path, extension: str) -> list[Path]`
#   that uses rglob() to find all files with the given extension under root.
#   Sort the results by file size (largest first) and return them.
#   Test it by finding all .py files in the python_learning directory.

# Exercise 3 — CONFIG PERSISTENCE
#   Write a simple config manager:
#     - `load_config(path: Path) -> dict` — reads JSON config, returns {} if missing
#     - `save_config(path: Path, config: dict)` — writes JSON config
#     - `update_config(path: Path, **kwargs)` — loads, merges kwargs, saves
#   Demonstrate: create a config, update a key, add a new key, then reload and print.
