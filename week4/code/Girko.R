library(ggplot2)
library(here)

# Build a function that returns an ellipse (predicted eigenvalue boundary)
build_ellipse <- function(hradius, vradius){
  npoints = 250
  a <- seq(0, 2 * pi, length = npoints + 1)
  x <- hradius * cos(a)
  y <- vradius * sin(a)
  return(data.frame(x = x, y = y))
}

# Set matrix
N <- 250
M <- matrix(rnorm(N * N), N, N)

eigvals <- eigen(M)$values
# Build dataframe
eigDF <- data.frame(
  "Real" = Re(eigvals),
  "Imaginary" = Im(eigvals)
)

# Compute theoretical radius
radius <- sqrt(N)

# Build dataframe for the ellipse boundary
ellDF <- build_ellipse(radius, radius)
names(ellDF) <- c("Real", "Imaginary")

# Create plot
p <- ggplot(eigDF, aes(x = Real, y = Imaginary)) +
  geom_point(shape = I(MyBars.R3)) +
  geom_hline(aes(yintercept = 0)) +
  geom_vline(aes(xintercept = 0)) +
  geom_polygon(
    data = ellDF,
    aes(x = Real, y = Imaginary, alpha = 1/20, fill = "red")
  ) +
  theme(legend.position = "none") +
  ggtitle("Girko Circular Law")

# Save plot to PDF
pdf(here("week4", "results", "Girko.pdf"), width = 8, height = 8)
print(p)
dev.off()

print("Complete")