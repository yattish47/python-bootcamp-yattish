# Lesson 5.1 — FastAPI Basics
# CONCEPT: Decorator-based HTTP routing with automatic request validation and docs generation
# KOTLIN EQUIVALENT: @GetMapping / @PostMapping / @RequestBody / @PathVariable / ResponseEntity
# PHP EQUIVALENT: Route::get() / Route::post() / Form Requests / response()->json()

# ─── SETUP ───────────────────────────────────────────────────────────────────
# pip install fastapi uvicorn
# Run this app: uvicorn lesson_5_1_fastapi_basics:app --reload
# Auto-docs:    http://localhost:8000/docs

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uvicorn

# ─── THE APP INSTANCE ────────────────────────────────────────────────────────
# FastAPI() is like creating a Spring Boot @SpringBootApplication
# or a Laravel Application instance.
app = FastAPI(
    title="User API",
    description="Demo CRUD API for Lesson 5.1",
    version="1.0.0",
)

# In-memory "database" — a plain dict (like a Map<Int, User> in Kotlin)
users_db: dict[int, dict] = {}
next_id = 1  # Auto-increment counter

# ─── PYDANTIC MODELS ─────────────────────────────────────────────────────────
# Pydantic BaseModel = Kotlin data class + @Valid annotations
# FastAPI uses these for automatic request parsing AND response serialization.

class CreateUserRequest(BaseModel):
    """Validated request body for creating a user.

    Kotlin equivalent:
        data class CreateUserRequest(
            @field:NotBlank val name: String,
            @field:Email val email: String,
            val age: Int = 0
        )

    Laravel equivalent: Form Request with rules()
    """
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: str = Field(..., description="Email address")
    age: int = Field(default=0, ge=0, le=150, description="Age in years")

class UpdateUserRequest(BaseModel):
    """Partial update — all fields optional (like PATCH in REST)."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)

class UserResponse(BaseModel):
    """What we return to the client — never expose internal fields.

    Kotlin: separate DTO class annotated with @JsonIgnoreProperties
    Laravel: API Resource (UserResource)
    """
    id: int
    name: str
    email: str
    age: int

# ─── GET — LIST ALL USERS (query parameters) ─────────────────────────────────
# Query params are function arguments with defaults.
# Kotlin: @GetMapping + @RequestParam(defaultValue="1") page: Int
# Laravel: $request->input('page', 1)

@app.get("/users", response_model=list[UserResponse], tags=["Users"])
def get_users(page: int = 1, limit: int = 10, name_filter: Optional[str] = None):
    """List users with optional pagination and name filter.

    URL examples:
        GET /users
        GET /users?page=2&limit=5
        GET /users?name_filter=alice
    """
    all_users = list(users_db.values())

    # Optional filter
    if name_filter:
        all_users = [u for u in all_users if name_filter.lower() in u["name"].lower()]

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    return all_users[start:end]

# ─── GET — SINGLE USER (path parameter) ──────────────────────────────────────
# Path params are declared in the route AND in the function signature.
# Kotlin: @GetMapping("/users/{id}") + @PathVariable id: Long
# Laravel: Route::get('/users/{id}', ...) + $id in method signature

@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int):
    """Get a single user by ID.

    FastAPI automatically converts the path segment to int.
    If user_id is not a valid int, FastAPI returns 422 Unprocessable Entity.
    """
    if user_id not in users_db:
        # HTTPException = @ResponseStatus(HttpStatus.NOT_FOUND) in Spring
        # Laravel: abort(404, 'User not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found",
        )
    return users_db[user_id]

# ─── POST — CREATE USER (request body) ───────────────────────────────────────
# The Pydantic model is automatically deserialized + validated from JSON body.
# Invalid body → FastAPI returns 422 with field-level error details.
# Kotlin: @PostMapping + @RequestBody @Valid CreateUserRequest
# Laravel: Route::post() + validated() from Form Request

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(body: CreateUserRequest):
    """Create a new user.

    FastAPI does all of this automatically:
    - Parse JSON body
    - Validate all fields (type, min_length, ge, le, etc.)
    - Return 422 with error details if validation fails
    - Serialize UserResponse back to JSON
    """
    global next_id

    # Check duplicate email (simple in-memory check)
    for existing in users_db.values():
        if existing["email"] == body.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{body.email}' already in use",
            )

    user = {"id": next_id, "name": body.name, "email": body.email, "age": body.age}
    users_db[next_id] = user
    next_id += 1
    return user

# ─── PUT — FULL UPDATE ────────────────────────────────────────────────────────

@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: int, body: CreateUserRequest):
    """Replace a user completely (PUT semantics)."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    users_db[user_id].update({"name": body.name, "email": body.email, "age": body.age})
    return users_db[user_id]

# ─── PATCH — PARTIAL UPDATE ───────────────────────────────────────────────────

@app.patch("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def patch_user(user_id: int, body: UpdateUserRequest):
    """Update only provided fields (PATCH semantics).

    body.model_dump(exclude_unset=True) returns only the fields the client sent.
    Kotlin: check each field for null manually
    Laravel: $request->only(['name', 'email'])
    """
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    updates = body.model_dump(exclude_unset=True)  # Only provided fields
    users_db[user_id].update(updates)
    return users_db[user_id]

# ─── DELETE ───────────────────────────────────────────────────────────────────

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(user_id: int):
    """Delete a user. Returns 204 No Content on success."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    # 204 = no return value needed

# ─── ROOT + HEALTH CHECK ──────────────────────────────────────────────────────

@app.get("/", tags=["Meta"])
def root():
    return {"message": "User API is running", "docs": "/docs"}

@app.get("/health", tags=["Meta"])
def health():
    return {"status": "ok", "user_count": len(users_db)}

# ─── SEED DATA (for easy demo) ────────────────────────────────────────────────

def _seed():
    """Pre-populate a few users so /docs is useful immediately."""
    global next_id
    seeds = [
        {"name": "Alice Tan", "email": "alice@example.com", "age": 30},
        {"name": "Bob Lim", "email": "bob@example.com", "age": 25},
        {"name": "Carol Wong", "email": "carol@example.com", "age": 35},
    ]
    for s in seeds:
        users_db[next_id] = {"id": next_id, **s}
        next_id += 1

_seed()

# ─── RUN DIRECTLY ────────────────────────────────────────────────────────────
# python lesson_5_1_fastapi_basics.py
# OR: uvicorn lesson_5_1_fastapi_basics:app --reload

if __name__ == "__main__":
    print("Starting User API on http://localhost:8000")
    print("Swagger UI: http://localhost:8000/docs")
    uvicorn.run("lesson_5_1_fastapi_basics:app", host="0.0.0.0", port=8000, reload=True)

# ─── EXERCISES ────────────────────────────────────────────────────────────────
# EXERCISE 1:
#   Add a GET /users/search endpoint that accepts a query parameter `email`
#   and returns users whose email contains the search string (case-insensitive).
#   Return 200 with an empty list if nothing found (not 404).
#
# EXERCISE 2:
#   Add an `active: bool = True` field to CreateUserRequest and UserResponse.
#   Add a query parameter `active_only: bool = False` to GET /users that
#   filters out inactive users when set to True.
#
# EXERCISE 3:
#   Create a GET /users/{user_id}/summary endpoint that returns a plain string
#   (not JSON) in the format: "Alice Tan (age 30) — alice@example.com"
#   Hint: return a Response(content=..., media_type="text/plain") or just a str.
