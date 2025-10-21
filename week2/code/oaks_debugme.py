import csv
import sys
# import ipdb; ipdb.set_trace()
from fuzzywuzzy import fuzz


def check_required_package():  # Check for required package
    try:
        __import__('fuzzywuzzy')
    except ImportError:
        print("Error: The fuzzywuzzy package is missing. Please install it to proceed.")
        sys.exit(1)


#Define function
def is_an_oak(name):
    # """ Returns True if name is starts with 'quercus' 
    # >>> is_an_oak('Quercus robur')
    # True
    # >>> is_an_oak('Acer pseudoplatanus')
    # False
    # """
    return fuzz.partial_ratio(name.lower(), 'quercus') >= 80

def main(argv): 
    f = open('../data/TestOaksData.csv','r')
    g = open('../data/JustOaksData.csv','w')
    taxa = csv.reader(f)
    
    header = next(taxa)  # get the header line.
    if header != ['Genus', 'Species']:
        taxa = csv.reader(f)
    else:
        next(taxa)  # skip the header line.
    
    # for row in taxa:
    #     print(row)   # check reading the file correctly.


    csvwrite = csv.writer(g)
    csvwrite.writerow(['Genus', 'Species'])
    for row in taxa:
        print(row)
        print ("The genus is: ") 
        print(row[0] + '\n')
        if is_an_oak(row[0]):
            print('FOUND AN OAK!\n')
            csvwrite.writerow([row[0], row[1]])    

    return 0
    
if (__name__ == "__main__"):
    status = main(sys.argv)