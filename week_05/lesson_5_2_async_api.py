# Lesson 5.2 — Async FastAPI: async/await, Depends(), BackgroundTasks, Lifespan
# CONCEPT: Non-blocking I/O, dependency injection, background work, startup/shutdown
# KOTLIN EQUIVALENT: @Async, @Autowired, @Bean, ApplicationRunner, coroutines
# PHP EQUIVALENT: Service container, app()->make(), queued jobs, AppServiceProvider::boot()

# ─── WHY ASYNC IN FASTAPI ────────────────────────────────────────────────────
# FastAPI runs on an async event loop (uvicorn + asyncio).
# Rule of thumb:
#   - `async def` — for routes that do I/O (DB, HTTP, file reads) → event loop handles it
#   - `def`       — for CPU-bound or sync library code → FastAPI runs it in a thread pool
#
# Kotlin equivalent: suspend fun in coroutines
# Laravel equivalent: Laravel has sync request handling by default; async = queued jobs

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Header
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── LIFESPAN: STARTUP / SHUTDOWN ────────────────────────────────────────────
# The lifespan context manager runs once at startup and once at shutdown.
# Use it to: open DB connections, load ML models, initialize HTTP clients.
#
# Kotlin: @PostConstruct / @PreDestroy, or ApplicationRunner bean
# Laravel: AppServiceProvider::boot() for startup; no built-in shutdown hook

http_client: httpx.AsyncClient | None = None  # Shared across all requests

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──
    global http_client
    logger.info("Starting up: creating shared HTTP client...")
    http_client = httpx.AsyncClient(timeout=10.0)
    logger.info("HTTP client ready.")

    yield  # <── app runs here

    # ── SHUTDOWN ──
    logger.info("Shutting down: closing HTTP client...")
    await http_client.aclose()
    logger.info("Cleanup done.")

app = FastAPI(title="Async API Demo", lifespan=lifespan)

# ─── DEPENDENCY INJECTION WITH Depends() ─────────────────────────────────────
# Depends() tells FastAPI: "call this function and inject its return value".
# It's like Spring's @Autowired or Laravel's service container.
#
# Benefits:
#   - Reusable logic (auth, DB sessions, rate limiting)
#   - Easy to test — swap dependencies in tests
#   - Dependencies can depend on other dependencies (nested)

# ── Simple dependency: extract + validate API key from header ──
API_KEY = "secret-dev-key"  # In real life: read from env

