# Lesson 5.4 — Streaming AI Responses: StreamingResponse + SSE + LangChain .stream()
# CONCEPT: Stream tokens to the client as they're generated instead of waiting for the full response
# KOTLIN EQUIVALENT: Spring WebFlux Flux<String> with text/event-stream content type
# PHP EQUIVALENT: Laravel Octane streaming, response()->stream(), or Swoole push

# ─── WHY STREAMING? ───────────────────────────────────────────────────────────
# Without streaming:
#   Client waits 3-10 seconds → gets full response at once → bad UX
#
# With streaming:
#   Client sees tokens appear word-by-word in ~100ms → feels instant → great UX
#
# This is how ChatGPT, Claude.ai, and Copilot work.
#
# Kotlin: Spring WebFlux returns Flux<String> with MediaType.TEXT_EVENT_STREAM_VALUE
# Laravel: response()->stream(function() { echo "data: token\n\n"; flush(); })

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# ─── MODELS ───────────────────────────────────────────────────────────────────

class StreamChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None
    system_prompt: str = Field(
        default="You are a helpful assistant. Be clear and concise.",
        description="System instruction for the AI"
    )

# ─── LIFESPAN ─────────────────────────────────────────────────────────────────

llm: "ChatOpenAI | None" = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm
    if LANGCHAIN_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, streaming=True)
        print("Streaming LLM initialized.")
    else:
        print("Running in mock streaming mode.")
    yield
    llm = None

app = FastAPI(title="Streaming AI API", version="1.0.0", lifespan=lifespan)

# ─── SERVER-SENT EVENTS (SSE) FORMAT ─────────────────────────────────────────
# SSE is a simple protocol for server-to-client streaming over HTTP.
#
# Format of each event:
#   data: {your payload here}\n\n
#
# The \n\n (double newline) marks the end of one event.
# The client's EventSource API fires an "message" event for each one.
#
# Why SSE over WebSockets?
#   - Simpler: one-direction (server → client), no handshake
#   - Works over standard HTTP/1.1 — no special server config
#   - Automatic reconnect built into browser EventSource API
#
# Kotlin: SseEmitter or Flux<ServerSentEvent<String>> in Spring WebFlux
# Laravel: No built-in SSE support; needs Swoole or Laravel Octane

def _sse_event(data: str | dict, event: str = "message") -> str:
    """
    Format a single SSE event.

    Output: "event: message\ndata: hello world\n\n"

    Kotlin: ServerSentEvent.builder().event("message").data("hello").build()
    """
    payload = json.dumps(data) if isinstance(data, dict) else data
    return f"event: {event}\ndata: {payload}\n\n"

def _sse_done() -> str:
    """Signal the end of the stream."""
    return _sse_event("[DONE]", event="done")

# ─── MOCK STREAMING (no LLM needed) ──────────────────────────────────────────

async def _mock_stream(message: str) -> AsyncGenerator[str, None]:
    """
    Simulates token streaming without an LLM.
    Yields tokens one word at a time with a small delay.
    """
    response_words = f"[MOCK STREAM] You asked: '{message}'. This is a simulated streaming response.".split()
    for word in response_words:
        yield _sse_event({"token": word + " "})
        await asyncio.sleep(0.05)
    yield _sse_done()

# ─── REAL STREAMING WITH LANGCHAIN ───────────────────────────────────────────

async def _langchain_stream(
    message: str,
    system_prompt: str,
    history: list | None = None,
) -> AsyncGenerator[str, None]:
    """
    Streams tokens from LangChain ChatOpenAI.

    LangChain's .astream() returns an async generator of AIMessageChunk objects.
    Each chunk has a .content attribute with a partial token string.

    Kotlin equivalent:
        chatClient.stream(messages)
            .map { chunk -> "data: ${chunk.content}\n\n" }
            .collect(...)
    """
    messages = [SystemMessage(content=system_prompt)]
    if history:
        messages.extend(history)
    messages.append(HumanMessage(content=message))

    full_response = []

    try:
        # .astream() is the async streaming version of .ainvoke()
        async for chunk in llm.astream(messages):
            token = chunk.content
            if token:
                full_response.append(token)
                # Each SSE event carries one token chunk
                yield _sse_event({"token": token})

        # Send the complete response as a final event (useful for clients to confirm)
        complete = "".join(full_response)
        yield _sse_event({"complete": complete, "token_count": len(complete.split())}, event="complete")

    except Exception as e:
        yield _sse_event({"error": str(e)}, event="error")

    finally:
        yield _sse_done()

