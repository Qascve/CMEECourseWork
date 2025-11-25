################################################################
################## Wrangling the Pound Hill Dataset ############
################################################################
if(!requireNamespace("here", quietly = TRUE)) {
  cat("Required package 'here' is not installed. Please install it using: install.packages('here')\n")
  quit(save = "no", status = 0)
}
if(!requireNamespace("reshape2", quietly = TRUE)) {
  cat("Required package 'reshape2' is not installed. Please install it using: install.packages('reshape2')\n")
  quit(save = "no", status = 0)
}

library(here)
MyData <- as.matrix(read.csv(here("week4", "data", "PoundHillData.csv"), header = FALSE))

# header = true because we do have metadata headers
MyMetaData <- read.csv(here("week4", "data", "PoundHillMetaData.csv"), header = TRUE, sep = ";")

############# Inspect the dataset ###############
head(MyData)
dim(MyData)
str(MyData)
#fix(MyData) #you can also do this
#fix(MyMetaData)

############# Transpose ###############
# To get those species into columns and treatments into rows 
MyData <- t(MyData) 
head(MyData)
dim(MyData)

############# Replace species absences with zeros ###############
MyData[MyData == ""] = 0

############# Convert raw matrix to data frame ###############

TempData <- as.data.frame(MyData[-1,],stringsAsFactors = F) #stringsAsFactors = F is important!
colnames(TempData) <- MyData[1,] # assign column names from original data

############# Convert from wide to long format  ###############
require(reshape2) # load the reshape2 package

#?melt #check out the melt function

MyWrangledData <- melt(TempData, id=c("Cultivation", "Block", "Plot", "Quadrat"), variable.name = "Species", value.name = "Count")

MyWrangledData[, "Cultivation"] <- as.factor(MyWrangledData[, "Cultivation"])
MyWrangledData[, "Block"] <- as.factor(MyWrangledData[, "Block"])
MyWrangledData[, "Plot"] <- as.factor(MyWrangledData[, "Plot"])
MyWrangledData[, "Quadrat"] <- as.factor(MyWrangledData[, "Quadrat"])
MyWrangledData[, "Count"] <- as.integer(MyWrangledData[, "Count"])

str(MyWrangledData)
head(MyWrangledData)
dim(MyWrangledData)

############# Exploring the data (extend the script below)  ###############
