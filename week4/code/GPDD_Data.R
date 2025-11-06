
library(maps)
library(here)

# Load the GPDD data
load(here("week4", "data", "GPDDFiltered.RData"))

# Create a world map
pdf(here("week4", "results", "GPDD_Map.pdf"), width = 8, height = 6)  # Save to results folder
map("world", col = "lightgray", fill = TRUE, border = "darkgray", 
    bg = "lightblue", ylim = c(-60, 90))

# Superimpose data points showing GPDD locations
points(gpdd$long, gpdd$lat, col = "red", pch = 20, cex = 0.7)

# Add title
title(main = "Global Population Dynamics Database - Data Locations")

dev.off()
print("GPDD Map Saved")

# Analysis based on distribution:
# Most of the data points are concentrated in the Northern Hemisphere, 
# and almost all are from developed countries such as Western Europe and North America, 
# with very few from other regions.

