# Lesson 4.2 — Environment Variables & Configuration
# Python for AI Engineers | Week 4
#
# CONCEPT:
#   Never hardcode API keys, database URLs, or secrets in source code.
#   .env files store these outside the codebase; python-dotenv loads them
#   into environment variables at runtime. `os.getenv()` reads them safely.
#
# KOTLIN EQUIVALENT:
#   application.properties / application.yml ≈ .env
#   @Value("${MY_KEY}") or @ConfigurationProperties ≈ os.getenv()
#   spring-dotenv library provides similar .env support for Spring Boot
#
# PHP EQUIVALENT:
#   Laravel's .env + config() helper ≈ python-dotenv + os.getenv()
#   env('KEY', 'default') in Laravel ≈ os.getenv('KEY', 'default') in Python

import os
import sys
from pathlib import Path

# ─── WHY .env FILES? ─────────────────────────────────────────────────────────

# Bad — key is in source code:
# openai.api_key = "sk-abc123..."   ← committed to git → public forever

# Good — key comes from environment:
# openai.api_key = os.getenv("OPENAI_API_KEY")  ← .env is gitignored


# ─── python-dotenv BASICS ─────────────────────────────────────────────────────

# pip install python-dotenv

from dotenv import load_dotenv, dotenv_values

# load_dotenv() reads a .env file and sets the variables in os.environ.
# It does NOT override variables that are already set (safe for CI/CD systems
# where real environment variables take precedence over .env files).

# Load from default location (.env in current directory)
load_dotenv()

# Load from a specific path
_this_dir = Path(__file__).parent
load_dotenv(_this_dir / ".env", override=False)   # override=False = don't overwrite existing

# Check what's loaded
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    masked = api_key[:7] + "..." + api_key[-4:]
    print(f"OPENAI_API_KEY loaded: {masked}")
else:
    print("OPENAI_API_KEY not set")


# ─── os.getenv() — READING VARIABLES ──────────────────────────────────────────

# os.getenv(key)                  → returns None if not set (no exception)
# os.getenv(key, default)         → returns default if not set
# os.environ[key]                 → raises KeyError if not set

# Safe — use this
debug_mode = os.getenv("DEBUG", "false").lower() == "true"
port = int(os.getenv("PORT", "8080"))
database_url = os.getenv("DATABASE_URL", "sqlite:///local.db")

print(f"\nConfiguration from environment:")
print(f"  DEBUG:        {debug_mode}")
print(f"  PORT:         {port}")
print(f"  DATABASE_URL: {database_url}")

# os.environ is a dict — you can iterate it
print(f"\nAll environment variables starting with 'OPENAI':")
for key, value in os.environ.items():
    if key.startswith("OPENAI"):
        masked_val = value[:4] + "..." if len(value) > 4 else value
        print(f"  {key} = {masked_val}")


# ─── PATTERN: config.py — FAIL FAST ON MISSING REQUIRED KEYS ─────────────────

# In production, you want to crash immediately at startup if a required
# variable is missing — not at runtime when the first API call fails.

