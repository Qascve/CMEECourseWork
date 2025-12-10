# PP_Regress.R
# Performs linear regressions for each Feeding Type × Life Stage combination
# and outputs both a PDF plot and a CSV table with regression statistics.

# Check if required packages are installed
if(!requireNamespace("ggplot2", quietly = TRUE)) {
  cat("Required package 'ggplot2' is not installed. Please install it using: install.packages('ggplot2')\n")
  quit(save = "no", status = 0)
}
if(!requireNamespace("dplyr", quietly = TRUE)) {
  cat("Required package 'dplyr' is not installed. Please install it using: install.packages('dplyr')\n")
  quit(save = "no", status = 0)
}
if(!requireNamespace("here", quietly = TRUE)) {
  cat("Required package 'here' is not installed. Please install it using: install.packages('here')\n")
  quit(save = "no", status = 0)
}

# Load required libraries (suppress startup messages)
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(here))

# Import dataset (relative path: script in /code, data in ../data)
data <- suppressMessages(read.csv(here("week3", "data", "EcolArchives-E089-51-D1.csv")))

# Remove missing values in relevant columns
data <- data %>%
  filter(!is.na(Prey.mass),
         !is.na(Predator.mass),
         !is.na(Type.of.feeding.interaction),
         !is.na(Predator.lifestage))

# Initialize dataframe for regression results
results <- data.frame(
  FeedingType = character(),
  LifeStage = character(),
  Slope = numeric(),
  Intercept = numeric(),
  R_squared = numeric(),
  F_statistic = numeric(),
  P_value = numeric(),
  stringsAsFactors = FALSE
)

# Ensure results directory exists
results_dir <- here("week3", "results")
if (!dir.exists(results_dir)) {
  dir.create(results_dir, recursive = TRUE)
}

pdf(here("week3", "results", "PP_Regress.pdf"), width = 10, height = 8)

# Create the figure
p <- ggplot(data, aes(x = log(Prey.mass), y = log(Predator.mass),
                      color = Type.of.feeding.interaction)) +
  geom_point(alpha = 0.6) +
  facet_wrap(~Predator.lifestage) +
  geom_smooth(method = "lm", se = TRUE) +
  labs(
    x = "Log Prey Mass",
    y = "Log Predator Mass",
    color = "Feeding Type"
  ) +
  theme_bw() +
  theme(legend.position = "right")

# Write the plot to PDF (suppress warnings from geom_smooth)
suppressWarnings(print(p))

# Close PDF
invisible(dev.off())

# Perform regressions for each combination of Feeding Type × Life Stage
for (stage in unique(data$Predator.lifestage)) {
  for (type in unique(data$Type.of.feeding.interaction)) {
    subset_data <- data %>%
      filter(Predator.lifestage == stage,
             Type.of.feeding.interaction == type)
    
    # Skip if insufficient data
    if (nrow(subset_data) > 2) {
      model <- lm(log(Predator.mass) ~ log(Prey.mass), data = subset_data)
      summary_stats <- summary(model)
      
      # Extract F-statistic and p-value safely
      if (!is.null(summary_stats$fstatistic)) {
        F_val <- summary_stats$fstatistic[1]
        P_val <- pf(F_val,
                    summary_stats$fstatistic[2],
                    summary_stats$fstatistic[3],
                    lower.tail = FALSE)
      } else {
        F_val <- NA
        P_val <- NA
      }
      
      # Append results
      results <- rbind(results, data.frame(
        FeedingType = type,
        LifeStage = stage,
        Slope = coef(model)[2],
        Intercept = coef(model)[1],
        R_squared = summary_stats$r.squared,
        F_statistic = F_val,
        P_value = P_val,
        stringsAsFactors = FALSE
      ))
    }
  }
}

# Save regression summary to CSV
write.csv(results, here("week3", "results", "PP_Regress_Results.csv"), row.names = FALSE)
# Print completion message
cat("Linear regressions complete!\n")
cat("Saved outputs:\n")
cat(here("week3", "results", "PP_Regress.pdf"), "\n")
cat(here("week3", "results", "PP_Regress_Results.csv"), "\n")