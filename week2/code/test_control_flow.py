# !/usr/bin/env python3

"""Some functions exemplifying the use of control statements"""
# docstrings are considered part of the running code (normal comments are
# stripped). Hence, you can access your docstrings at run time.
__author__ = 'Zhou Yang(zy3425@imperial.ac.uk)'
__version__ = '0.0.1'

import sys
import doctest

def even_or_odd(x=0): # if not specified, x should take value 0.

    """Find whether a number x is even or odd."""
    if x < 0:
        if -x % 2 == 0: 
            return f"{x} is Even!"
        else:
            return f"{x} is Odd!"
    if x % 2 == 0: #The conditional if
        return f"{x} is Even!"
    return f"{x} is Odd!"

      
def main(argv):
    print(even_or_odd(22))
    print(even_or_odd(33))
    print(even_or_odd(10))
    print(even_or_odd(-5))
    print(even_or_odd(-2))

   
if (__name__ == "__main__"):
    status = main(sys.argv)
    doctest.testmod() 