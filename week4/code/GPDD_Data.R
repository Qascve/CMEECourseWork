
library(maps)
library(here)

# Load the GPDD data
load(here("week4", "data", "GPDDFiltered.RData"))

# Create a world map
map("world", col = "lightgray", fill = TRUE, border = "darkgray", 
    bg = "lightblue", ylim = c(-60, 90))

# Superimpose data points showing GPDD locations
points(gpdd$long, gpdd$lat, col = "red", pch = 20, cex = 0.7)

# Add title
title(main = "Global Population Dynamics Database - Data Locations")

# Analysis based on distribution:
# Most of the data points are concentrated in the Northern Hemisphere, 
# and almost all are from developed countries such as Western Europe and North America, 
# with very few from other regions.
