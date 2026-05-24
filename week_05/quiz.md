# Week 5 Quiz — FastAPI AI Backend

Test your understanding of FastAPI, Pydantic, async Python, and streaming.

---

## Questions

**Q1.** In FastAPI, what decorator do you use to define a POST endpoint at `/users`?

<details><summary>Answer</summary>

```python
@app.post("/users")
def create_user(body: CreateUserRequest):
    ...
```
`@app.post()` maps to Spring's `@PostMapping` or Laravel's `Route::post()`.
</details>

---

**Q2.** A route function takes `def get_user(user_id: int, name: str = None)`.
Which of `user_id` and `name` is a path parameter vs a query parameter?
What URL would call this with user_id=5 and name="alice"?

<details><summary>Answer</summary>

- `user_id` is a **path parameter** — it must appear in the route decorator: `@app.get("/users/{user_id}")`
- `name` is a **query parameter** — it has a default value and is not in the path
- URL: `GET /users/5?name=alice`

Kotlin equivalent: `@PathVariable user_id: Int` vs `@RequestParam(required=false) name: String?`
</details>

---

**Q3.** What does `response_model=UserResponse` do on a FastAPI endpoint?

<details><summary>Answer</summary>

It tells FastAPI to:
1. Validate the return value against the `UserResponse` Pydantic model
2. Serialize the response to JSON using that model's fields only (excludes any extra fields)
3. Generate the correct response schema in the Swagger UI (`/docs`)

Kotlin equivalent: returning `ResponseEntity<UserResponse>` — Spring serializes via Jackson.
Laravel equivalent: returning a `UserResource` which defines which fields to expose.
</details>

---

**Q4.** When should you use `async def` vs `def` for FastAPI route handlers?

<details><summary>Answer</summary>

- **`async def`** — when your route does I/O-bound work using `await`: calling async DB drivers, httpx, async Redis, etc. FastAPI runs it on the event loop.
- **`def`** — when calling sync/blocking libraries (psycopg2, requests, old ORMs). FastAPI runs it in a thread pool automatically, so it won't block the event loop.

**Never** use `async def` with blocking code (like `time.sleep()` or the `requests` library) — that will block the entire event loop.
</details>

---

**Q5.** What is `Depends()` in FastAPI and what problem does it solve?

<details><summary>Answer</summary>

`Depends()` is FastAPI's dependency injection system. It tells FastAPI to call a function and inject its return value into your route handler.

```python
def get_db() -> Database:
    return Database(url=DATABASE_URL)

@app.get("/users")
async def list_users(db: Database = Depends(get_db)):
    return await db.fetch_all("SELECT * FROM users")
```

It solves:
- **Reusability**: auth checks, DB sessions, pagination — write once, inject everywhere
- **Testability**: swap dependencies in tests without changing route code
- **Separation of concerns**: routes focus on business logic, not infrastructure setup

Kotlin equivalent: Spring `@Autowired` / constructor injection.
Laravel equivalent: `app()->make(UserService::class)` or constructor injection in controllers.
</details>

---

**Q6.** What is `BackgroundTasks` and when should you NOT use it?

<details><summary>Answer</summary>

`BackgroundTasks` lets you schedule work to run after the HTTP response is sent:

```python
@app.post("/users")
async def create_user(body: CreateUserRequest, bg: BackgroundTasks):
    user = await db.create(body)
    bg.add_task(send_welcome_email, user.email)  # Fires after response
    return user
```

**Do NOT use it for:**
- Long-running tasks (> a few seconds) — the server is still "holding" that background task
- Tasks that must survive server restarts
- High-volume task queues

For those cases, use **Celery**, **RQ**, or a message queue (Kafka, RabbitMQ).

Kotlin equivalent: `@Async` void method called after the controller returns.
Laravel equivalent: `dispatch(new SendWelcomeEmail($user))` — but queued workers are more robust.
</details>

---

**Q7.** Explain the SSE (Server-Sent Events) format. What does each `\n\n` mean?

<details><summary>Answer</summary>

SSE is a simple text protocol for one-directional server-to-client streaming over HTTP.

Each event looks like:
```
event: message
data: {"token": "Hello"}

```

Rules:
- `event:` (optional) — event type; client can filter by type
- `data:` — the payload (can be any string, often JSON)
- `\n\n` — **double newline marks the end of one event**. This is the delimiter.

FastAPI:
```python
return StreamingResponse(generator(), media_type="text/event-stream")
```

Kotlin equivalent: `Flux<ServerSentEvent<String>>` with `MediaType.TEXT_EVENT_STREAM_VALUE`.
Laravel equivalent: Manual `echo "data: ...\n\n"; flush();` in a stream response.
</details>

---

**Q8.** What is the difference between LangChain's `.invoke()`, `.ainvoke()`, and `.astream()`?

<details><summary>Answer</summary>

| Method | Sync/Async | Returns | Use case |
|--------|-----------|---------|----------|
| `.invoke(input)` | Sync (blocking) | Full response | Scripts, tests, non-async contexts |
| `.ainvoke(input)` | Async | Full response (awaitable) | FastAPI `async def` routes, non-streaming |
| `.astream(input)` | Async | Async generator of chunks | FastAPI streaming endpoints |

```python
# Non-streaming
reply = await chain.ainvoke({"input": "Hello"})

# Streaming
async for chunk in chain.astream({"input": "Hello"}):
    print(chunk.content, end="", flush=True)
```

Always use `ainvoke` or `astream` inside `async def` FastAPI routes — never `invoke` (it blocks the event loop).
</details>
