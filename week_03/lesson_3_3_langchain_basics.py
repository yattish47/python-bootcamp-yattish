# Lesson 3.3 — LangChain Basics
# Python for AI Engineers | Week 3
#
# CONCEPT:
#   LangChain wraps LLM APIs with composable building blocks called Runnables.
#   You connect them with the `|` pipe operator (LCEL — LangChain Expression
#   Language) to form chains: prompt | llm | parser.
#   Each component has .invoke(), .stream(), and .batch() built in.
#
# KOTLIN EQUIVALENT:
#   LCEL `|` ≈ Kotlin function chaining / Sequence.map().filter()
#   A LangChain chain ≈ a composable pipeline of functions returning the same type
#
# PHP EQUIVALENT:
#   No direct equivalent; closest is a chain-of-responsibility pattern or
#   Laravel Pipeline: app(Pipeline::class)->send($data)->through([...])->thenReturn()

# ─── SETUP CHECK ──────────────────────────────────────────────────────────────

# Run this first: pip install langchain langchain-openai
# Set OPENAI_API_KEY in week_03/.env

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the week_03 directory (works regardless of where you run this)
_week_dir = Path(__file__).parent
load_dotenv(_week_dir / ".env")

if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not set. Live examples will be skipped.")
    print("Create week_03/.env with: OPENAI_API_KEY=sk-...")
    _HAS_KEY = False
else:
    _HAS_KEY = True


# ─── WHAT IS LCEL? ───────────────────────────────────────────────────────────

# LangChain Expression Language (LCEL) lets you compose Runnables using `|`.
# Every LangChain component is a Runnable: it has .invoke(), .stream(), .batch().
#
# Basic chain shape:
#
#   prompt_template | llm | output_parser
#
# When you call chain.invoke({"variable": "value"}):
#   1. prompt_template formats the variables into a ChatPromptValue
#   2. llm sends it to OpenAI, gets back an AIMessage
#   3. output_parser extracts the string from AIMessage
#
# This is composability: each step's output is the next step's input.


# ─── CORE IMPORTS ─────────────────────────────────────────────────────────────

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


# ─── ChatOpenAI ───────────────────────────────────────────────────────────────

# ChatOpenAI wraps the OpenAI chat completions API as a LangChain Runnable.
# You can swap this for ChatAnthropic, ChatGoogleGenerativeAI, ChatOllama, etc.
# without changing the rest of your chain — that's the main value of the wrapper.

if _HAS_KEY:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=256,
    )

    # Direct invocation — pass a list of messages (like the raw SDK)
    response = llm.invoke([
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is 2 + 2? Reply in one sentence."),
    ])
    print("Direct LLM call:")
    print(f"  content: {response.content}")
    print(f"  type:    {type(response).__name__}")   # AIMessage
    print()


# ─── ChatPromptTemplate ───────────────────────────────────────────────────────

# Prompt templates make prompts reusable and parameterised.
# Variables wrapped in {curly_braces} are filled in at .invoke() time.

joke_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a witty assistant that tells short, clever jokes."),
    ("human", "Tell me a joke about {topic}."),
])

# You can inspect what a template produces without calling the LLM:
formatted = joke_prompt.invoke({"topic": "Python programming"})
print("Formatted prompt messages:")
for msg in formatted.messages:
    print(f"  [{msg.__class__.__name__}] {msg.content}")
print()


# ─── THE PIPE OPERATOR — BUILDING A CHAIN ─────────────────────────────────────

# chain = prompt | llm | parser
# This is equivalent to:
#   def chain(inputs):
#       return parser(llm(prompt.invoke(inputs)))

parser = StrOutputParser()   # extracts .content string from AIMessage

if _HAS_KEY:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=128)
    joke_chain = joke_prompt | llm | parser

    joke = joke_chain.invoke({"topic": "async programming"})
    print(f"Joke chain result:\n  {joke}\n")


# ─── MULTI-VARIABLE TEMPLATES ─────────────────────────────────────────────────

translation_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a professional translator. Translate accurately and naturally."),
    ("human", "Translate the following text from {source_lang} to {target_lang}:\n\n{text}"),
])