def get_api_key(x_api_key: Annotated[str | None, Header()] = None) -> str:
    """
    Dependency that validates the X-Api-Key header.

    Kotlin: HandlerInterceptor or @PreAuthorize
    Laravel: auth middleware, $request->bearerToken()
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key

# ── Service-style dependency: a fake "database" service ──
class UserService:
    """Simulates a database-backed service.

    Kotlin: @Service class UserService @Autowired constructor(val repo: UserRepository)
    Laravel: class UserService injected via constructor in controller
    """
    def __init__(self):
        self._store: dict[int, dict] = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
            2: {"id": 2, "name": "Bob",   "email": "bob@example.com"},
        }

    async def find_by_id(self, user_id: int) -> dict | None:
        await asyncio.sleep(0.01)  # Simulate async DB latency
        return self._store.get(user_id)

    async def list_all(self) -> list[dict]:
        await asyncio.sleep(0.01)
        return list(self._store.values())

# FastAPI calls this function to get a UserService instance per request.
# For a real DB: open session here, yield, close in finally.
def get_user_service() -> UserService:
    """
    Kotlin: @Bean fun userService(): UserService = UserService()
    Laravel: $this->app->bind(UserService::class, fn() => new UserService())
    """
    return UserService()

# Type alias makes route signatures cleaner (Python 3.9+ style)
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ApiKeyDep = Annotated[str, Depends(get_api_key)]

# ─── ASYNC ROUTE WITH DEPENDENCY INJECTION ───────────────────────────────────

@app.get("/users", tags=["Users"])
async def list_users(service: UserServiceDep):
    """
    async def = non-blocking. The event loop can handle other requests
    while this one awaits the DB call.

    Kotlin: suspend fun listUsers(service: UserService): List<User>
    """
    users = await service.list_all()
    return {"users": users, "count": len(users)}

@app.get("/users/{user_id}", tags=["Users"])
async def get_user(user_id: int, service: UserServiceDep):
    user = await service.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ─── PROTECTED ROUTE (stacked dependencies) ───────────────────────────────────
# Multiple Depends() can be combined — they all run before the handler.
# Kotlin: @PreAuthorize + @Valid together on one method
# Laravel: route middleware + Form Request

@app.delete("/users/{user_id}", tags=["Users"])
async def delete_user(
    user_id: int,
    service: UserServiceDep,
    _api_key: ApiKeyDep,  # Underscore = we don't use the value, just the side-effect (auth check)
):
    """Only callable with a valid X-Api-Key header."""
    user = await service.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": user_id, "message": "User deleted"}

# ─── BACKGROUND TASKS ────────────────────────────────────────────────────────
# BackgroundTasks = fire-and-forget after the response is sent.
# Good for: audit logs, sending emails, analytics events.
# NOT good for: long jobs (use Celery/RQ for those).
#
# Kotlin: @Async void sendEmail(...) called after the response
# Laravel: dispatch(new SendWelcomeEmail($user)) — queued job

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

def _send_email_sync(to: str, subject: str, body: str):
    """Simulates sending an email (sync, runs in thread pool)."""
    time.sleep(0.5)  # Simulate SMTP latency
    logger.info(f"[EMAIL] To: {to} | Subject: {subject}")

async def _send_email_async(to: str, subject: str, body: str):
    """Async version — awaits a coroutine."""
    await asyncio.sleep(0.5)
    logger.info(f"[EMAIL ASYNC] To: {to} | Subject: {subject}")

@app.post("/send-email", tags=["Background"])
async def send_email(req: EmailRequest, background_tasks: BackgroundTasks):
    """
    Response returns immediately. Email is sent in background.

    You can add both sync and async functions to BackgroundTasks.
    FastAPI handles the event loop bridging for sync functions automatically.
    """
    # Add to background queue — runs after response is sent
    background_tasks.add_task(_send_email_async, req.to, req.subject, req.body)

    return {"status": "queued", "message": f"Email to {req.to} is being sent"}

# ─── ASYNC HTTP CALL (using shared client) ────────────────────────────────────
# Reuse the http_client initialized in lifespan — don't create a new one per request!
# Kotlin: WebClient as a @Bean, injected into services
# Laravel: Http::get() — but creates a new connection each time

@app.get("/proxy/joke", tags=["Demo"])
async def fetch_joke():
    """Fetches a joke from a public API — demonstrates async HTTP call."""
    if http_client is None:
        raise HTTPException(status_code=503, detail="HTTP client not initialized")
    try:
        resp = await http_client.get("https://official-joke-api.appspot.com/random_joke")
        resp.raise_for_status()
        joke = resp.json()
        return {"setup": joke["setup"], "punchline": joke["punchline"]}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

# ─── SYNC VS ASYNC DEMO ───────────────────────────────────────────────────────
# FastAPI can handle both. sync def routes run in a thread pool automatically.

@app.get("/sync-demo", tags=["Demo"])
def sync_route():
    """
    Regular def — FastAPI runs this in a thread pool.
    Use this when calling sync libraries (e.g., psycopg2, old ORMs).
    """
    time.sleep(0.1)  # Blocking — but that's OK here (thread pool)
    return {"type": "sync", "message": "I ran in a thread pool"}

@app.get("/async-demo", tags=["Demo"])
async def async_route():
    """
    async def — FastAPI runs this on the event loop.
    Use this when calling async libraries (httpx, asyncpg, motor).
    """
    await asyncio.sleep(0.1)  # Non-blocking — event loop can handle others
    return {"type": "async", "message": "I ran on the event loop"}

# ─── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lesson_5_2_async_api:app", host="0.0.0.0", port=8001, reload=True)

# ─── EXERCISES ────────────────────────────────────────────────────────────────
# EXERCISE 1:
#   Create a dependency `get_pagination(page: int = 1, limit: int = 10)`
#   that returns a dict {"offset": (page-1)*limit, "limit": limit}.
#   Apply it to GET /users using Depends() so the handler receives
#   pagination info without repeating the page/limit parameters.
#
# EXERCISE 2:
#   Add a background task to the POST /users endpoint (from lesson 5.1):
#   after creating a user, fire a background task that logs:
#   "Welcome email sent to {email}" after a 1-second simulated delay.
#   The route should still return the created user immediately.
#
# EXERCISE 3:
#   Add a GET /users/{user_id}/profile endpoint that makes TWO async HTTP
#   calls concurrently (using asyncio.gather):
#   - Fetch from https://jsonplaceholder.typicode.com/users/{user_id}
#   - Fetch from https://jsonplaceholder.typicode.com/posts?userId={user_id}
#   Return both results in a single response dict.
#   Hint: results = await asyncio.gather(call1, call2)
