# Lesson 6.1 — Agent Introduction: ReAct Loop, AgentExecutor, Tool Calling
# CONCEPT: An agent uses an LLM to dynamically decide which tools to call and when
# KOTLIN EQUIVALENT: A @Service class with a while loop that calls @Component tools based on LLM decisions
# PHP EQUIVALENT: A Laravel job that dispatches other jobs/actions based on LLM output

# ─── WHAT IS AN AGENT? ────────────────────────────────────────────────────────
#
# A chain is a fixed pipeline:
#   Input → Step 1 → Step 2 → Step 3 → Output
#   Like a Spring @Service with hardcoded method calls.
#
# An agent is a loop:
#   Input → [LLM thinks] → [LLM picks a tool] → [Tool runs] → [LLM sees result]
#         → [LLM thinks again] → [Pick another tool OR give final answer]
#
# The LLM is the "brain" that decides what to do next.
# Tools are the "hands" that actually do things.
#
# Kotlin analogy:
#   while (!isDone) {
#       val decision = llm.think(question, previousObservations)
#       if (decision.isFinalAnswer) break
#       val result = toolRegistry[decision.toolName].execute(decision.toolArgs)
#       observations.add(result)
#   }
#
# Laravel analogy:
#   while (!$isDone) {
#       $decision = $llm->think($question, $history);
#       if ($decision->isFinalAnswer()) break;
#       $result = app($decision->toolClass)->handle($decision->args);
#       $history[] = $result;
#   }

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ─── LANGCHAIN AGENT IMPORTS ──────────────────────────────────────────────────

try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain_core.tools import tool
    from langchain import hub
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Install: pip install langchain langchain-openai")

# ─── THE REACT PATTERN ────────────────────────────────────────────────────────
#
# ReAct = Reasoning + Acting
# The LLM is prompted to output in this format:
#
#   Thought: I need to figure out what 123 * 456 is.
#   Action: calculator
#   Action Input: 123 * 456
#   Observation: 56088
#   Thought: I now know the answer.
#   Final Answer: 123 * 456 = 56088
#
# The AgentExecutor parses this output, calls the right tool,
# feeds the result back as "Observation", and loops.
#
# This is the key insight: the LLM outputs TEXT that looks like a function call,
# and the agent framework parses that text and actually calls the function.

# ─── DEFINE A SIMPLE TOOL ────────────────────────────────────────────────────
#
# A "tool" is just a Python function with:
#   1. A clear name (the LLM uses this to pick the tool)
#   2. A docstring (the LLM reads this to understand what the tool does)
#   3. A return value (becomes the "Observation" the LLM sees)
#
# Kotlin: @Component class CalculatorTool : Tool { override fun name() = "calculator" }
# Laravel: class CalculatorTool extends Action { public function handle(string $expr) }

if LANGCHAIN_AVAILABLE:
    @tool
    def calculator(expression: str) -> str:
        """
        Evaluates a mathematical expression and returns the result.
        Use this for any arithmetic: addition, subtraction, multiplication, division, powers.
        Input should be a valid Python math expression like '2 + 2' or '100 * 1.1 ** 5'.
        """
        try:
            # eval() is safe here because we're in a controlled demo context.
            # In production: use a proper math parser (e.g., asteval, sympy).
            result = eval(expression, {"__builtins__": {}}, {})
            return f"{expression} = {result}"
        except Exception as e:
            return f"Error evaluating '{expression}': {e}"

    @tool
    def string_reverse(text: str) -> str:
        """
        Reverses a string.
        Use this when the user asks to reverse any text or string.
        Input: the string to reverse.
        """
        return text[::-1]

    @tool
    def word_count(text: str) -> str:
        """
        Counts the number of words in a piece of text.
        Use this when the user asks how many words are in something.
        Input: the text to count words in.
        """
        count = len(text.split())
        return f"The text has {count} words."

# ─── BUILD THE AGENT ──────────────────────────────────────────────────────────
#
# create_react_agent() builds a ReAct agent from:
#   - llm: the brain (ChatOpenAI)
#   - tools: the toolbox
#   - prompt: the ReAct prompt template (includes {tools}, {tool_names}, {input}, {agent_scratchpad})
#
# AgentExecutor wraps the agent and runs the loop:
#   - max_iterations: safety limit to prevent infinite loops
#   - verbose: show the Thought/Action/Observation trace (like debug logging)
#
# Kotlin: new AgentExecutor(llm, tools, maxIterations=10, verbose=true)

