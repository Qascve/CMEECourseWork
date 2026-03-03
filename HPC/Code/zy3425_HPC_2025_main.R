# CMEE 2024 HPC exercises R code main pro forma
# You don't HAVE to use this but it will be very helpful.
# If you opt to write everything yourself from scratch please ensure you use
# EXACTLY the same function and parameter names and beware that you may lose
# marks if it doesn't work properly because of not using the pro-forma.

name <- "Zhou Yang"
preferred_name <- "Zhou"
email <- "zy3425@ic.ac.uk"
username <- "zy3425"

# Please remember *not* to clear the work space here, or anywhere in this file.
# If you do, it'll wipe out your username information that you entered just
# above, and when you use this file as a 'toolbox' as intended it'll also wipe
# away everything you're doing outside of the toolbox.  For example, it would
# wipe away any automarking code that may be running and that would be annoying!

# Section One: Stochastic demographic population model

# Question 0

state_initialise_adult <- function(num_stages, initial_size){
  # Create state vector with all individuals in adult (final) stage
  state <- rep(0, num_stages)
  state[num_stages] <- initial_size
  state
}

state_initialise_spread <- function(num_stages, initial_size){
  # Spread individuals evenly across stages, remainder to youngest first
  base_per_stage <- floor(initial_size / num_stages)
  remainder <- initial_size %% num_stages
  state <- rep(base_per_stage, num_stages)
 
  if (remainder > 0) {
    state[1:remainder] <- state[1:remainder] + 1
  }
  state
}

# Question 1
question_1 <- function(){
  # Source the demographic simulation code
  source("Code/Demographic.R")
  
  # Define projection matrices
  growth_matrix <- matrix(c(0.1, 0.0, 0.0, 0.0,
                            0.5, 0.4, 0.0, 0.0,
                            0.0, 0.4, 0.7, 0.0,
                            0.0, 0.0, 0.25, 0.4),
                           nrow = 4, ncol = 4, byrow = TRUE)
  
  reproduction_matrix <- matrix(c(0.0, 0.0, 0.0, 2.6,
                                  0.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0),
                                nrow = 4, ncol = 4, byrow = TRUE)
  
  projection_matrix <- reproduction_matrix + growth_matrix
  
  # Create two initial conditions
  initial_adult <- state_initialise_adult(4, 100)      # All adults
  initial_spread <- state_initialise_spread(4, 100)    # Evenly spread
  
  # Run deterministic simulations
  sim_adult <- deterministic_simulation(initial_adult, projection_matrix, 24)
  sim_spread <- deterministic_simulation(initial_spread, projection_matrix, 24)
  
  png(filename = "Results/question_1.png", width = 600, height = 400)
  # plot your graph here
  plot(0:24, sim_adult, type = "l", col = "blue", lwd = 2,
       xlab = "Time Step", ylab = "Population Size",
       main = "Population Growth with Different Initial Distributions",
       ylim = range(c(sim_adult, sim_spread)))
  lines(0:24, sim_spread, col = "red", lwd = 2)
  legend("topleft", legend = c("All Adults", "Evenly Spread"),
         col = c("blue", "red"), lwd = 2)
  Sys.sleep(0.1)
  dev.off()
  
  return(paste(
    "The initial stage structure clearly changes early growth.",
    "In this run, both populations increase at first, but the all-adult start grows much faster",
    "because reproduction from adults is immediate.",
    "The spread initial state grows more steadily.",
    "Over time, the two trajectories become more similar as the stage structure settles."
  ))
}

# Question 2
question_2 <- function(){
  source("Code/Demographic.R")
  
  growth_matrix <- matrix(c(0.1, 0.0, 0.0, 0.0,
                            0.5, 0.4, 0.0, 0.0,
                            0.0, 0.4, 0.7, 0.0,
                            0.0, 0.0, 0.25, 0.4),
                          nrow = 4, ncol = 4, byrow = TRUE)
  
  reproduction_matrix <- matrix(c(0.0, 0.0, 0.0, 2.6,
                                  0.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0),
                                nrow = 4, ncol = 4, byrow = TRUE)
  
  clutch_distribution <- c(0.06, 0.08, 0.13, 0.15, 0.16, 0.18, 0.15, 0.06, 0.03)
  
  initial_adult <- state_initialise_adult(4, 100)
  initial_spread <- state_initialise_spread(4, 100)
  
  sim_adult <- stochastic_simulation(initial_adult, growth_matrix, reproduction_matrix, clutch_distribution, 24)
  sim_spread <- stochastic_simulation(initial_spread, growth_matrix, reproduction_matrix, clutch_distribution, 24)
  
  png(filename = "Results/question_2.png", width = 600, height = 400)
  # plot your graph here
  plot(0:24, sim_adult, type = "l", col = "blue", lwd = 2,
       xlab = "Time Step", ylab = "Population Size",
       main = "Stochastic Population Dynamics",
       ylim = range(c(0, sim_adult, sim_spread), na.rm = TRUE))
  lines(0:24, sim_spread, col = "red", lwd = 2)
  legend("topleft", legend = c("Adults", "Spread"),
         col = c("blue", "red"), lwd = 2, lty = c(1, 1))
  Sys.sleep(0.1)
  dev.off()
  
  return(paste(
    "Compared with deterministic simulations, stochastic trajectories are less smooth",
    "and show irregular fluctuations through time.",
    "This is because births, deaths and stage transitions are random events in each step,",
    "so population size can move up or down unpredictably around the deterministic trend."
  ))
}

