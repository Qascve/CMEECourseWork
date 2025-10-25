script_path <- dirname(sys.frame(1)$ofile)
setwd(script_path)

rm(list=ls())

load("../data/KeyWestAnnualMeanTemperature.RData")

set.seed(0)

observed_cor <- cor(ats$Year, ats$Temp) # calculate correlation

repeatTimes <- 10000
random_cors <- numeric(repeatTimes)
for(i in 1:repeatTimes) {
     shuffled_temps <- sample(ats$Temp) # shuffle temperatures
    random_cors[i] <- cor(ats$Year, shuffled_temps) # calculate correlation with shuffled temps
}
# Now random_cors contains 10000 correlation coefficients from the permutations

p_value <- sum(abs(random_cors) >= abs(observed_cor)) / repeatTimes

pdf("../results/Florida_analysis1.pdf", width = 8, height = 6)
plot(ats$Year, ats$Temp, 
     main = sprintf("Temperature Trends in Key West (correlation = %.3f)", observed_cor),
     xlab = "Year", 
     ylab = "Temperature (°C)",
     pch = 16,
     col = "darkblue")
abline(lm(Temp ~ Year, data = ats), col = "red", lwd = 2)
dev.off()

pdf("../results/Florida_analysis2.pdf", width = 8, height = 6)
hist(random_cors,
     main = "Distribution of Random Correlations",
     xlab = "Correlation Coefficient")
abline(v = observed_cor, col = "red", lwd = 2)
dev.off()

pdf("../results/Florida_analysis3.pdf", width = 8, height = 6)
baseline_temp <- mean(ats$Temp[1:5]) 
temp_changes <- ats$Temp - baseline_temp

plot(ats$Year, temp_changes,
     type = "b",
     main = sprintf("Temperature Changes Relative to 1901-1905 Average (%.2f°C)", 
                   baseline_temp),
     xlab = "Year",
     ylab = "Temperature Change (°C)",
     col = "blue",
     pch = 16)
lines(lowess(ats$Year, temp_changes), col = "red", lwd = 2)
legend("topleft", 
       legend = c("Annual change", "Smoothed trend"),
       col = c("blue", "red", "red"),
       lty = c(1, 1, 2),
       pch = c(16, NA, NA),
       bty = "n")

dev.off()

#Save results to CSV files
results_df <- data.frame(Observed_Correlation = observed_cor, P_Value = p_value)
write.csv(results_df, "../results/Florida.csv", row.names = FALSE)

# Print results
cat("\nresults：\n")
cat("correlation：", round(observed_cor, 4), "\n")
cat("p value：", round(p_value, 4), "\n")