if _HAS_KEY:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    translate_chain = translation_prompt | llm | parser

    result = translate_chain.invoke({
        "source_lang": "English",
        "target_lang": "Malay",
        "text": "Hello, how are you today?",
    })
    print(f"Translation: {result}\n")


# ─── STREAMING WITH .stream() ─────────────────────────────────────────────────

# .stream() yields chunks as they arrive from the API — same as SSE / streaming.
# This is what you use in chatbots to show text appearing token by token.

streaming_prompt = ChatPromptTemplate.from_messages([
    ("human", "Write a 3-sentence story about {subject}. Be creative."),
])

if _HAS_KEY:
    llm_stream = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)
    stream_chain = streaming_prompt | llm_stream | parser

    print("Streaming response:", flush=True)
    for chunk in stream_chain.stream({"subject": "a robot learning to cook"}):
        print(chunk, end="", flush=True)
    print("\n")


# ─── .batch() — MULTIPLE INPUTS AT ONCE ──────────────────────────────────────

# .batch() processes a list of inputs, concurrently where possible.

if _HAS_KEY:
    sentiment_prompt = ChatPromptTemplate.from_messages([
        ("system", "Reply with only one word: Positive, Negative, or Neutral."),
        ("human", "{review}"),
    ])
    sentiment_chain = sentiment_prompt | llm | parser

    reviews = [
        {"review": "This product is amazing, I love it!"},
        {"review": "Terrible quality, broke after one day."},
        {"review": "It arrived on time."},
    ]
    sentiments = sentiment_chain.batch(reviews)
    print("Batch sentiment results:")
    for review, sentiment in zip(reviews, sentiments):
        print(f"  {review['review'][:40]!r:45} → {sentiment.strip()}")
    print()


# ─── CUSTOM RUNNABLE WITH RunnableLambda ─────────────────────────────────────

# You can insert plain Python functions into a chain using RunnableLambda.

from langchain_core.runnables import RunnableLambda

def add_context(inputs: dict) -> dict:
    """Pre-processing step: enrich inputs before they hit the prompt."""
    inputs["text"] = inputs["text"].strip().upper()
    return inputs

def post_process(output: str) -> str:
    """Post-processing step: clean the LLM output."""
    return output.strip().replace("\n\n", "\n")

if _HAS_KEY:
    preprocess = RunnableLambda(add_context)
    postprocess = RunnableLambda(post_process)

    full_chain = (
        preprocess
        | translation_prompt
        | llm
        | parser
        | postprocess
    )
    result = full_chain.invoke({
        "text": "  good morning  ",
        "source_lang": "English",
        "target_lang": "Spanish",
    })
    print(f"Full pipeline result: {result}\n")


# ─── WHY LANGCHAIN OVER RAW SDK ───────────────────────────────────────────────

# | Raw OpenAI SDK                  | LangChain                              |
# |---------------------------------|----------------------------------------|
# | Direct, explicit API calls      | Composable, declarative chains         |
# | You write prompt formatting     | PromptTemplate handles it              |
# | You parse response content      | StrOutputParser / others handle it     |
# | Tied to OpenAI                  | Swap models with one line change       |
# | Memory = DIY                    | RunnableWithMessageHistory built-in    |
# | Streaming = manual iteration    | .stream() works on any chain           |
# | No batching helpers             | .batch() with concurrency built-in     |
#
# Use raw SDK when: simple scripts, tight control, minimal dependencies.
# Use LangChain when: building agents, RAG, multi-step pipelines, need memory.


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1 — BUILD YOUR OWN CHAIN
#   Create a chain that:
#     1. Takes a {language} and a {code_snippet} as input.
#     2. Uses a system prompt: "You are a senior code reviewer."
#     3. Asks the LLM to review the code and suggest one improvement.
#   Invoke it with a Python snippet of your choice and print the result.

# Exercise 2 — BATCH PROCESSING
#   Use the sentiment chain from the lesson (or build your own) to classify
#   5 product reviews in a single .batch() call. Print each review (truncated
#   to 40 chars) alongside its sentiment label.

# Exercise 3 — STREAMING WORD COUNT
#   Build a chain that streams a short story (3-4 sentences) about a topic
#   you choose. As chunks stream in, accumulate them. After streaming finishes,
#   print the total word count of the complete response.
