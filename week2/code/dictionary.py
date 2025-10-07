taxa = [ ('Myotis lucifugus','Chiroptera'),
         ('Gerbillus henleyi','Rodentia',),
         ('Peromyscus crinitus', 'Rodentia'),
         ('Mus domesticus', 'Rodentia'),
         ('Cleithrionomys rutilus', 'Rodentia'),
         ('Microgale dobsoni', 'Afrosoricida'),
         ('Microgale talazaci', 'Afrosoricida'),
         ('Lyacon pictus', 'Carnivora'),
         ('Arctocephalus gazella', 'Carnivora'),
         ('Canis lupus', 'Carnivora'),
        ]

# Write a python script to populate a dictionary called taxa_dic derived from
# taxa so that it maps order names to sets of taxa and prints it to screen.
# 
# An example output is:
#  
# 'Chiroptera' : set(['Myotis lucifugus']) ... etc. 
# OR, 
# 'Chiroptera': {'Myotis  lucifugus'} ... etc

#### Your solution here #### 
taxa_dic = {}
for item in taxa:
    species = item[0]
    order = item[1]
    if order not in taxa_dic:
        taxa_dic[order] = set()  # Initialize a new set for this order
    taxa_dic[order].add(species)  # Add the species to the set for this order

print(taxa_dic)

# Now write a list comprehension that does the same (including the printing after the dictionary has been created)  
 
#### Your solution here #### 

comprehension_taxa_dic = {}
{comprehension_taxa_dic.setdefault(item[1], set()).add(item[0]) for item in taxa} # Set item[1] as key, add item[0] to the set at that key

print(comprehension_taxa_dic)