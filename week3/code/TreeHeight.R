# This function calculates heights of trees given distance of each tree
# from its base and angle to its top, using  the trigonometric formula
#
# height = distance * tan(radians)
#
# ARGUMENTS
# degrees:   The angle of elevation of tree
# distance:  The distance from base of tree (e.g., meters)
#
# OUTPUT
# The heights of the tree, same units as "distance"
script_path <- dirname(sys.frame(1)$ofile)
setwd(script_path)

treeData <- read.csv("../data/trees.csv", header = TRUE) # import with headers

TreeHeight <- function(degrees, distance) {
    radians <- degrees * pi / 180
    height <- distance * tan(radians)
    print(paste("Tree height is:", height))
  
    return (height)
}

treeData$Tree.Height.m <- TreeHeight(treeData$Angle.degrees, treeData$Distance.m)
write.csv(treeData, "../results/TreeHts.csv", row.names = FALSE)