# ─── STREAMING ENDPOINT ───────────────────────────────────────────────────────

@app.post("/chat/stream", tags=["Streaming"])
async def stream_chat(req: StreamChatRequest):
    """
    Stream AI response tokens as Server-Sent Events.

    Client receives a stream of events like:
        event: message
        data: {"token": "Hello"}

        event: message
        data: {"token": " world"}

        event: complete
        data: {"complete": "Hello world", "token_count": 2}

        event: done
        data: [DONE]

    How to test with curl:
        curl -N -X POST http://localhost:8003/chat/stream \\
             -H "Content-Type: application/json" \\
             -d '{"message": "Tell me about Python in 3 sentences"}'

    How to test in browser (JavaScript):
        const response = await fetch('/chat/stream', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: 'Hello!'})
        });
        const reader = response.body.getReader();
        // Read chunks and parse SSE events

    Kotlin equivalent:
        @GetMapping(value = ["/chat/stream"], produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
        fun streamChat(@RequestBody req: ChatRequest): Flux<String> = ...

    Laravel equivalent:
        return response()->stream(function () use ($message) {
            foreach ($tokens as $token) {
                echo "data: $token\n\n";
                ob_flush(); flush();
            }
        }, 200, ['Content-Type' => 'text/event-stream']);
    """
    # Choose streaming generator
    if llm is not None:
        generator = _langchain_stream(req.message, req.system_prompt)
    else:
        generator = _mock_stream(req.message)

    # StreamingResponse wraps an async generator and streams its output
    # media_type "text/event-stream" tells the browser this is SSE
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering if behind a proxy
        },
    )

# ─── NON-STREAMING ENDPOINT (for comparison) ─────────────────────────────────

@app.post("/chat", tags=["Non-Streaming"])
async def chat_non_streaming(req: StreamChatRequest):
    """
    Non-streaming endpoint for comparison.
    Client waits for the full response before getting anything.
    """
    if llm is None:
        return {"reply": f"[MOCK] You said: {req.message}", "streaming": False}

    messages = [
        SystemMessage(content=req.system_prompt),
        HumanMessage(content=req.message),
    ]
    response = await llm.ainvoke(messages)
    return {"reply": response.content, "streaming": False}

# ─── PLAIN TEXT STREAMING DEMO ────────────────────────────────────────────────
# Sometimes you want to stream plain text, not JSON events.
# This is simpler but gives clients less structure.

@app.get("/stream/plain", tags=["Streaming"])
async def stream_plain_text():
    """
    Demo: stream plain text chunks.
    Not SSE format — just raw bytes.
    """
    async def generate():
        words = "The quick brown fox jumps over the lazy dog".split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.1)

    return StreamingResponse(generate(), media_type="text/plain")

# ─── HEALTH ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "llm_ready": llm is not None, "streaming": True}

# ─── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("Streaming API running at http://localhost:8003")
    print("Test: curl -N -X POST http://localhost:8003/chat/stream -H 'Content-Type: application/json' -d '{\"message\": \"Hello\"}'")
    uvicorn.run("lesson_5_4_streaming:app", host="0.0.0.0", port=8003, reload=True)

# ─── EXERCISES ────────────────────────────────────────────────────────────────
# EXERCISE 1:
#   Add a `delay_ms: int = 0` field to StreamChatRequest.
#   In the mock stream generator, use this value as the delay between tokens
#   (instead of the hardcoded 0.05). This lets callers control the speed of the mock.
#
# EXERCISE 2:
#   Add an SSE event type "thinking" that fires before the first token:
#       event: thinking
#       data: {"status": "generating response..."}
#   Yield this event first in both _mock_stream and _langchain_stream,
#   then yield the token events as normal.
#
# EXERCISE 3:
#   Create a GET /stream/countdown/{n} endpoint that streams a countdown
#   from n to 0 as SSE events, one number per second:
#       event: message
#       data: {"count": 5}
#       ... (1 second delay)
#       event: message
#       data: {"count": 4}
#       ...
#       event: done
#       data: [DONE]
#   Test with: curl -N http://localhost:8003/stream/countdown/5
