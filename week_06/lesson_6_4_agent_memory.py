# Lesson 6.4 — Agent Memory: Conversation History, Reasoning Traces, Avoiding Repetition
# CONCEPT: Giving agents the ability to remember previous turns in a conversation
# KOTLIN EQUIVALENT: ConcurrentHashMap<String, MutableList<BaseMessage>> in a @Service
# PHP EQUIVALENT: Session/Cache-backed conversation state in a Laravel service

# ─── WHY AGENT MEMORY IS TRICKIER THAN CHAIN MEMORY ─────────────────────────
#
# For a simple chain:
#   prompt = ChatPromptTemplate([("system", "..."), MessagesPlaceholder("history"), ("human", "{input}")])
#   chain = prompt | llm
#   chain_with_memory = RunnableWithMessageHistory(chain, ...)
#   → Simple. History goes directly into the prompt.
#
# For an agent, the prompt already has a specific structure:
#   {tools}, {tool_names}, {input}, {agent_scratchpad}
# The ReAct prompt doesn't have a {history} slot by default.
#
# Solutions:
#   1. Use a CUSTOM ReAct prompt that includes {chat_history}
#   2. Prepend history to the {input} manually
#   3. Use newer agent types (create_openai_tools_agent) that handle this more cleanly
#
# In this lesson we use approach 3 (create_openai_tools_agent) which is
# the modern, cleaner way to handle both tool calling AND memory.

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Install: pip install langchain langchain-openai")

# ─── SIMPLE MEMORY: LIST OF MESSAGES ─────────────────────────────────────────
#
# The simplest agent memory is a list of HumanMessage/AIMessage objects.
# Each conversation turn appends to this list.
# The agent sees the full history as context.
#
# This is called ConversationBufferMemory in older LangChain,
# but the modern way is to pass the message list directly.
#
# Kotlin:
#   val history = mutableListOf<BaseMessage>()
#   history.add(HumanMessage(userInput))
#   val response = agent.invoke(input, history)
#   history.add(AIMessage(response))

# In-memory session store — in production use Redis or a DB
sessions: dict[str, list] = {}

def get_history(session_id: str) -> list:
    """Return message history for a session, creating empty list if new."""
    if session_id not in sessions:
        sessions[session_id] = []
    return sessions[session_id]

def add_to_history(session_id: str, human_msg: str, ai_msg: str):
    """Append a turn to the session history."""
    if LANGCHAIN_AVAILABLE:
        sessions[session_id].append(HumanMessage(content=human_msg))
        sessions[session_id].append(AIMessage(content=ai_msg))

# ─── TOOLS ────────────────────────────────────────────────────────────────────

if LANGCHAIN_AVAILABLE:
    # Track which topics have been searched (demonstrates memory preventing repetition)
    searched_topics: set[str] = set()

    @tool
    def web_search(query: str) -> str:
        """
        Searches the web for information about a topic.
        Use for current events, facts, or any information you don't know.
        Input: a search query string.
        """
        # Mock search — in production use Tavily or DuckDuckGo
        searched_topics.add(query.lower())
        mock_results = {
            "python": "Python is a high-level programming language created by Guido van Rossum in 1991.",
            "langchain": "LangChain is a framework for building applications with large language models.",
            "fastapi": "FastAPI is a modern Python web framework for building APIs with automatic validation.",
            "malaysia": "Malaysia is a country in Southeast Asia with a population of about 33 million.",
        }
        for keyword, result in mock_results.items():
            if keyword in query.lower():
                return result
        return f"Search result for '{query}': Found general information about the topic."

    @tool
    def calculator(expression: str) -> str:
        """
        Evaluates a math expression.
        Use for arithmetic calculations.
        Input: a Python math expression like '2 + 2' or '100 * 0.15'.
        """
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"{expression} = {result}"
        except Exception as e:
            return f"Error: {e}"

    @tool
    def remember_fact(fact: str) -> str:
        """
        Stores an important fact for later reference in this conversation.
        Use this when the user provides important information you should remember.
        Input: the fact to remember, as a clear sentence.
        """
        return f"Noted: '{fact}' has been remembered for this conversation."

# ─── BUILD MEMORY-ENABLED AGENT ───────────────────────────────────────────────
#
# create_openai_tools_agent uses OpenAI's native function/tool calling API.
# This is more reliable than ReAct for complex conversations.
# It natively handles chat_history in the prompt.
#
# Prompt structure for OpenAI tools agent:
#   [SystemMessage]
#   [MessagesPlaceholder("chat_history")]  ← conversation history goes here
#   [HumanMessage: {input}]
#   [MessagesPlaceholder("agent_scratchpad")]  ← tool calls/results go here

