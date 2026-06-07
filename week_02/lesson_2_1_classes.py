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
    
#     The !r in f"BankAccount(owner={self.owner!r})" just means "format this value using repr()" — so strings get quotes around them:
#   self.owner = "Ali"
#   f"{self.owner}"    # Ali
#   f"{self.owner!r}"  # 'Ali'   ← includes the quotes

    # __str__ is for print() and str()
    def __str__(self) -> str:
        return self.get_summary()
    

#      t = Transaction(250.0, "deposit")

#   # __str__ — what a user sees
#   print(t)
#   # DEPOSIT: RM250.00

#   # __repr__ — what a developer sees in logs/debugger
#   print(repr(t))
#   # Transaction(amount=250.0, type='deposit', timestamp=datetime.datetime(2026, 6, 7, 10, 23, 45))

#   # Inside a list — Python uses __repr__ automatically
#   history = [Transaction(250.0, "deposit"), Transaction(50.0, "withdrawal")]
#   print(history)
#   # [Transaction(amount=250.0, type='deposit', ...), Transaction(amount=50.0, type='withdrawal', ...)]

#   The key difference:
#   - A customer sees DEPOSIT: RM250.00 — clean, simple
#   - A developer debugging sees the full object with timestamp — enough to trace exactly what happened

#   Same object, two different audiences.


account = BankAccount("Ali", 1000.0)
account.deposit(500)
account.withdraw(200)
print(account)             # Ali | Balance: 1300.00 | Transactions: 2
print(repr(account))       # BankAccount(owner='Ali', balance=1300.0)
print(BankAccount.bank_name)  # PyBank


# acc = BankAccount("Yattish", 1000.0)

#   # 1. print() — calls __str__
#   print(acc)                        # Yattish's account: RM1000.00

#   # 2. f-string — calls __str__
#   message = f"Welcome! {acc}"
#   print(message)                    # Welcome! Yattish's account: RM1000.00

#   # 3. str() — calls __str__
#   text = str(acc)
#   print(text)                       # Yattish's account: RM1000.00

#   # 4. Inside a list — calls __repr__ (NOT __str__)
#   accounts = [acc]
#   print(accounts)                   # [BankAccount(owner='Yattish', balance=1000.0)]

#   # 5. repr() or in debugger — calls __repr__
#   print(repr(acc))                  # BankAccount(owner='Yattish', balance=1000.0)

#   Rule of thumb:
#   - print(obj) → __str__
#   - print([obj]) → __repr__ (Python uses repr inside containers)
#   - No __str__? Python falls back to __repr__


# Quick rule:
#   - Simple data classes → always add them (or use @dataclass which generates __repr__ automatically)
#   - Internal/utility classes you never print → skip it, no point

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

# @property creates a property object named diameter. That object can hold up to 3 parts:

#   @property
#   def diameter(self):        # the getter — attached to the property object
#       return self.radius * 2

#   @diameter.setter
#   def diameter(self, value): # the setter — attached to the SAME property object
#       self.radius = value / 2

#   @diameter.setter means "take the existing diameter property and attach a setter to it." Same name, same object, just adding a setter slot.


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
    
  


#  cls is just a convention, you can name it anything:
#   But everyone uses cls — same reason everyone uses self. Technically optional, practically never change it or you'll confuse every Python developer who reads your code.

#   So the pattern is:
#   - @classmethod → Python injects the class, first arg conventionally named cls
#   - regular method → Python injects the instance, first arg conventionally named self
#   - @staticmethod → Python injects nothing

# u1 = User("Ali")
#   u2 = User("Bob")

#   # instance — each object has its own name
#   print(u1.name)      # Ali
#   print(u2.name)      # Bob

#   # class — shared across everything
#   print(User._count)  # 2
#   print(u1._count)    # 2  ← same value, it's shared
#   print(u2._count)    # 2  ← same value, it's shared

u1 = User("Ali", "ali@example.com")
u2 = User.from_dict({"name": "Bob", "email": "bob@example.com"})
print(User.count())                         # 2
print(User.validate_email("bad-email"))     # False


# pass means "do nothing" — it's a placeholder.

#   Python requires a function body to not be empty. If you have nothing to put there yet, you use pass:


# ─── EXERCISES ───────────────────────────────────────────────────────────────

# Exercise 1:
#   Create a `Rectangle` class with `width` and `height`.
#   Add @property `area` and @property `perimeter`.
#   Add a `is_square` @property that returns True if width == height.

# Exercise 3:
#   Add a `@classmethod from_string(cls, s: str)` to Rectangle
#   that parses "10x5" and returns Rectangle(width=10, height=5).


class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    @property
    def area(self) -> float:
        return float(self.width * self.height)
    
    @property
    def perimeter(self) -> float:
        return float((self.width + self.height) * 2)
    
    @property
    def is_square(self) -> bool:
        return self.width == self.height
    
    @classmethod
    def from_string(cls, s:str):
        split_string = s.split("x")
        width = float(split_string[0])
        height = float(split_string[1])
        # can do this way for cleaner and bigger list
        # width, height = [float(x) for x in s.split("x")]
        return cls(width, height)
    
    # without repr it defaulted to memory address, after adding repr it shows this custom message
    def __repr__(self):
        return(f"Rectangle(width={self.width}, height={self.height})")

    # after adding str it shows this now when printing
    def __str__(self):
        return(f"Width = {self.width}, Height = {self.height}")



    
r1 = Rectangle(4, 6)
print(r1.area)        # 24.0
print(r1.perimeter)   # 20.0
print(r1.is_square)   # False
print(r1.from_string("2x3"))

r2 = Rectangle(5, 5)
print(r2.is_square)   # True

r3 = Rectangle.from_string("10x5")

print(r3.area)       # 50.0
print(r3.width)      # 10.0
print(r3.height)     # 5.0
print(r3.from_string("2x3"))

# Exercise 2:
#   Create a `Vehicle` base class with `make`, `model`, `year`.
#   Add a `description()` method returning "{year} {make} {model}".
#   Create a `Car(Vehicle)` subclass with an extra `num_doors` attribute.
#   Create an `ElectricCar(Car)` subclass with `battery_range_km`.
#   Override `description()` in ElectricCar to append " (Electric, Xkm range)".

class Vehicle:
    def __init__(self, make: str, model: str, year: int):
        self.make = make
        self.model = model
        self.year = year
    
    def description(self) -> str:
        return (f"{self.year} {self.make} {self.model}")

class Car(Vehicle):
    def __init__(self, make, model, year, num_doors: int):
        super().__init__(make, model, year)
        self.num_doors = num_doors

class ElectricCar(Car):
    def __init__(self, make, model, year, num_doors, battery_range_km: float):
        super().__init__(make, model, year, num_doors)
        self.battery_range_km = battery_range_km
    
    def description(self):
        return (f"{super().description()} (Electric, {self.battery_range_km}km range)")
    
v = Vehicle("Toyota", "Camry", 2020)
c = Car("Honda", "Civic", 2022, 4)
e = ElectricCar("Tesla", "Model 3", 2024, 4, 300)

print(v.description())   # 2020 Toyota Camry
print(c.description())   # 2022 Honda Civic
print(e.description())   # 2024 Tesla Model 3 (Electric, 300km range)
print(isinstance(e, Vehicle))  # True


