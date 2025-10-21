#############################
# FILE INPUT
#############################
# Open a file for reading
import os
import sys

if not os.path.exists('../sandbox/test.txt'): ## make sure the file exists
    print("not found: ../sandbox/test.txt")
    sys.exit(1)

f = open('../sandbox/test.txt', 'r')
# use "implicit" for loop:
# if the object is a file, python will cycle over lines
for line in f:
    print(line)

# close the file
f.close()

if not os.path.exists('../sandbox/test.txt'): ## make sure the file exists
    print("not found: ../sandbox/test.txt")
    sys.exit(1)

# Same example, skip blank lines
f = open('../sandbox/test.txt', 'r')
for line in f:
    if len(line.strip()) > 0:
        print(line)

f.close()