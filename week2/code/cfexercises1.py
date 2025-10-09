import sys

def foo_1(x):
    return x ** 0.5

def foo_2(x, y):
    if x > y:
        return x
    return y

def foo_3(x, y, z):
    if x > y:
        x, y = y, x
    if x > z:
        x, z = z, x
    if y > z:
        y, z = z, y
    return [x, y, z]

def foo_4(x):
    result = 1
    for i in range(1, x + 1):
        result = result * i
    return result

def foo_5(x): # a recursive function that calculates the factorial of x
    if x == 0 or x == 1:
        return 1
    elif x > 1:
        return x * foo_5(x - 1)
    else:
        return "Error negative numbers"
     
def foo_6(x): # Calculate the factorial of x without if statement
    facto = 1
    while x > 0:
        facto = facto * x
        x = x - 1
    return facto

def main(argv):

    print("Test output with x=9, y=16, z=25")
    x = 9
    y = 16
    z = 25
    print(foo_1(x))
    print(foo_2(x,y))
    print(foo_3(x,y,z))
    print(foo_4(x))
    print(foo_5(x))
    print(foo_6(x))

    print(" Now input your own values for x, y and z")
    x = input("Enter a number for x: ")
    if not x.isdigit():
        print("Error: x should be a number")
        return 1
    y = input("Enter a number for y: ")
    if not y.isdigit():
        print("Error: y should be a number")
        return 1
    z = input("Enter a number for z: ")
    if not z.isdigit():
        print("Error: z should be a number")
        return 1
    
    print(foo_1(x))
    print(foo_2(x,y))
    print(foo_3(x,y,z))
    print(foo_4(x))
    print(foo_5(x))
    print(foo_6(x))
    return 0

if (__name__ == "__main__"):
    status = main(sys.argv)
    sys.exit(status)
