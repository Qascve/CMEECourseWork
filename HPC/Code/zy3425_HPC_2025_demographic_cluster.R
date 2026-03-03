# CMEE 2024 HPC exercises R code pro forma
# For stochastic demographic model cluster run (Q3)

rm(list = ls())
graphics.off()

# Load required functions
source("zy3425_HPC_2025_main.R")
source("Demographic.R")

# Job index from PBS array
iter <- as.numeric(Sys.getenv("PBS_ARRAY_INDEX"))


if (is.na(iter)) {
  stop("iter is NA. Set PBS_ARRAY_INDEX on cluster, or set iter manually for local testing.")
}
if (iter < 1 || iter > 100) {
  stop("iter must be in 1..100 for Q3.")
}

# Unique random seed for each parallel run
set.seed(iter)

# Model settings (from Q2)
growth_matrix <- matrix(
  c(
    0.1, 0.0, 0.0, 0.0,
    0.5, 0.4, 0.0, 0.0,
    0.0, 0.4, 0.7, 0.0,
    0.0, 0.0, 0.25, 0.4
  ),
  nrow = 4, ncol = 4, byrow = TRUE
)

reproduction_matrix <- matrix(
  c(
    0.0, 0.0, 0.0, 2.6,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0
  ),
  nrow = 4, ncol = 4, byrow = TRUE
)

clutch_distribution <- c(0.06, 0.08, 0.13, 0.15, 0.16, 0.18, 0.15, 0.06, 0.03)
simulation_length <- 120

# Assign one of four initial conditions
# 1: 100 adults, 2: 10 adults, 3: 100 spread, 4: 10 spread
if (iter <= 25) {
  initial_condition_id <- 1
  initial_state <- c(0, 0, 0, 100)
} else if (iter <= 50) {
  initial_condition_id <- 2
  initial_state <- c(0, 0, 0, 10)
} else if (iter <= 75) {
  initial_condition_id <- 3
  initial_state <- c(25, 25, 25, 25)
} else {
  initial_condition_id <- 4
  initial_state <- c(3, 3, 2, 2)
}

# Run 150 stochastic simulations for this initial condition
results_list <- vector(mode = "list", length = 150)
for (rep_id in seq_len(150)) {
  results_list[[rep_id]] <- stochastic_simulation(
    initial_state = initial_state,
    growth_matrix = growth_matrix,
    reproduction_matrix = reproduction_matrix,
    clutch_distribution = clutch_distribution,
    simulation_length = simulation_length
  )
}

# Filename must include iter so array jobs never overwrite each other
output_dir <- file.path("..", "Data", "demographic")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}
output_filename <- file.path(output_dir, paste("demographic_sim_", iter, ".rda", sep = ""))

# Save simulation outputs and key metadata for downstream analysis
save(
  results_list,
  iter,
  initial_condition_id,
  initial_state,
  growth_matrix,
  reproduction_matrix,
  clutch_distribution,
  simulation_length,
  file = output_filename
)
