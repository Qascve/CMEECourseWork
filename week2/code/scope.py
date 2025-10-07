# scope.py

# Local variables and function scope

i = 1
x = 0
for i in range(10):
    x += 1
print(i)  # 9
print(x)  # 10

i = 1
x = 0
def a_function(y):
    x = 0
    for i in range(y):
        x += 1
    return x

a_function(10)
print(i)  # still 1
print(x)  # still 0

# explicitly reassign the result to x
x = a_function(10)
print("Updated x after reassignment:", x)

# Global variables

_a_global = 10  # a global variable

if _a_global >= 5:
    _b_global = _a_global + 5  # also global

print("Before calling a_function, outside the function, _a_global =", _a_global)
print("Before calling a_function, outside the function, _b_global =", _b_global)

def a_function():
    _a_global = 4  # local variable
    if _a_global >= 4:
        _b_global = _a_global + 5  # local variable
    _a_local = 3
    print("Inside function, _a_global =", _a_global)
    print("Inside function, _b_global =", _b_global)
    print("Inside function, _a_local =", _a_local)

a_function()

print("After calling a_function, outside, _a_global (still) =", _a_global)
print("After calling a_function, outside, _b_global (still) =", _b_global)
try:
    print("After calling a_function, outside, _a_local =", _a_local)
except NameError as e:
    print("NameError:", e)


_a_global = 10
def a_function():
    _a_local = 4
    print("Inside function, _a_local =", _a_local)
    print("Inside function, _a_global =", _a_global)

a_function()
print("Outside function, _a_global =", _a_global)

# Modifying a global variable by 'global' keyword
_a_global = 10
print("Before calling a_function, outside, _a_global =", _a_global)

def a_function():
    global _a_global
    _a_global = 5
    _a_local = 4
    print("Inside function, _a_global =", _a_global)
    print("Inside function, _a_local =", _a_local)

a_function()
print("After calling a_function, outside, _a_global now =", _a_global)
def a_function():
    _a_global = 10
    def _a_function2():
        global _a_global
        _a_global = 20
    print("Before calling _a_function2, _a_global =", _a_global)
    _a_function2()
    print("After calling _a_function2, _a_global =", _a_global)

a_function()
print("In main namespace, _a_global =", _a_global)

_a_global = 10
def a_function():
    def _a_function2():
        global _a_global
        _a_global = 20
    print("Before calling _a_function2, _a_global =", _a_global)
    _a_function2()
    print("After calling _a_function2, _a_global =", _a_global)

a_function()
print("In main namespace, _a_global =", _a_global)

