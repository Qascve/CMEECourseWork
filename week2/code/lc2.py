# Average UK Rainfall (mm) for 1910 by month
# http://www.metoffice.gov.uk/climate/uk/datasets
rainfall = (('JAN',111.4),
            ('FEB',126.1),
            ('MAR', 49.9),
            ('APR', 95.3),
            ('MAY', 71.8),
            ('JUN', 70.2),
            ('JUL', 97.1),
            ('AUG',140.2),
            ('SEP', 27.0),
            ('OCT', 89.4),
            ('NOV',128.4),
            ('DEC',142.2),
           )

# (1) Use a list comprehension to create a list of month,rainfall tuples where
# the amount of rain was greater than 100 mm.
 
heavy_rain = [item for item in rainfall if item[1] > 100]
print (">100mm" , str(heavy_rain))

# (2) Use a list comprehension to create a list of just month names where the
# amount of rain was less than 50 mm. 

light_rain = [item[0] for item in rainfall if item[1] < 50]
print ( "less than 50 mm", str(light_rain))

# (3) Now do (1) and (2) using conventional loops (you can choose to do 
# this before 1 and 2 !). 

heavy_rain = [] # create list for month,rainfall tuples where the amount of rain was greater than 100 mm
for item in rainfall:
    if item[1] > 100: # item[1] is the rainfall value
        heavy_rain.append(item) # append the whole tuple
print (">100mm" , str(heavy_rain))

light_rain = [] # create list for month names where the amount of rain was less than 50 mm
for item in rainfall:
    if item[1] < 50:
        light_rain.append(item[0]) # item[0] is the month name, append just the month name
print ( "less than 50 mm", str(light_rain))

# A good example output is:
#
# Step #1:
# Months and rainfall values when the amount of rain was greater than 100mm:
# [('JAN', 111.4), ('FEB', 126.1), ('AUG', 140.2), ('NOV', 128.4), ('DEC', 142.2)]
# ... etc.

