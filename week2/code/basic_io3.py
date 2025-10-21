import os
import sys
import pickle
#############################
# STORING OBJECTS
#############################
# To save an object (even complex) for later use
my_dictionary = {"a key": 10, "another key": 11}

if not os.path.exists('../sandbox'): ## make sure the folder exists
    print("not found: ../sandbox")
    sys.exit(1)

f = open('../sandbox/testp.p','wb') ## note the b: accept binary files
pickle.dump(my_dictionary, f)
f.close()

## Load the data again
if not os.path.exists('../sandbox/testp.p'):
    print("not found: ../sandbox/testp.p")
    sys.exit(1)
f = open('../sandbox/testp.p','rb')
another_dictionary = pickle.load(f)
f.close()

print(another_dictionary)