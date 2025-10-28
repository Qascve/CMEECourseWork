# Load required libraries
library(ggplot2)
library(dplyr)
library(here)

MyDF <- read.csv(here("week4", "data", "EcolArchives-E089-51-D1.csv"), stringsAsFactors = FALSE)

# Data cleaning: remove rows with missing values in key columns
MyDF <- MyDF[complete.cases(MyDF[, c("Predator.mass", "Prey.mass", "Type.of.feeding.interaction", "Predator.lifestage")]), ]

# Filter out invalid mass values (zero or negative)
MyDF <- MyDF[MyDF$Predator.mass > 0 & MyDF$Prey.mass > 0, ]

# Faceted by feeding type, colored by predator life stage
p <- ggplot(MyDF, aes(x = Prey.mass, y = Predator.mass, color = Predator.lifestage)) +
  # Add semi-transparent points
  geom_point(alpha = 0.6, size = 1.5) +
  # Create separate panels for each feeding interaction type
  facet_grid(Type.of.feeding.interaction ~ ., scales = "fixed") +
  # Add regression lines with confidence intervals for each life stage
  geom_smooth(method = "lm", se = TRUE, linewidth = 0.8, alpha = 0.2, formula = y ~ x) +
  scale_x_log10(name = "Prey Mass in grams") +
  scale_y_log10(name = "Predator mass in grams", labels = scales::scientific) +
  # Use black and white theme
  theme_bw() +
  theme(
    strip.text.y = element_text(angle = 0, hjust = 0, size = 8),
    strip.background = element_rect(fill = "lightgray"),
    legend.position = "bottom",
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 8),
    axis.text = element_text(size = 8),
    axis.title = element_text(size = 10)
  ) +
  # Set legend title
  labs(color = "Predator.lifestage")

# Save the plot to PDF in the results directory
pdf(here("week4", "results", "PP_Regress.pdf"), width = 10, height = 12)
suppressWarnings(print(p))
invisible(dev.off())

results <- data.frame(
  Feeding.Type = character(),
  Predator.Lifestage = character(),
  Slope = numeric(),
  Intercept = numeric(),
  R.squared = numeric(),
  F.statistic = numeric(),
  P.value = numeric(),
  stringsAsFactors = FALSE
)

# Get all unique combinations of feeding types and life stages
feeding_types <- unique(MyDF$Type.of.feeding.interaction)
life_stages <- unique(MyDF$Predator.lifestage)

# Loop through all feeding type × life stage combinations
for (feeding in feeding_types) {
  for (stage in life_stages) {
    # Subset data for current combination
    subset_data <- MyDF[MyDF$Type.of.feeding.interaction == feeding & MyDF$Predator.lifestage == stage, ]

    # Only perform regression if there are at least 3 data points
    if (nrow(subset_data) >= 3) {
      # Fit linear model to log-transformed data
      # This fits: log(Predator.mass) ~ log(Prey.mass)
      model <- lm(log(Predator.mass) ~ log(Prey.mass), data = subset_data)
      
      # Get model summary# Initialize an empty dataframe to store regression results
      model_summary <- summary(model)
      
      # Extract regression coefficients
      intercept <- coef(model)[1]
      slope <- coef(model)[2]
      
      # Extract R-squared value
      r_squared <- model_summary$r.squared
      
      # Extract F-statistic
      f_statistic <- model_summary$fstatistic[1]
      
      # Calculate p-value from F-statistic
      p_value <- pf(model_summary$fstatistic[1], model_summary$fstatistic[2], model_summary$fstatistic[3], lower.tail = FALSE)
      
      # Append results to the dataframe
      results <- rbind(results, data.frame(
        Feeding.Type = feeding,
        Predator.Lifestage = stage,
        Slope = slope,
        Intercept = intercept,
        R.squared = r_squared,
        F.statistic = f_statistic,
        P.value = p_value,
        stringsAsFactors = FALSE
      ))
    }
  }
}

# Sort results by feeding type and life stage for better readability
results <- results[order(results$Feeding.Type, results$Predator.Lifestage), ]

# Save results to CSV file in the results directory
write.csv(results, here("week4", "results", "PP_Regress_Results.csv"), row.names = FALSE)