# Questions 3 and 4 involve writing code elsewhere to run your simulations on the cluster


# Question 5
question_5 <- function(){
  data_dir <- "Data/demographic"
  files <- list.files(data_dir, pattern = "demographic_sim_[0-9]+\\.rda$", full.names = TRUE)
  if (length(files) == 0) {
    stop("No demographic_sim_*.rda files found in Data/demographic.")
  }

  cond_labels <- c(
    "Adults, large population",
    "Adults, small population",
    "Mixed, large population",
    "Mixed, small population"
  )
  expected_states <- list(
    c(0, 0, 0, 100),
    c(0, 0, 0, 10),
    c(25, 25, 25, 25),
    c(3, 3, 2, 2)
  )
  # Aggregate all simulation runs across all .rda files first.
  all_condition <- integer(0)
  all_final_pop <- numeric(0)

  for (file in files) {
    env <- new.env()
    load(file, envir = env)

    if (!exists("initial_condition_id", envir = env)) {
      stop("initial_condition_id is required in each .rda file.")
    }
    condition_id <- as.integer(get("initial_condition_id", envir = env))
    if (!condition_id %in% 1:4) {
      stop("initial_condition_id must be 1, 2, 3, or 4.")
    }
    if (exists("initial_state", envir = env)) {
      state_vec <- as.numeric(get("initial_state", envir = env))
      if (!isTRUE(all.equal(state_vec, expected_states[[condition_id]]))) {
        stop("initial_state does not match its initial_condition_id.")
      }
    }

    runs <- get("results_list", envir = env)
    final_pop <- vapply(runs, function(x) x[length(x)], numeric(1))
    all_condition <- c(all_condition, rep(condition_id, length(final_pop)))
    all_final_pop <- c(all_final_pop, final_pop)
  }

  extinction_count <- setNames(rep(0L, 4), cond_labels)
  total_count <- setNames(rep(0L, 4), cond_labels)
  for (condition_id in 1:4) {
    idx <- all_condition == condition_id
    label <- cond_labels[condition_id]
    total_count[label] <- sum(idx)
    extinction_count[label] <- sum(all_final_pop[idx] == 0)
  }

  extinction_prop <- extinction_count / total_count

  png(filename = "Results/question_5.png", width = 700, height = 450)
  barplot(
    extinction_prop,
    col = c("#4C78A8", "#F58518", "#54A24B", "#E45756"),
    ylim = c(0, max(extinction_prop) * 1.15 + 1e-6),
    ylab = "Proportion extinct",
    xlab = "Initial condition",
    main = "Extinction proportion by initial condition"
  )
  Sys.sleep(0.1)
  dev.off()

  worst <- names(which.max(extinction_prop))
  prop_text <- paste(
    paste0(names(extinction_prop), ": ", round(extinction_prop, 4)),
    collapse = "; "
  )
  return(paste(
    "Extinction proportions across all four initial conditions are:",
    prop_text, ".",
    "The population most likely to go extinct is", worst,
    "(proportion =", round(max(extinction_prop), 4), ").",
    "This conclusion is data-driven from all loaded .rda simulations."
  ))
}

