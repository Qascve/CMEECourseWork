import os
import csv

with open('../data/DNA1.txt', 'r') as s1, open('../data/DNA2.txt', 'r') as s2:
    s1 = s1.read() 
    s2 = s2.read()
# Two example sequences to match
# seq2 = "ATCGCCGGATTACGGG"
# seq1 = "CAATTCGGAT"

# Assign the longer sequence s1, and the shorter to s2
# l1 is length of the longest, l2 that of the shortest

l1 = len(s1)
l2 = len(s2)
if l1 >= l2:
    s1 = s1
    s2 = s2
else:
    s1 = s2
    s2 = s1
    l1, l2 = l2, l1 # swap the two lengths

# A function that computes a score by returning the number of matches starting
# from arbitrary startpoint (chosen by user)
def calculate_score(s1, s2, l1, l2, startpoint):
    matched = "" # to hold string displaying alignements
    score = 0
    for i in range(l2):
        if (i + startpoint) < l1:
            if s1[i + startpoint] == s2[i]: # if the bases match
                matched = matched + "*"
                score = score + 1
            else:
                matched = matched + "-"

    # some formatted output
    print("." * startpoint + matched)           
    print("." * startpoint + s2)
    print(s1)
    print(score) 
    print(" ")

    return score

# Test the function with some example starting points:
# calculate_score(s1, s2, l1, l2, 0)
# calculate_score(s1, s2, l1, l2, 1)
# calculate_score(s1, s2, l1, l2, 5)

# now try to find the best match (highest score) for the two sequences

my_best_align = []
my_best_score = 0

for i in range(l1): # Note that you just take the last alignment with the highest score
    z = calculate_score(s1, s2, l1, l2, i)
    if z > my_best_score:
        my_best_align = [("." * i + s2)] # store the best alignment
        my_best_score = z
    elif z == my_best_score:
        my_best_align.append(("." * i + s2)) # if same score, append this alignment
print(my_best_align)
print(s1)
print("Best score:", my_best_score)

results_dir = '../results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

results_file = os.path.join(results_dir, 'align.csv')

with open(results_file, 'w', newline='') as file:
    file = csv.writer(file)
    file.writerow([my_best_align])
    file.writerow([s1])
    file.writerow(["Best score:" + str(my_best_score)])