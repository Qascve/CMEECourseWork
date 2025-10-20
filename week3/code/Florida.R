script_path <- dirname(sys.frame(1)$ofile)
setwd(script_path)

rm(list=ls())

load("../data/KeyWestAnnualMeanTemperature.RData")

observed_cor <- cor(ats$Year, ats$Temp) # calculate correlation

repeatTimes <- 1000
random_cors <- numeric(repeatTimes)
for(i in 1:repeatTimes) {
    shuffled_temps <- sample(ats$Temp) # shuffle temperatures
    random_cors[i] <- cor(ats$Year, shuffled_temps) # calculate correlation with shuffled temps
}
# Now random_cors contains 1000 correlation coefficients from the permutations

p_value <- sum(abs(random_cors) >= abs(observed_cor)) / repeatTimes

png("../results/Florida_analysis.png", width = 800, height = 800)
par(mfrow = c(2,1))

plot(ats$Year, ats$Temp, 
     main = "Temperature Over Time in Key West",
     xlab = "Year", ylab = "Temperature (°C)")
abline(lm(Temp ~ Year, data = ats), col = "red")

hist(random_cors, breaks = 50,
     main = "Distribution of Random Correlations",
     xlab = "Correlation Coefficient")
abline(v = observed_cor, col = "red", lwd = 2)

dev.off()

cat("\nresults：\n")
cat("correlation：", round(observed_cor, 4), "\n")
cat("p value：", round(p_value, 4), "\n")