# Question 6
question_6 <- function(){
  source("Code/Demographic.R")

  data_dir <- "Data/demographic"
  files <- list.files(data_dir, pattern = "^demographic_sim_[0-9]+\\.rda$", full.names = TRUE)
  if (length(files) == 0) {
    stop("No demographic_sim_*.rda files found in Data/demographic.")
  }

  growth_matrix <- matrix(c(0.1, 0.0, 0.0, 0.0,
                            0.5, 0.4, 0.0, 0.0,
                            0.0, 0.4, 0.7, 0.0,
                            0.0, 0.0, 0.25, 0.4),
                          nrow = 4, ncol = 4, byrow = TRUE)

  reproduction_matrix <- matrix(c(0.0, 0.0, 0.0, 2.6,
                                  0.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0),
                                nrow = 4, ncol = 4, byrow = TRUE)

  projection_matrix <- reproduction_matrix + growth_matrix
  expected_states <- list(
    c(0, 0, 0, 100),
    c(0, 0, 0, 10),
    c(25, 25, 25, 25),
    c(3, 3, 2, 2)
  )

  # Aggregate all runs from all .rda files first, then analyse.
  all_condition <- integer(0)
  all_stochastic <- list()

  for (file in files) {
    env <- new.env()
    load(file, envir = env)

    if (!exists("initial_condition_id", envir = env)) {
      stop("initial_condition_id is required in each .rda file.")
    }
    condition_id <- as.integer(get("initial_condition_id", envir = env))
    if (!condition_id %in% 1:4) {
      stop("initial_condition_id must be 1, 2, 3, or 4.")
    }
    if (exists("initial_state", envir = env)) {
      state_vec <- as.numeric(get("initial_state", envir = env))
      if (!isTRUE(all.equal(state_vec, expected_states[[condition_id]]))) {
        stop("initial_state does not match its initial_condition_id.")
      }
    }

    runs <- get("results_list", envir = env)
    all_condition <- c(all_condition, rep(condition_id, length(runs)))
    all_stochastic <- c(all_stochastic, runs)
  }

  # Analyse the combined dataset but keep only conditions 3 and 4 as required.
  keep_idx <- all_condition %in% c(3L, 4L)
  if (!any(keep_idx)) {
    stop("No runs from initial conditions 3 and 4 found across demographic .rda files.")
  }
  kept_condition <- all_condition[keep_idx]
  kept_stochastic <- all_stochastic[keep_idx]

  cond3_runs <- kept_stochastic[kept_condition == 3L]
  cond4_runs <- kept_stochastic[kept_condition == 4L]
  if (length(cond3_runs) == 0 || length(cond4_runs) == 0) {
    stop("Both conditions 3 and 4 are required after combining all .rda runs.")
  }

  mat3 <- do.call(rbind, cond3_runs)
  mat4 <- do.call(rbind, cond4_runs)
  mean3 <- colMeans(mat3)
  mean4 <- colMeans(mat4)

  sim_len <- ncol(mat3) - 1
  det3 <- deterministic_simulation(c(25, 25, 25, 25), projection_matrix, sim_len)
  det4 <- deterministic_simulation(c(3, 3, 2, 2), projection_matrix, sim_len)

  dev3 <- mean3 / det3
  dev4 <- mean4 / det4

  rmse3 <- sqrt(mean((dev3 - 1)^2, na.rm = TRUE))
  rmse4 <- sqrt(mean((dev4 - 1)^2, na.rm = TRUE))

  png(filename = "Results/question_6.png", width = 600, height = 400)
  old_par <- par(no.readonly = TRUE)
  par(mfrow = c(1, 2))

  plot(
    0:sim_len, dev3, type = "l", lwd = 2, col = "#1f77b4",
    ylim = range(c(dev3, dev4), na.rm = TRUE),
    xlab = "Time step", ylab = "Stochastic mean / Deterministic",
    main = "Condition 3: large mixed"
  )
  abline(h = 1, lty = 2, col = "gray40")

  plot(
    0:sim_len, dev4, type = "l", lwd = 2, col = "#d62728",
    ylim = range(c(dev3, dev4), na.rm = TRUE),
    xlab = "Time step", ylab = "Stochastic mean / Deterministic",
    main = "Condition 4: small mixed"
  )
  abline(h = 1, lty = 2, col = "gray40")

  par(old_par)
  Sys.sleep(0.1)
  dev.off()

  better <- if (rmse3 < rmse4) "condition 3 (large mixed)" else "condition 4 (small mixed)"
  return(paste(
    "The deterministic approximation is more appropriate for", better,
    "because its deviation from 1 is smaller (RMSE:",
    "cond3 =", round(rmse3, 6), ", cond4 =", round(rmse4, 6), ").",
    "Larger mixed populations average out stochastic noise more effectively."
  ))
}


# Section Two: Individual-based ecological neutral theory simulation 

get_personal_speciation_rate <- function() {
  env <- new.env(parent = globalenv())
  suppressWarnings(suppressMessages(sys.source("Code/Get_my_speciation_rate.R", envir = env)))
  env$personal_speciation_rate
}

# Question 7
species_richness <- function(community){
  # count distinct species IDs; drop NAs if present
  length(unique(stats::na.omit(community)))
}

# Question 8
init_community_max <- function(size){
  seq_len(size)
}

# Question 9
init_community_min <- function(size){
  rep(1, size)
}

# Question 10
choose_two <- function(max_value){
  sample.int(max_value, 2, replace = FALSE)
}

# Question 11
neutral_step <- function(community){
  pair <- choose_two(length(community))
  community[pair[1]] <- community[pair[2]]
  community
}

# Question 12
neutral_generation <- function(community){
  n <- length(community)
  if (n %% 2 == 0) {
    n_steps <- n %/% 2
  } else {
    # For odd sizes, randomly round x/2 down or up.
    n_steps <- (n %/% 2) + sample.int(2, 1) - 1
  }
  
  for (i in seq_len(n_steps)) {
    community <- neutral_step(community)
  }
  community
}

# Question 13
neutral_time_series <- function(community, duration)  {
  richness <- numeric(duration + 1)
  richness[1] <- species_richness(community)
  if (duration > 0) {
    for (t in seq_len(duration)) {
      community <- neutral_generation(community)
      richness[t + 1] <- species_richness(community)
    }
  }
  richness
}

# Question 14
question_14 <- function() {
  community <- init_community_max(100)
  richness <- neutral_time_series(community, 200)
  
  png(filename = "Results/question_14.png", width = 600, height = 400)
  # plot your graph here
  plot(0:200, richness, type = "l", col = "blue", lwd = 2,
       xlab = "Generation", ylab = "Species Richness",
       main = "Neutral Model: Richness Over Time")
  Sys.sleep(0.1)
  dev.off()
  
  return(paste(
    "With no speciation, the neutral model will always converge to a state",
    "where a single species dominates the entire community. This happens because",
    "random drift causes species to go extinct one by one until only one remains."
  ))
}