def build_memory_agent(verbose: bool = True):
    """
    Build an agent that maintains conversation history across turns.

    The agent:
    - Remembers what was said in previous turns
    - Can refer back to earlier topics
    - Shows its reasoning (verbose=True)
    """
    if not LANGCHAIN_AVAILABLE:
        return None
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in week_06/.env")
        return None

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    tools = [web_search, calculator, remember_fact]

    # Custom prompt that includes chat_history placeholder
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful research assistant with memory. "
            "You remember everything discussed in the conversation. "
            "If asked about something mentioned earlier, refer to the conversation history. "
            "If you need to look something up, use the web_search tool. "
            "For math, use the calculator tool."
        )),
        MessagesPlaceholder("chat_history"),      # Previous conversation turns
        ("human", "{input}"),                     # Current user message
        MessagesPlaceholder("agent_scratchpad"),  # Agent's tool calls (filled by executor)
    ])

    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=10,
        handle_parsing_errors=True,
    )

# ─── MULTI-TURN CONVERSATION DEMO ────────────────────────────────────────────
#
# This demonstrates the agent maintaining context across turns.
# Each message in a session uses the accumulated history.

def demo_memory_conversation():
    """
    Run a multi-turn conversation to demonstrate agent memory.

    Notice that in turn 3, the agent refers back to what was said in turn 1.
    Without memory, it would have no context.
    """
    agent = build_memory_agent(verbose=True)
    if not agent:
        print("Agent not available.")
        return

    session_id = "demo-session"
    history = get_history(session_id)

    # Multi-turn conversation where later questions reference earlier context
    conversation = [
        "What is Python programming language?",
        "Who created it and when?",                           # Refers to Python from turn 1
        "What percentage of software developers use it?",     # Still about Python
        "What is 33 multiplied by 4.65?",                    # Unrelated math
        "Based on our conversation, summarize what I've learned about Python.",  # Requires memory
    ]

    print("=" * 60)
    print("MULTI-TURN AGENT CONVERSATION WITH MEMORY")
    print("=" * 60)

    for i, message in enumerate(conversation, 1):
        print(f"\n[Turn {i}] USER: {message}")
        print("-" * 40)

        try:
            result = agent.invoke({
                "input": message,
                "chat_history": history,  # Pass accumulated history
            })
            reply = result["output"]
            print(f"AGENT: {reply}")

            # Store this turn in history for the next iteration
            add_to_history(session_id, message, reply)

        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 60)
    print(f"Conversation complete. {len(history) // 2} turns stored in memory.")

# ─── INSPECTING THE REASONING TRACE ──────────────────────────────────────────
#
# verbose=True shows the agent's internal reasoning:
#
#   > Entering new AgentExecutor chain...
#
#   Invoking: `web_search` with `{'query': 'Python programming language history'}`
#   Python is a high-level programming language...
#
#   Python was created by Guido van Rossum and first released in 1991.
#
#   > Finished chain.
#
# This is like enabling DEBUG logging in Spring Boot — you see every step.
# In production, set verbose=False or use callbacks to capture traces.
#
# Kotlin equivalent: @Slf4j + log.debug() in your AgentExecutor service
# Laravel equivalent: Log::debug() or Telescope tracing

# ─── TRIMMING MEMORY (prevent token overflow) ─────────────────────────────────
#
# Long conversations grow the history, which uses more tokens.
# At some point you'll hit the model's context window limit.
#
# Strategies:
#   1. Keep last N messages (simple sliding window)
#   2. Summarize old messages (compress but keep meaning)
#   3. Use a vector store to retrieve only relevant past messages

def trim_history(history: list, max_messages: int = 20) -> list:
    """
    Keep only the last max_messages messages.
    Always keep an even number (HumanMessage + AIMessage pairs).

    Kotlin: history.takeLast(maxMessages)
    Laravel: array_slice($history, -$maxMessages)
    """
    if len(history) <= max_messages:
        return history
    # Ensure we keep complete pairs (trim from the start)
    trimmed = history[-max_messages:]
    # Make sure we start with a HumanMessage
    if LANGCHAIN_AVAILABLE and trimmed and isinstance(trimmed[0], AIMessage):
        trimmed = trimmed[1:]
    return trimmed

if __name__ == "__main__":
    print("Lesson 6.4 — Agent Memory")
    print()
    demo_memory_conversation()

# ─── EXERCISES ────────────────────────────────────────────────────────────────
# EXERCISE 1:
#   Run the demo_memory_conversation() and inspect the verbose output.
#   For Turn 5 ("Based on our conversation, summarize..."), does the agent
#   actually use the chat_history? How can you tell from the trace?
#   Write your observations as comments.
#
# EXERCISE 2:
#   Modify the conversation list to include a message like:
#   "My name is [your name] and I'm from Malaysia."
#   Then later ask: "What's my name and where am I from?"
#   Does the agent remember without calling any tools?
#   Hint: The agent should answer from chat_history, not use web_search.
#
# EXERCISE 3:
#   Implement a "session summary" feature:
#   After every 3 turns, call the LLM to summarize the conversation so far,
#   then replace the history with a single SystemMessage containing that summary.
#   This reduces token usage on long conversations.
#   Hint: use `llm.invoke([HumanMessage("Summarize this: ..." + str(history))])`
#   and then reset: sessions[session_id] = [SystemMessage(summary)]
