library(tidyverse)
library(here)


# Load data
data <- read.csv(here("week4", "data", "EcolArchives-E089-51-D1.csv"))


# Create log-transformed columns
data <- data %>%
  mutate(
    logPredMass = log10(Predator.mass),
    logPreyMass = log10(Prey.mass),
    logSizeRatio = log10(Prey.mass / Predator.mass)
  )

# Get all feeding types
feeding_types <- unique(data$Type.of.feeding.interaction)


# Plot: Predator mass distributions
pdf(here("week4", "results", "Pred_Subplots.pdf"),width=10, height=12)
par(mfrow = c(3, 2))  # adjust layout based on number of feeding types
for (ftype in feeding_types) {
  subset_data <- subset(data, Type.of.feeding.interaction == ftype)
  hist(
    subset_data$logPredMass,
    main = paste("Predator mass:", ftype),
    xlab = "log10(Predator mass)",
    col = "lightblue",
    border = "white"
  )
}
dev.off()


# Plot: Prey mass distributions
pdf(here("week4", "results", "Prey_Subplots.pdf"),width=10, height=12)
par(mfrow = c(3, 2))
for (ftype in feeding_types) {
  subset_data <- subset(data, Type.of.feeding.interaction == ftype)
  hist(
    subset_data$logPreyMass,
    main = paste("Prey mass:", ftype),
    xlab = "log10(Prey mass)",
    col = "lightgreen",
    border = "white"
  )
}
dev.off()


# Plot: Size ratio distributions

pdf(here("week4", "results", "SizeRatio_Subplots.pdf"),width=10, height=12)
par(mfrow = c(3, 2))
for (ftype in feeding_types) {
  subset_data <- subset(data, Type.of.feeding.interaction == ftype)
  hist(
    subset_data$logSizeRatio,
    main = paste("Size ratio:", ftype),
    xlab = "log10(Prey/Predator mass)",
    col = "lightcoral",
    border = "white"
  )
}
dev.off()


# Compute mean and median log values by feeding type

results <- data %>%
  group_by(Type.of.feeding.interaction) %>%
  summarise(
    MeanPredMass = mean(logPredMass, na.rm = TRUE),
    MedianPredMass = median(logPredMass, na.rm = TRUE),
    MeanPreyMass = mean(logPreyMass, na.rm = TRUE),
    MedianPreyMass = median(logPreyMass, na.rm = TRUE),
    MeanSizeRatio = mean(logSizeRatio, na.rm = TRUE),
    MedianSizeRatio = median(logSizeRatio, na.rm = TRUE)
  )


# Save results to CSV
write.csv(results, here("week4", "results", "PP_Results.csv"), row.names = FALSE)

print("Analysis complete")