# Question 15
neutral_step_speciation <- function(community, speciation_rate)  {
  pair <- choose_two(length(community))
  death_index <- pair[1]
  parent_index <- pair[2]
  
  if (runif(1) < speciation_rate) {
    community[death_index] <- max(community) + 1
  } else {
    community[death_index] <- community[parent_index]
  }
  
  community
}

# Question 16
neutral_generation_speciation <- function(community, speciation_rate)  {
  n <- length(community)
  if (n %% 2 == 0) {
    n_steps <- n %/% 2
  } else {
    # For odd sizes, randomly round x/2 down or up.
    n_steps <- (n %/% 2) + sample.int(2, 1) - 1
  }
  
  for (i in seq_len(n_steps)) {
    community <- neutral_step_speciation(community, speciation_rate)
  }
  
  community
}

# Question 17
neutral_time_series_speciation <- function(community, speciation_rate, duration)  {
  richness <- numeric(duration + 1)
  richness[1] <- species_richness(community)
  
  if (duration > 0) {
    for (t in seq_len(duration)) {
      community <- neutral_generation_speciation(community, speciation_rate)
      richness[t + 1] <- species_richness(community)
    }
  }
  
  richness
}

# Question 18
question_18 <- function()  {
  speciation_rate <- 0.1
  duration <- 200
  size <- 100
  
  community_max <- init_community_max(size)
  community_min <- init_community_min(size)
  
  series_max <- neutral_time_series_speciation(community_max, speciation_rate, duration)
  series_min <- neutral_time_series_speciation(community_min, speciation_rate, duration)
  
  png(filename = "Results/question_18.png", width = 600, height = 400)
  # plot your graph here
  plot(0:duration, series_max, type = "l", col = "blue", lwd = 2,
       xlab = "Generation", ylab = "Species Richness",
       main = "Neutral Model with Speciation",
       ylim = range(c(series_max, series_min)))
  lines(0:duration, series_min, col = "red", lwd = 2)
  legend("topleft", legend = c("Max initial richness", "Min initial richness"),
         col = c("blue", "red"), lwd = 2)
  Sys.sleep(0.1)
  dev.off()
  
  return(paste(
    "Initial conditions affect the short-term trajectory: the max-richness",
    "community declines while the min-richness community increases. Over time,",
    "both converge to a similar equilibrium richness because speciation adds",
    "new species while drift removes them, leading to a balance."
  ))
}

# Question 19
species_abundance <- function(community)  {
  counts <- table(community)
  as.integer(sort(counts, decreasing = TRUE))
}

# Question 20
octaves <- function(abundance_vector) {
  if (length(abundance_vector) == 0) {
    return(integer(0))
  }
  
  classes <- floor(log2(abundance_vector)) + 1
  tabulate(classes)
}

# Question 21
sum_vect <- function(x, y) {
  len_x <- length(x)
  len_y <- length(y)
  
  if (len_x < len_y) {
    x <- c(x, rep(0, len_y - len_x))
  } else if (len_y < len_x) {
    y <- c(y, rep(0, len_x - len_y))
  }
  
  x + y
}

# Question 22
question_22 <- function() {
  speciation_rate <- 0.1
  size <- 100
  burn_in <- 200
  record_generations <- 2000
  record_interval <- 20
  
  run_octave_series <- function(initial_community) {
    community <- initial_community
    
    for (i in seq_len(burn_in)) {
      community <- neutral_generation_speciation(community, speciation_rate)
    }
    
    octave_list <- list()
    octave_list[[1]] <- octaves(species_abundance(community))
    
    steps <- record_generations / record_interval
    for (i in seq_len(steps)) {
      for (j in seq_len(record_interval)) {
        community <- neutral_generation_speciation(community, speciation_rate)
      }
      octave_list[[length(octave_list) + 1]] <- octaves(species_abundance(community))
    }
    
    octave_list
  }
  
  mean_octaves <- function(octave_list) {
    total <- numeric(0)
    for (oct in octave_list) {
      total <- sum_vect(total, oct)
    }
    total / length(octave_list)
  }
  
  octaves_max <- run_octave_series(init_community_max(size))
  octaves_min <- run_octave_series(init_community_min(size))
  
  mean_max <- mean_octaves(octaves_max)
  mean_min <- mean_octaves(octaves_min)
  
  png(filename = "Results/question_22.png", width = 600, height = 400)
  # plot your graph here
  old_par <- par(no.readonly = TRUE)
  par(mfrow = c(1, 2))
  
  barplot(mean_max, main = "Max initial richness",
          xlab = "Octave class", ylab = "Mean species count")
  barplot(mean_min, main = "Min initial richness",
          xlab = "Octave class", ylab = "Mean species count")
  
  par(old_par)
  Sys.sleep(0.1)
  dev.off()
  
  return(paste(
    "After a long burn-in, the mean abundance distributions become very similar",
    "for both initial conditions. Initial state affects the transient dynamics,",
    "but the long-term distribution is governed by the balance of speciation and",
    "drift, so initial conditions no longer matter."
  ))
}

