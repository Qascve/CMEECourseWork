# Check if required packages are installed
if(!requireNamespace("maps", quietly = TRUE)) {
  cat("Error: 'maps' package is not installed.\n")
  quit(save = "no", status = 0)
}
if(!requireNamespace("here", quietly = TRUE)) {
  cat("Error: 'here' package is not installed.\n")
  quit(save = "no", status = 0)
}

# Load required packages
library(maps)
library(here)

# Load the GPDD data
load(here("week4", "data", "GPDDFiltered.RData"))

# Save the plot to PDF
pdf(here("week4", "results", "GPDD_map.pdf"), width = 11, height = 8)

# Create a world map
map("world", col = "lightgray", fill = TRUE, border = "darkgray", 
    bg = "lightblue", ylim = c(-60, 90))

# Superimpose data points showing GPDD locations
points(gpdd$long, gpdd$lat, col = "red", pch = 20, cex = 0.7)

# Add title
title(main = "Global Population Dynamics Database - Data Locations")

# Close the PDF device
dev.off()

# Analysis based on distribution:
# Most of the data points are concentrated in the Northern Hemisphere, 
# and almost all are from developed countries such as Western Europe and North America, 
# with very few from other regions.


print("GPDD map saved to results/GPDD_map.pdf\n")