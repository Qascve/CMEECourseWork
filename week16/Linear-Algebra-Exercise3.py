import sympy as sp

# Linear Algebra Exercise 3
x, y = sp.symbols('x y')
A = sp.Matrix([[3,-7],[1,7]])
b = sp.Matrix([4,10])
z = A.inv() * b

print("A inverse:")
print(A.inv())
print("A, b:")
print(A, b)
print("z = A^{-1} * b:")
print(z)
x = z[0]
y = z[1]
print(f"Solution: x = {x}, y = {y}")