# Question 23
neutral_cluster_run <- function(speciation_rate, size, wall_time, interval_rich, interval_oct, burn_in_generations, output_file_name) {
  community <- init_community_min(size)
  interval_rich <- as.integer(interval_rich)
  interval_oct <- as.integer(interval_oct)
  
  time_series <- numeric(0)
  abundance_list <- list()
  
  generation <- 0
  start_time <- proc.time()[3]
  
  while ((proc.time()[3] - start_time) / 60 < wall_time) {
    community <- neutral_generation_speciation(community, speciation_rate)
    generation <- generation + 1
    
    if (generation <= burn_in_generations && generation %% interval_rich == 0) {
      time_series <- c(time_series, species_richness(community))
    }
    
    if (generation %% interval_oct == 0) {
      abundance_list[[length(abundance_list) + 1]] <- octaves(species_abundance(community))
    }
  }
  
  total_time <- (proc.time()[3] - start_time) / 60
  final_community <- community
  
  save(time_series, abundance_list, final_community, total_time,
       speciation_rate, size, wall_time, interval_rich, interval_oct,
       burn_in_generations, file = output_file_name)
  
  invisible(NULL)
}

# Questions 24 and 25 involve writing code elsewhere to run your simulations on
# the cluster

# Question 26 
process_neutral_cluster_results <- function() {
  files <- list.files(".", pattern = "^neutral_sim_[0-9]+\\.rda$", full.names = TRUE)
  if (length(files) == 0) {
    files <- list.files("Data/neutral", pattern = "^neutral_sim_[0-9]+\\.rda$", full.names = TRUE)
  }
  if (length(files) == 0) {
    stop("No neutral_sim_*.rda files found in current directory or Data/neutral.")
  }

  combined_results <- list() #create your list output here to return
  sizes <- c(500, 1000, 2500, 5000)
  sum_list <- vector("list", length(sizes))
  n_list <- integer(length(sizes))

  for (file in files) {
    env <- new.env()
    load(file, envir = env)
    if (!all(c("abundance_list", "size", "burn_in_generations", "interval_oct") %in% ls(env))) {
      next
    }

    size_value <- as.numeric(get("size", envir = env))
    size_idx <- match(size_value, sizes)
    if (is.na(size_idx)) {
      next
    }

    abundance_list <- get("abundance_list", envir = env)
    burn_in_generations <- as.numeric(get("burn_in_generations", envir = env))
    interval_oct <- as.numeric(get("interval_oct", envir = env))
    sampled_generations <- seq_along(abundance_list) * interval_oct
    keep_idx <- which(sampled_generations > burn_in_generations)

    for (i in keep_idx) {
      oct <- abundance_list[[i]]
      if (is.null(sum_list[[size_idx]])) {
        sum_list[[size_idx]] <- oct
      } else {
        sum_list[[size_idx]] <- sum_vect(sum_list[[size_idx]], oct)
      }
      n_list[size_idx] <- n_list[size_idx] + 1L
    }
  }

  if (any(n_list == 0)) {
    stop("Some community sizes have no post-burn-in octave data.")
  }

  for (i in seq_along(sizes)) {
    combined_results[[i]] <- sum_list[[i]] / n_list[i]
  }

  # save results to an .rda file
  save(combined_results, file = "Data/neutral/combined_results.rda")
  combined_results
}

plot_neutral_cluster_results <- function(){

    # load combined_results from your rda file
  combined_file <- "Data/neutral/combined_results.rda"
  if (!file.exists(combined_file) && file.exists("combined_results.rda")) {
    combined_file <- "combined_results.rda"
  }
  if (!file.exists(combined_file)) {
    stop("Run process_neutral_cluster_results() first.")
  }
  env <- new.env()
  load(combined_file, envir = env)
  combined_results <- get("combined_results", envir = env)
  sizes <- c(500, 1000, 2500, 5000)
  
  if (!dir.exists("Results")) {
    dir.create("Results", recursive = TRUE)
  }
  png(filename = "Results/plot_neutral_cluster_results.png", width = 600, height = 400)
    # plot your graph here
    old_par <- par(no.readonly = TRUE)
    par(mfrow = c(2, 2))
    for (i in seq_along(sizes)) {
      barplot(combined_results[[i]],
              main = paste("Size =", sizes[i]),
              xlab = "Octave class", ylab = "Mean species count")
    }
    par(old_par)
    Sys.sleep(0.1)
    dev.off()
    
    return(combined_results)
}


# Challenge questions - these are substantially harder and worth fewer marks.
# I suggest you only attempt these if you've done all the main questions. 