class Config:
    """
    Centralised configuration that validates required keys at import time.
    Pattern used in most production Python services.
    """

    def __init__(self):
        load_dotenv()   # idempotent — safe to call multiple times
        self.openai_api_key: str = self._require("OPENAI_API_KEY")
        self.model: str = os.getenv("MODEL", "gpt-4o-mini")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.port: int = int(os.getenv("PORT", "8080"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @staticmethod
    def _require(key: str) -> str:
        """Return the value of an env var or raise a clear error."""
        value = os.getenv(key)
        if not value:
            raise EnvironmentError(
                f"Required environment variable '{key}' is not set.\n"
                f"Add it to your .env file: {key}=your_value_here"
            )
        return value

    def __repr__(self) -> str:
        key = self.openai_api_key
        masked = key[:7] + "..." if len(key) > 7 else "***"
        return (
            f"Config(model={self.model!r}, debug={self.debug}, "
            f"port={self.port}, key={masked!r})"
        )


# Load config (will raise EnvironmentError if OPENAI_API_KEY is missing)
try:
    config = Config()
    print(f"\nConfig loaded: {config}")
except EnvironmentError as e:
    print(f"\nConfig error: {e}")


# ─── READING .env AS A DICT (without setting os.environ) ─────────────────────

# Sometimes you want to inspect .env values without polluting os.environ.
# dotenv_values() returns a dict without modifying the environment.

env_path = _this_dir / ".env"
if env_path.exists():
    env_dict = dotenv_values(env_path)
    print(f"\n.env file contains {len(env_dict)} variable(s): {list(env_dict.keys())}")
else:
    print(f"\nNo .env file at {env_path}")


# ─── MULTIPLE .env FILES ──────────────────────────────────────────────────────

# Common pattern in teams:
#
# .env          — shared defaults (committed to git, NO secrets)
# .env.local    — developer overrides (gitignored)
# .env.test     — test-specific values (may be committed)
# .env.prod     — production values (NEVER committed, injected by CI/CD)
#
# Loading order (last write wins, or use override=False to keep first):

def load_env_for_environment(env_name: str = "local") -> None:
    """Load base .env then override with .env.<env_name>."""
    base = _this_dir / ".env"
    override_file = _this_dir / f".env.{env_name}"

    load_dotenv(base, override=False)
    if override_file.exists():
        load_dotenv(override_file, override=True)
        print(f"Loaded {base.name} + {override_file.name}")
    else:
        print(f"Loaded {base.name} only (no {override_file.name})")

# In practice, you'd call this once at app startup:
# load_env_for_environment(os.getenv("APP_ENV", "local"))


# ─── WHAT TO PUT IN .gitignore ────────────────────────────────────────────────

GITIGNORE_ADDITIONS = """
# .gitignore — add these for Python AI projects

# Environment files with secrets
.env
.env.local
.env.*.local
.env.prod
.env.production

# Python cache
__pycache__/
*.py[cod]
*.pyo

# Virtual environments
venv/
.venv/
env/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
"""
print("\n.gitignore recommendations:")
print(GITIGNORE_ADDITIONS)


# ─── PRACTICAL HELPER — get_required ─────────────────────────────────────────

def get_required(key: str) -> str:
    """Get a required environment variable, raising a clear error if missing."""
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(
            f"Missing required environment variable: {key}\n"
            f"Set it with: export {key}=value  OR add it to your .env file"
        )
    return value


def get_optional(key: str, default: str = "") -> str:
    """Get an optional environment variable with a default value."""
    return os.getenv(key, default)


# Demo
try:
    key = get_required("OPENAI_API_KEY")
    print(f"API key found (length: {len(key)})")
except EnvironmentError as e:
    print(f"Not found: {e}")

model = get_optional("MODEL", "gpt-4o-mini")
print(f"Using model: {model}")


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 — TYPED CONFIG CLASS
#   Extend the Config class to include:
#     - MAX_RETRIES: int (default 3)
#     - RATE_LIMIT_RPM: int (required — raise if missing)
#     - ALLOWED_MODELS: list[str] (parse from comma-separated string, e.g. "gpt-4o,gpt-4o-mini")
#   Add a validate() method that raises ValueError if any value is out of range
#   (e.g., MAX_RETRIES < 1 or MAX_RETRIES > 10).

# Exercise 2 — ENV FILE GENERATOR
#   Write a function `generate_env_template(config_class) -> str` that inspects
#   a Config-like class and generates a .env.example string.
#   For required fields output: KEY=   (empty value, user must fill in)
#   For optional fields output: KEY=default_value
#   Print the result so someone new to the project knows what to set.

# Exercise 3 — ENVIRONMENT SWITCHER
#   Create three mini .env files in /tmp: .env.dev, .env.staging, .env.prod
#   Each has APP_NAME, LOG_LEVEL, and DEBUG set to different values.
#   Write a function `switch_env(env: str)` that loads the right file and
#   prints a summary of the loaded config. Test all three environments.