def build_agent(verbose: bool = True):
    """Build and return an AgentExecutor with calculator, reverse, and word_count tools."""
    if not LANGCHAIN_AVAILABLE:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY in week_06/.env to run the agent.")
        return None

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    tools = [calculator, string_reverse, word_count]

    # Pull the standard ReAct prompt from LangChain Hub
    # This prompt tells the LLM to output in Thought/Action/Action Input/Observation format
    prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,          # Print Thought/Action/Observation steps
        max_iterations=10,        # Prevent infinite loops
        handle_parsing_errors=True,  # Don't crash on malformed LLM output
    )

# ─── DEMO: RUNNING THE AGENT ──────────────────────────────────────────────────
#
# The agent will:
# 1. Read the question
# 2. Think about which tool to use
# 3. Call the tool
# 4. Read the result (Observation)
# 5. Decide if it has the answer or needs another tool
# 6. Return the Final Answer

def demo_agent():
    agent_executor = build_agent(verbose=True)
    if not agent_executor:
        print("Agent not available. Check OPENAI_API_KEY and langchain installation.")
        return

    questions = [
        "What is 1337 * 42?",
        "Reverse the string 'Hello, World!'",
        "How many words are in the sentence 'The quick brown fox jumps over the lazy dog'?",
        "What is 15% of 840? Then reverse the string 'Python'.",  # Multi-step!
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"QUESTION: {question}")
        print('='*60)
        try:
            result = agent_executor.invoke({"input": question})
            print(f"\nFINAL ANSWER: {result['output']}")
        except Exception as e:
            print(f"Error: {e}")

# ─── UNDERSTANDING THE AGENT LOOP (without running it) ────────────────────────
#
# This is a pseudocode representation of what AgentExecutor does internally:
#
# def agent_loop(question, tools, llm, max_iterations):
#     scratchpad = ""
#     for i in range(max_iterations):
#         # LLM sees: question + scratchpad of previous steps
#         llm_output = llm.generate(prompt(question, scratchpad, tools))
#
#         if "Final Answer:" in llm_output:
#             return extract_final_answer(llm_output)
#
#         # Parse the LLM's tool choice
#         action = parse_action(llm_output)        # e.g., "calculator"
#         action_input = parse_input(llm_output)   # e.g., "1337 * 42"
#
#         # Actually call the tool
#         observation = tools[action].run(action_input)
#
#         # Add this step to the scratchpad so LLM sees it next iteration
#         scratchpad += f"Thought: ...\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}\n"
#
#     return "Max iterations reached"
#
# Kotlin:
#   var scratchpad = ""
#   repeat(maxIterations) {
#       val output = llm.generate(buildPrompt(question, scratchpad, tools))
#       if (output.contains("Final Answer:")) return extractAnswer(output)
#       val observation = toolRegistry[parseAction(output)].execute(parseInput(output))
#       scratchpad += buildScratchpadEntry(output, observation)
#   }

if __name__ == "__main__":
    print("Lesson 6.1 — Agent Introduction")
    print("This lesson demonstrates the ReAct agent loop.")
    print()

    if LANGCHAIN_AVAILABLE:
        demo_agent()
    else:
        print("To run the demo: pip install langchain langchain-openai")
        print("Then set OPENAI_API_KEY in week_06/.env")

# ─── EXERCISES ────────────────────────────────────────────────────────────────
# EXERCISE 1 (Conceptual — draw the agent loop):
#   Trace the ReAct loop for this question:
#   "What is the square root of 144, and how many letters are in 'mathematics'?"
#   Write out the expected:
#     Thought → Action → Action Input → Observation → Thought → ...→ Final Answer
#   Do this on paper or as comments. Don't run the agent yet.
#
# EXERCISE 2 (Code):
#   Add a new tool called `uppercase` that converts a string to uppercase.
#   Add it to the tools list in build_agent().
#   Test it with: "Convert 'langchain agents are powerful' to uppercase."
#
# EXERCISE 3 (Conceptual):
#   When would you use a chain instead of an agent?
#   Give two scenarios where a chain is better, and two where an agent is better.
#   Write your answers as comments.
#
#   Hint for chains: summarizing a fixed document, translating text
#   Hint for agents: answering questions that require web search, multi-step math