# Challenge question A
Challenge_A <- function(){
  files <- list.files("Data/demographic", pattern = "^demographic_sim_[0-9]+\\.rda$", full.names = TRUE)
  if (length(files) == 0) {
    stop("No demographic_sim_*.rda files found in Data/demographic.")
  }

  get_iter <- function(path) {
    as.integer(sub("^.*demographic_sim_([0-9]+)\\.rda$", "\\1", path))
  }
  files <- files[!is.na(get_iter(files)) & get_iter(files) >= 1 & get_iter(files) <= 100]
  if (length(files) == 0) {
    stop("No valid demographic_sim_1..100.rda files found.")
  }

  id_to_label <- function(id, iter) {
    if (is.na(id)) {
      if (iter <= 25) {
        return("large adult")
      }
      if (iter <= 50) {
        return("small adult")
      }
      if (iter <= 75) {
        return("large mixed")
      }
      return("small mixed")
    }
    labels <- c("large adult", "small adult", "large mixed", "small mixed")
    labels[id]
  }

  df_list <- vector("list", 150L * length(files))
  df_idx <- 0L
  simulation_number <- 0L

  for (file in files) {
    iter <- get_iter(file)
    env <- new.env()
    load(file, envir = env)

    if (!exists("results_list", envir = env)) {
      next
    }
    results_list <- get("results_list", envir = env)
    if (!is.list(results_list)) {
      next
    }

    condition_id <- NA_integer_
    if (exists("initial_condition_id", envir = env)) {
      condition_id <- as.integer(get("initial_condition_id", envir = env))
      if (!condition_id %in% 1:4) {
        condition_id <- NA_integer_
      }
    }
    initial_condition <- id_to_label(condition_id, iter)

    for (sim in results_list) {
      if (!is.numeric(sim)) {
        next
      }
      simulation_number <- simulation_number + 1L
      df_idx <- df_idx + 1L
      df_list[[df_idx]] <- data.frame(
        simulation_number = simulation_number,
        initial_condition = initial_condition,
        time_step = seq_along(sim) - 1L,
        population_size = as.numeric(sim),
        stringsAsFactors = FALSE
      )
    }
  }

  if (df_idx == 0) {
    stop("No valid simulation time series found in demographic .rda files.")
  }
  population_size_df <- do.call(rbind, df_list[seq_len(df_idx)])
  time_step <- population_size <- simulation_number <- initial_condition <- NULL

  png(filename = "Results/Challenge_A.png", width = 800, height = 500)
  suppressMessages(library(ggplot2))
  print(
    ggplot(
      population_size_df,
      aes(x = time_step, y = population_size, group = simulation_number, colour = initial_condition)
    ) +
      geom_line(alpha = 0.1) +
      labs(x = "Time step", y = "Population size", colour = "Initial condition") +
      theme_minimal()
  )
  Sys.sleep(0.1)
  dev.off()

  population_size_df
}

# Challenge question B
Challenge_B <- function() {
  speciation_rate <- 0.1
  size <- 100
  duration <- 2200
  repeats <- 30

  run_replicates <- function(initial_community) {
    series_mat <- matrix(0, nrow = repeats, ncol = duration + 1)
    for (i in seq_len(repeats)) {
      series_mat[i, ] <- neutral_time_series_speciation(initial_community,
                                                        speciation_rate, duration)
    }
    series_mat
  }
  
  series_max <- run_replicates(init_community_max(size))
  series_min <- run_replicates(init_community_min(size))
  
  mean_max <- colMeans(series_max)
  mean_min <- colMeans(series_min)
  
  z <- stats::qnorm(0.986)
  se_max <- apply(series_max, 2, sd) / sqrt(repeats)
  se_min <- apply(series_min, 2, sd) / sqrt(repeats)

  upper_max <- mean_max + z * se_max
  lower_max <- mean_max - z * se_max
  upper_min <- mean_min + z * se_min
  lower_min <- mean_min - z * se_min

  png(filename = "Results/Challenge_B.png", width = 800, height = 500)
  plot(0:duration, mean_max, type = "l", col = "blue", lwd = 2,
       xlab = "Generation", ylab = "Species Richness",
       main = "Mean species richness with 97.2% CI",
       ylim = range(c(lower_min, upper_max)))
  lines(0:duration, mean_min, col = "red", lwd = 2)
  lines(0:duration, upper_max, col = "blue", lty = 2)
  lines(0:duration, lower_max, col = "blue", lty = 2)
  lines(0:duration, upper_min, col = "red", lty = 2)
  lines(0:duration, lower_min, col = "red", lty = 2)
  legend("topright", legend = c("Max init", "Min init"),
         col = c("blue", "red"), lwd = 2)
  Sys.sleep(0.1)
  dev.off()

  estimate_equilibrium <- function(series) {
    window <- 200
    target <- mean(tail(series, window))
    tol <- 0.02 * target
    smooth <- as.numeric(stats::filter(series, rep(1 / 51, 51), sides = 1))
    idx <- which(!is.na(smooth) & abs(smooth - target) <= tol)
    if (length(idx) == 0) {
      return(duration)
    }
    idx[1] - 1
  }
  eq_max <- estimate_equilibrium(mean_max)
  eq_min <- estimate_equilibrium(mean_min)
  eq_gen <- max(eq_max, eq_min)

  paste(
    "Using 30 replicate simulations per initial condition and a 97.2% confidence interval,",
    "the system appears to reach dynamic equilibrium at approximately generation",
    eq_gen, "(max-init:", eq_max, ", min-init:", eq_min, ")."
  )
}

