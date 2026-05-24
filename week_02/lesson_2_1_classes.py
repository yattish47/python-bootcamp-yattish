# Lesson 2.1 — Classes
# Python for AI Engineers | Week 2
#
# CONCEPT:
#   Python classes use `self` (like PHP's `$this` or Kotlin's implicit `this`).
#   `__init__` is the constructor. Methods are just functions with `self` as the
#   first parameter. Python has no `public`/`private` keywords — prefix with `_`
#   to signal "don't use this outside the class" (convention, not enforced).
#
# KOTLIN:  class Dog(val name: String) { fun bark() = "Woof" }
# PHP:     class Dog { public string $name; function bark(): string { return "Woof"; } }
# PYTHON:  class Dog: def __init__(self, name: str): self.name = name

# ─── BASIC CLASS ─────────────────────────────────────────────────────────────

class BankAccount:
    # Class variable — shared by ALL instances (like Kotlin companion object val)
    bank_name: str = "PyBank"

    def __init__(self, owner: str, balance: float = 0.0):
        # Instance variables — unique to each object
        self.owner = owner
        self.balance = balance
        self._transaction_count = 0   # _ = "private by convention"

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self._transaction_count += 1

    def withdraw(self, amount: float) -> bool:
        if amount > self.balance:
            return False
        self.balance -= amount
        self._transaction_count += 1
        return True

    def get_summary(self) -> str:
        return f"{self.owner} | Balance: {self.balance:.2f} | Transactions: {self._transaction_count}"

    # __repr__ is what you see in the REPL / debugging (like Kotlin's toString)
    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self.balance})"

    # __str__ is for print() and str()
    def __str__(self) -> str:
        return self.get_summary()


account = BankAccount("Ali", 1000.0)
account.deposit(500)
account.withdraw(200)
print(account)             # Ali | Balance: 1300.00 | Transactions: 2
print(repr(account))       # BankAccount(owner='Ali', balance=1300.0)
print(BankAccount.bank_name)  # PyBank

# ─── @PROPERTY — COMPUTED ATTRIBUTES ─────────────────────────────────────────

# Like Kotlin's `val` with a custom getter
class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    @property
    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    @property
    def diameter(self) -> float:
        return self.radius * 2

    @diameter.setter           # allow setting: circle.diameter = 10
    def diameter(self, value: float):
        self.radius = value / 2


c = Circle(5)
print(f"Area: {c.area:.2f}")       # Area: 78.54
print(f"Diameter: {c.diameter}")   # Diameter: 10
c.diameter = 20                    # uses setter
print(f"Radius: {c.radius}")       # Radius: 10.0

# ─── INHERITANCE ─────────────────────────────────────────────────────────────

class Animal:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species

    def speak(self) -> str:
        return f"{self.name} makes a sound"

    def __str__(self) -> str:
        return f"{self.species} named {self.name}"


class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name, "Dog")   # like Kotlin's super() or PHP parent::__construct()
        self.breed = breed

    def speak(self) -> str:             # override — no keyword needed
        return f"{self.name} says: Woof!"

    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} says: Meow!"


dog = Dog("Rex", "Labrador")
cat = Cat("Whiskers", "Cat")

print(dog.speak())     # Rex says: Woof!
print(cat.speak())     # Whiskers says: Meow!
print(dog.fetch("ball"))
print(isinstance(dog, Animal))   # True — like Kotlin's `is` or PHP's `instanceof`

# ─── CLASS METHODS & STATIC METHODS ─────────────────────────────────────────

class User:
    _count = 0

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        User._count += 1

    @classmethod                       # like Kotlin companion object fun
    def from_dict(cls, data: dict) -> "User":
        return cls(data["name"], data["email"])

    @staticmethod                      # no access to cls or self
    def validate_email(email: str) -> bool:
        return "@" in email and "." in email

    @classmethod
    def count(cls) -> int:
        return cls._count


u1 = User("Ali", "ali@example.com")
u2 = User.from_dict({"name": "Bob", "email": "bob@example.com"})
print(User.count())                         # 2
print(User.validate_email("bad-email"))     # False


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Create a `Rectangle` class with `width` and `height`.
#   Add @property `area` and @property `perimeter`.
#   Add a `is_square` @property that returns True if width == height.

# Exercise 2:
#   Create a `Vehicle` base class with `make`, `model`, `year`.
#   Add a `description()` method returning "{year} {make} {model}".
#   Create a `Car(Vehicle)` subclass with an extra `num_doors` attribute.
#   Create an `ElectricCar(Car)` subclass with `battery_range_km`.
#   Override `description()` in ElectricCar to append " (Electric, Xkm range)".

# Exercise 3:
#   Add a `@classmethod from_string(cls, s: str)` to Rectangle
#   that parses "10x5" and returns Rectangle(width=10, height=5).
