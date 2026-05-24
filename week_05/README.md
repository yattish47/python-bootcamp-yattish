# Week 5 — FastAPI AI Backend

## Setup

```bash
pip install fastapi uvicorn httpx langchain langchain-openai python-dotenv
```

Create a `.env` file in `week_05/`:
```
OPENAI_API_KEY=sk-...
```

## How to Run the Project

```bash
# From the python_learning root:
uvicorn project.chat_api.main:app --reload --app-dir week_05

# Or from inside week_05/:
uvicorn project.chat_api.main:app --reload
```

API docs auto-generated at: http://localhost:8000/docs

---

## Lessons

| File | Topic |
|---|---|
| `lesson_5_1_fastapi_basics.py` | Routes, path/query params, Pydantic models, CRUD example |
| `lesson_5_2_async_api.py` | async/await, Depends(), BackgroundTasks, lifespan |
| `lesson_5_3_ai_endpoint.py` | LangChain wired to FastAPI, session history |
| `lesson_5_4_streaming.py` | StreamingResponse, SSE, LangChain .stream() |

---

## Framework Comparison

### FastAPI vs Spring Boot (Kotlin)

| Concept | Spring Boot | FastAPI |
|---|---|---|
| Route decorator | `@GetMapping("/users")` | `@app.get("/users")` |
| Path variable | `@PathVariable id: Long` | `user_id: int` in path param |
| Request body | `@RequestBody dto: CreateUserDto` | `body: CreateUserRequest` (Pydantic) |
| Validation | `@Valid`, `javax.validation` | Pydantic auto-validates |
| Dependency injection | `@Autowired`, `@Bean` | `Depends()` |
| Response wrapper | `ResponseEntity<T>` | `response_model=UserResponse` |
| Server | Embedded Tomcat | uvicorn |
| Async | `@Async`, Coroutines | `async def` natively |

### FastAPI vs Laravel/PHP

| Concept | Laravel | FastAPI |
|---|---|---|
| Route definition | `Route::get('/users', ...)` | `@app.get("/users")` |
| POST route | `Route::post('/users', ...)` | `@app.post("/users")` |
| Request validation | Form Request classes | Pydantic BaseModel |
| JSON response | `response()->json($data)` | Return dict or Pydantic model |
| Middleware | `$middleware` array | FastAPI middleware / Depends |
| Service container | `app()->make(Service::class)` | `Depends(get_service)` |
| Background jobs | Queued jobs, `dispatch()` | `BackgroundTasks` |

---

## Key Insight

FastAPI is what you'd get if Spring Boot and Flask had a baby:
- Decorator-based routing (Flask style)
- Pydantic validation is like Spring's `@Valid` + Kotlin data classes — but auto-wired
- `Depends()` is a lightweight Spring `@Autowired` / Laravel service container
- uvicorn is the embedded Tomcat equivalent — ships with the app
