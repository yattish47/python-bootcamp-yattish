# Lesson 2.2 — Dataclasses & Pydantic
# Python for AI Engineers | Week 2
#
# CONCEPT:
#   `dataclass` is Python's equivalent of Kotlin's `data class` — it auto-generates
#   __init__, __repr__, and __eq__ from your field declarations.
#
#   Pydantic goes further: it validates types at runtime and is the foundation
#   of FastAPI (Week 5). You'll use it constantly in AI projects.
#
# KOTLIN:  data class User(val name: String, val age: Int)
# PYTHON:  @dataclass class User: name: str; age: int
# PYDANTIC: class User(BaseModel): name: str; age: int  ← validates at runtime

from dataclasses import dataclass, field
from typing import Optional

# ─── DATACLASS ───────────────────────────────────────────────────────────────

@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


p1 = Point(0, 0)
p2 = Point(3, 4)
print(p1)                         # Point(x=0, y=0) — __repr__ auto-generated
print(p1 == Point(0, 0))         # True — __eq__ auto-generated
print(p1.distance_to(p2))        # 5.0


@dataclass
class UserProfile:
    name: str
    email: str
    age: int = 0                          # default value
    tags: list[str] = field(default_factory=list)  # mutable default needs field()
    bio: Optional[str] = None

    def is_adult(self) -> bool:
        return self.age >= 18


user = UserProfile(name="Ali", email="ali@example.com", age=30, tags=["python", "ai"])
print(user)
print(user.is_adult())


# ─── PYDANTIC ────────────────────────────────────────────────────────────────
# pip install pydantic   (included via openai or fastapi, but can install standalone)

try:
    from pydantic import BaseModel, EmailStr, field_validator, model_validator

    class Address(BaseModel):
        street: str
        city: str
        postcode: str

    class Customer(BaseModel):
        name: str
        age: int
        email: str
        address: Optional[Address] = None
        tags: list[str] = []

        @field_validator("age")
        @classmethod
        def age_must_be_positive(cls, v: int) -> int:
            if v < 0:
                raise ValueError("Age must be non-negative")
            return v

        @field_validator("name")
        @classmethod
        def name_must_not_be_empty(cls, v: str) -> str:
            if not v.strip():
                raise ValueError("Name cannot be empty")
            return v.strip()

    # Valid data
    c = Customer(name="Ali", age=30, email="ali@example.com", tags=["vip"])
    print(c)
    print(c.model_dump())            # convert to dict
    print(c.model_dump_json())       # convert to JSON string

    # Parse from dict (like JSON deserialization)
    data = {"name": "Bob", "age": 25, "email": "bob@test.com"}
    c2 = Customer.model_validate(data)
    print(c2.name)

    # This will raise a ValidationError
    try:
        bad = Customer(name="", age=-5, email="bad")
    except Exception as e:
        print(f"Validation error: {e}")

except ImportError:
    print("Run: pip install pydantic")
    print("Pydantic is installed automatically with 'openai' or 'fastapi'")


# ─── WHY PYDANTIC MATTERS FOR AI PROJECTS ────────────────────────────────────
#
# Pydantic is used everywhere in the AI stack:
#
# - FastAPI request/response bodies (Week 5)
# - LangChain tool schemas (Week 6)
# - OpenAI structured outputs
# - Validating LLM JSON responses
#
# Pattern you'll see constantly:
#
#   class ChatRequest(BaseModel):
#       message: str
#       session_id: str
#       max_tokens: int = 1000
#
#   class ChatResponse(BaseModel):
#       reply: str
#       model: str
#       tokens_used: int


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Create a @dataclass `Product` with: name (str), price (float), quantity (int = 0).
#   Add a method `total_value() -> float` that returns price * quantity.
#   Add a method `is_in_stock() -> bool`.

# Exercise 2:
#   Create a Pydantic model `OrderItem` with: product_name (str), quantity (int),
#   unit_price (float). Add a validator that ensures quantity > 0.
#   Add a @property `subtotal` that returns quantity * unit_price.
#   (In Pydantic v2, use @computed_field instead of @property for serialization.)

# Exercise 3:
#   Create a Pydantic model `APIResponse` with: success (bool), data (Optional[dict]),
#   error (Optional[str]). Add a model validator that ensures: if success is False,
#   error must not be None.
