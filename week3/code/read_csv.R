setwd("../code/")
MyData <- read.csv("../data/trees.csv")
ls(pattern = "My*") # Check that MyData has appeared
class(MyData)
head(MyData)
str(MyData) 
MyData <- read.table("../data/trees.csv", sep = ',', header = TRUE) #another way
MyData <- read.csv("../data/trees.csv", skip = 5) # skip first 5 linesdata
