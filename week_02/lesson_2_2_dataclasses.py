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
        
# In Python, empty string "" is falsy:
#   bool("")    # False
#   bool("Ali") # True

#   not ""      # True  ← empty
#   not "Ali"   # False ← not empty

#   So if not v.strip() means "if the string is empty after trimming whitespace, raise an error."

    # Valid data
    c = Customer(name="Ali", age=30, email="ali@example.com", tags=["vip"])
    print(c)
    print(c.model_dump())            # convert to dict
    print(c.model_dump_json())       # convert to JSON string

    # Parse from dict (like JSON deserialization)
    data = {"name": "Bob", "age": 25, "email": "bob@test.com"}
    c2 = Customer.model_validate(data) # its equivalent to object mapper in java and kotlin
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

@dataclass
class Product:
    name : str
    price : float
    quantity : int = 0

    def total_value(self) -> float:
        return self.price * self.quantity
    
    def is_in_stock(self) -> bool:
        if (self.quantity < 0):
            raise ValueError("Quantity cannot be less than 0")
        elif(self.quantity > 0):
            return True
        else:
            return False

# Exercise 2:
#   Create a Pydantic model `OrderItem` with: product_name (str), quantity (int),
#   unit_price (float). Add a validator that ensures quantity > 0.
#   Add a @property `subtotal` that returns quantity * unit_price.
#   (In Pydantic v2, use @computed_field instead of @property for serialization.)

class OrderItem(BaseModel):
    product_name: str
    quantity: int
    unit_price: float

    @field_validator("quantity")
    @classmethod
    def quantity_is_not_zero(cls, v:int) -> bool:
        if v <= 0:
            raise ValueError("Quantity cannot be less than 0")
        return v
    
    @property
    def subtotal(self)-> float:
        subtotal = self.quantity * self.unit_price
        return subtotal

# Exercise 3:
#   Create a Pydantic model `APIResponse` with: success (bool), data (Optional[dict]),
#   error (Optional[str]). Add a model validator that ensures: if success is False,
#   error must not be None.

class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

    @model_validator(mode='after')
    def check_success(self):
        if (self.success is False and self.error is None):
            raise ValueError("error must be set when success is False")
        return self


#  The pattern is:
#   - Field rule (only needs one field) → @field_validator
#   - Cross-field rule (needs two or more fields) → @model_validator

#   Don't add a @model_validator just for the sake of it. If every rule is single-field, use only @field_validator. If you have a cross-field rule, add @model_validator for that
#   specific check.

# Almost always use mode='after' — your fields are properly typed and you can access them normally via self. Use mode='before' only if you need to manipulate the raw input data
#   before Pydantic touches it.

# class Order(BaseModel):
#       quantity: int
#       price: float

#       @model_validator(mode='before')
#       @classmethod
#       def check_before(cls, data):
#           print(data)   # {'quantity': '2', 'price': '10.5'} ← still strings from JSON
#           return data

#       @model_validator(mode='after')
#       def check_after(self):
#           print(self.quantity)   # 2 ← already converted to int
#           return self


# Exercise 1 - Product
p1 = Product("Laptop", 1200.0, 3)
print(p1.total_value())   # 3600.0
print(p1.is_in_stock())   # True

p2 = Product("Mouse", 25.0, 0)
print(p2.total_value())   # 0.0
print(p2.is_in_stock())   # False

# Exercise 2 - OrderItem
item1 = OrderItem(product_name="Keyboard", quantity=2, unit_price=80.0)
print(item1.subtotal)     # 160.0

try:
    item2 = OrderItem(product_name="Monitor", quantity=0, unit_price=350.0)
except Exception as e:
    print(e)              # quantity must be greater than 0

try:
    item3 = OrderItem(product_name="Monitor", quantity=-1, unit_price=350.0)
except Exception as e:
    print(e)              # quantity must be greater than 0

# Exercise 3 - APIResponse
r1 = APIResponse(success=True, data={"user": "Ali"}, error=None)
print(r1)                 # success=True, data filled, no error

r2 = APIResponse(success=False, data=None, error="Not found")
print(r2)                 # valid — has error message

try:
    r3 = APIResponse(success=False, data=None, error=None)
except Exception as e:
    print(e)              # error must be set when success is False