# Challenge question C
Challenge_C <- function() {
  speciation_rate <- 0.1
  size <- 100
  duration <- 500
  repeats <- 20

  richness_levels <- unique(round(seq(2, size, length.out = 8)))

  make_random_community <- function(size, richness) {
    sample.int(richness, size, replace = TRUE)
  }

  avg_series <- function(richness) {
    mat <- matrix(0, nrow = repeats, ncol = duration + 1)
    for (i in seq_len(repeats)) {
      community <- make_random_community(size, richness)
      mat[i, ] <- neutral_time_series_speciation(community, speciation_rate, duration)
    }
    colMeans(mat)
  }
  
  series_list <- lapply(richness_levels, avg_series)

  png(filename = "Results/Challenge_C.png", width = 800, height = 500)
  plot(0:duration, series_list[[1]], type = "l",
       xlab = "Generation", ylab = "Species Richness",
       main = "Averaged Time Series for Different Initial Richness",
       ylim = range(unlist(series_list)))
  
  cols <- rainbow(length(series_list))
  for (i in seq_along(series_list)) {
    lines(0:duration, series_list[[i]], col = cols[i], lwd = 2)
  }
  legend("topright", legend = richness_levels, col = cols, lwd = 2,
         title = "Initial Richness")
  Sys.sleep(0.1)
  dev.off()

  invisible(list(initial_richness = richness_levels, mean_series = series_list))
}

# Challenge question D
Challenge_D <- function() {
  files <- list.files("Data/neutral", pattern = "^neutral_sim_[0-9]+\\.rda$", full.names = TRUE)
  if (length(files) == 0) {
    stop("No neutral_sim_*.rda files found in Data/neutral.")
  }

  get_iter <- function(path) {
    as.integer(sub("^.*neutral_sim_([0-9]+)\\.rda$", "\\1", path))
  }
  files <- files[!is.na(get_iter(files)) & get_iter(files) >= 1 & get_iter(files) <= 100]
  if (length(files) == 0) {
    stop("No valid neutral_sim_1..100.rda files found.")
  }

  sizes <- c(500, 1000, 2500, 5000)
  sum_by_size <- vector("list", length(sizes))
  n_by_size <- vector("list", length(sizes))

  for (file in files) {
    env <- new.env()
    load(file, envir = env)
    if (!all(c("time_series", "size", "interval_rich") %in% ls(env))) {
      next
    }
    size_value <- as.numeric(get("size", envir = env))
    idx <- match(size_value, sizes)
    if (is.na(idx)) {
      next
    }

    time_series <- as.numeric(get("time_series", envir = env))
    interval_rich <- as.integer(get("interval_rich", envir = env))
    if (length(time_series) == 0 || interval_rich <= 0) {
      next
    }
    generations <- seq_along(time_series) * interval_rich
    max_gen <- max(generations)

    if (is.null(sum_by_size[[idx]])) {
      sum_by_size[[idx]] <- rep(0, max_gen)
      n_by_size[[idx]] <- rep(0, max_gen)
    } else if (length(sum_by_size[[idx]]) < max_gen) {
      extend <- max_gen - length(sum_by_size[[idx]])
      sum_by_size[[idx]] <- c(sum_by_size[[idx]], rep(0, extend))
      n_by_size[[idx]] <- c(n_by_size[[idx]], rep(0, extend))
    }

    sum_by_size[[idx]][generations] <- sum_by_size[[idx]][generations] + time_series
    n_by_size[[idx]][generations] <- n_by_size[[idx]][generations] + 1L
  }

  mean_series_by_size <- vector("list", length(sizes))
  generation_by_size <- vector("list", length(sizes))
  recommended_burn_in <- rep(NA_real_, length(sizes))

  estimate_burn_in <- function(mean_series, generations) {
    if (length(mean_series) < 30) {
      return(max(generations))
    }
    tail_window <- max(20, floor(length(mean_series) * 0.1))
    target <- mean(tail(mean_series, tail_window))
    tol <- 0.02 * target
    ok <- abs(mean_series - target) <= tol
    streak <- 0L
    required_streak <- max(20L, floor(length(mean_series) * 0.05))
    for (i in seq_along(ok)) {
      if (ok[i]) {
        streak <- streak + 1L
        if (streak >= required_streak) {
          return(generations[i - required_streak + 1L])
        }
      } else {
        streak <- 0L
      }
    }
    max(generations)
  }

  for (i in seq_along(sizes)) {
    valid <- !is.null(sum_by_size[[i]]) && !is.null(n_by_size[[i]])
    if (!valid) {
      next
    }
    generations <- which(n_by_size[[i]] > 0)
    if (length(generations) == 0) {
      next
    }
    mean_series <- sum_by_size[[i]][generations] / n_by_size[[i]][generations]
    generation_by_size[[i]] <- generations
    mean_series_by_size[[i]] <- mean_series
    recommended_burn_in[i] <- estimate_burn_in(mean_series, generations)
  }

  valid_idx <- which(!vapply(mean_series_by_size, is.null, logical(1)))
  if (length(valid_idx) == 0) {
    stop("No valid richness time series found in neutral cluster files.")
  }

  ymax <- max(unlist(mean_series_by_size[valid_idx]))
  xmax <- max(unlist(generation_by_size[valid_idx]))

  png(filename = "Results/Challenge_D.png", width = 800, height = 500)
  plot(0, 0, type = "n", xlim = c(0, xmax), ylim = c(0, ymax),
       xlab = "Generation", ylab = "Mean species richness",
       main = "Mean richness during burn-in by community size")
  cols <- c("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728")
  for (i in valid_idx) {
    lines(generation_by_size[[i]], mean_series_by_size[[i]], col = cols[i], lwd = 2)
  }
  legend("bottomright", legend = paste("Size", sizes[valid_idx]), col = cols[valid_idx], lwd = 2)
  Sys.sleep(0.1)
  dev.off()

  recommendation <- data.frame(
    size = sizes,
    recommended_burn_in = recommended_burn_in,
    stringsAsFactors = FALSE
  )
  save(recommendation, file = "Data/neutral/Challenge_D_recommendation.rda")
  recommendation
}

