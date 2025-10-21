#############################
# FILE OUTPUT
#############################
# Save the elements of a list to a file
import os
import sys

if not os.path.exists('../sandbox/test.txt'): ## make sure the folder exists
    print("not found: ../sandbox/test.txt")
    sys.exit(1)
    
list_to_save = range(100)

f = open('../sandbox/testout.txt','w')
for i in list_to_save:
    f.write(str(i) + '\n') ## Add a new line at the end

f.close()
