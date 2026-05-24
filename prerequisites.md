# Prerequisites — Python for AI Engineers

Complete this setup before Lesson 1.1. It should take about 20–30 minutes.

---

## 1. Install Python 3.11+

**macOS (recommended via Homebrew):**
```bash
brew install python@3.11
python3 --version   # should print Python 3.11.x or higher
```

**Alternative — python.org installer:**
Download from https://www.python.org/downloads/ and run the installer.

---

## 2. Install pyenv (Python version manager)

`pyenv` lets you switch between Python versions per project — like `nvm` for Node or `sdk` for Java.

```bash
brew install pyenv

# Add to your shell profile (~/.zshrc or ~/.bashrc):
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

source ~/.zshrc

# Install and set Python 3.11
pyenv install 3.11.9
pyenv global 3.11.9
python --version   # should print Python 3.11.9
```

---

## 3. Install VS Code + Python Extension

1. Download VS Code from https://code.visualstudio.com
2. Open VS Code → Extensions (⌘⇧X) → search **"Python"** → install the one by Microsoft
3. Optional but recommended: also install **"Pylance"** for better type checking

---

## 4. How Virtual Environments Work

Python uses **virtual environments** to isolate packages per project — like Gradle per-project dependencies or Composer's `vendor/` folder.

**Create and activate a venv for each week's work:**
```bash
cd python_learning/week_01
python -m venv .venv
source .venv/bin/activate     # activate on macOS/Linux
# (.venv) should appear in your terminal prompt

deactivate                    # when done
```

**You will create a new venv for each week** as new packages are introduced.

---

## 5. API Keys

You will need these API keys as you progress through the course.

| Week | Service | Free Tier? | Get it at |
|------|---------|-----------|-----------|
| Week 2 | **OpenAI API** | $5 free credit | https://platform.openai.com/api-keys |
| Week 6 | **Tavily Search** (optional) | 1,000 free searches/mo | https://app.tavily.com |

**How to store API keys safely:**

Each project week has a `.env` file (which is never committed to git):
```
# python_learning/week_02/.env
OPENAI_API_KEY=sk-...your-key-here...
```

Load it in Python with:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

---

## 6. Package Install Pattern

Packages are installed **per week**, not all upfront. Each week's `README.md` lists what to install.

```bash
# Example — Week 2 setup
cd python_learning/week_02
python -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv
```

---

## 7. Quick Sanity Check

Run this to confirm your environment is ready:

```bash
python --version          # Python 3.11+
pip --version             # pip 23+
code --version            # VS Code is in PATH
```

If `code` is not found: open VS Code → Cmd+Shift+P → type **"Shell Command: Install 'code' command in PATH"**

---

## You're Ready

Once the above checks pass, open `week_01/README.md` and start Lesson 1.1.


#                                                                                                                                                            
# To activate this environment, use
#
#     $ conda activate pyai
#
# To deactivate an active environment, use
#
#     $ conda deactivate