# Challenge question E
Challenge_E <- function() {
  coalescence_sim <- function(size, speciation_rate) {
    lineages <- rep(1, size)
    abundances <- numeric(0)
    n <- size
    theta <- speciation_rate * (size - 1) / (1 - speciation_rate)
    
    while (n > 1) {
      j <- sample.int(n, 1)
      randnum <- runif(1)
      if (randnum < (theta / (theta + n - 1))) {
        abundances <- c(abundances, lineages[j])
      } else {
        i <- sample.int(n - 1, 1)
        if (i >= j) {
          i <- i + 1
        }
        lineages[i] <- lineages[i] + lineages[j]
      }
      lineages <- lineages[-j]
      n <- n - 1
    }
    abundances <- c(abundances, lineages[1])
    abundances
  }

  speciation_rate <- get_personal_speciation_rate()
  sizes <- c(500, 1000, 2500, 5000)

  coalescence_repeats <- 25
  start_time <- proc.time()[3]
  coalescence_results <- vector("list", length(sizes))
  for (i in seq_along(sizes)) {
    total_oct <- numeric(0)
    for (rep_id in seq_len(coalescence_repeats)) {
      total_oct <- sum_vect(total_oct, octaves(coalescence_sim(sizes[i], speciation_rate)))
    }
    coalescence_results[[i]] <- total_oct / coalescence_repeats
  }
  coalescence_cpu_hours <- (proc.time()[3] - start_time) / 3600

  files <- list.files("Data/neutral", pattern = "^neutral_sim_[0-9]+\\.rda$", full.names = TRUE)
  get_iter <- function(path) {
    as.integer(sub("^.*neutral_sim_([0-9]+)\\.rda$", "\\1", path))
  }
  files <- files[!is.na(get_iter(files)) & get_iter(files) >= 1 & get_iter(files) <= 100]
  if (length(files) == 0) {
    stop("No valid neutral_sim_1..100.rda files found for cluster comparison.")
  }

  sum_list <- vector("list", length(sizes))
  n_list <- integer(length(sizes))
  cluster_cpu_hours <- 0

  for (file in files) {
    env <- new.env()
    load(file, envir = env)
    if (!all(c("abundance_list", "size", "burn_in_generations", "interval_oct") %in% ls(env))) {
      next
    }
    size_value <- as.numeric(get("size", envir = env))
    size_idx <- match(size_value, sizes)
    if (is.na(size_idx)) {
      next
    }

    abundance_list <- get("abundance_list", envir = env)
    burn_in_generations <- as.numeric(get("burn_in_generations", envir = env))
    interval_oct <- as.numeric(get("interval_oct", envir = env))
    sampled_generations <- seq_along(abundance_list) * interval_oct
    keep_idx <- which(sampled_generations > burn_in_generations)

    for (j in keep_idx) {
      oct <- abundance_list[[j]]
      if (is.null(sum_list[[size_idx]])) {
        sum_list[[size_idx]] <- oct
      } else {
        sum_list[[size_idx]] <- sum_vect(sum_list[[size_idx]], oct)
      }
      n_list[size_idx] <- n_list[size_idx] + 1L
    }

    if (exists("total_time", envir = env)) {
      cluster_cpu_hours <- cluster_cpu_hours + as.numeric(get("total_time", envir = env)) / 60
    }
  }

  if (any(n_list == 0)) {
    stop("Missing post-burn-in octave data for at least one community size.")
  }
  cluster_results <- lapply(seq_along(sizes), function(i) sum_list[[i]] / n_list[i])

  png(filename = "Results/Challenge_E.png", width = 900, height = 600)
  old_par <- par(no.readonly = TRUE)
  par(mfrow = c(2, 2))
  for (i in seq_along(sizes)) {
    co <- coalescence_results[[i]]
    cl <- cluster_results[[i]]
    max_len <- max(length(co), length(cl))
    co <- c(co, rep(0, max_len - length(co)))
    cl <- c(cl, rep(0, max_len - length(cl)))
    barplot(rbind(co, cl), beside = TRUE,
            main = paste("Size", sizes[i]),
            xlab = "Octave class", ylab = "Mean species count",
            legend.text = c("Coalescence", "Cluster"), args.legend = list(x = "topright", cex = 0.8))
  }
  par(old_par)
  Sys.sleep(0.1)
  dev.off()

  paste(
    "Coalescence simulations used", round(coalescence_cpu_hours, 4), "CPU hours, while the cluster runs used",
    round(cluster_cpu_hours, 2), "CPU hours in total (from saved total_time values).",
    "Coalescence is much faster because it samples ancestry backward and avoids",
    "simulating every birth-death event forward through time."
  )
}

