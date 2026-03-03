# CMEE 2024 HPC exercises R code pro forma
# For neutral model cluster run (Q24)

rm(list = ls())
graphics.off()

source("zy3425_HPC_2025_main.R")
source("Get_my_speciation_rate.R")

# Job index from PBS array
iter <- as.numeric(Sys.getenv("PBS_ARRAY_INDEX"))
# For local testing, comment the line above and uncomment the line below:
# iter <- 1


if (is.na(iter)) {
  stop("iter is NA. Set PBS_ARRAY_INDEX on cluster, or set iter manually for local testing.")
}
if (iter < 1 || iter > 100) {
  stop("iter must be in 1..100 for Q24.")
}

# Unique random seed for each parallel run
set.seed(iter)

# Assign community size: 25 runs per size
if (iter <= 25) {
  size <- 500
} else if (iter <= 50) {
  size <- 1000
} else if (iter <= 75) {
  size <- 2500
} else {
  size <- 5000
}

# Use personal speciation rate
speciation_rate <- personal_speciation_rate

# Unique output filename per parallel run
output_dir <- file.path("..", "Data", "neutral")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}
output_file_name <- file.path(output_dir, paste("neutral_sim_", iter, ".rda", sep = ""))

# Run simulation and save results
neutral_cluster_run(
  speciation_rate = speciation_rate,
  size = size,
  wall_time = 690,
  interval_rich = 1,
  interval_oct = size / 10,
  burn_in_generations = 8 * size,
  output_file_name = output_file_name
)
