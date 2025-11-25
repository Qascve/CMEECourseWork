library(ggplot2)
suppressPackageStartupMessages(library(here))

# Check if input file exists
file_path <- here("week4", "data", "Results.txt")
if (!file.exists(file_path)) {
  cat("Input file 'Results.txt' not found in data directory.\n")
  quit(save = "no", status = 0)
} else {
  # Read data from file
  a <- read.table(file_path, header = TRUE)
}

# Add ymin column
a$ymin <- rep(0, nrow(a))

# Base plot
p <- ggplot(a)

# First linerange
p <- p + geom_linerange(data = a, aes(x = x, ymin = ymin, ymax = y1),
                        colour = "#E69F00", linewidth = 0.5, alpha = 0.5, show.legend = FALSE)

# Second linerange
p <- p + geom_linerange(data = a, aes(x = x, ymin = ymin, ymax = y2),
                        colour = "#56B4E9", linewidth = 0.5, alpha = 0.5, show.legend = FALSE)

# Third linerange
p <- p + geom_linerange(data = a, aes(x = x, ymin = ymin, ymax = y3),
                        colour = "#D55E00", linewidth = 0.5, alpha = 0.5, show.legend = FALSE)

# Add text labels (only for non-NA labels)
p <- p + geom_text(data = a[!is.na(a$Label), ], aes(x = x, y = -500, label = Label))

# Axis labels and theme
p <- p + scale_x_continuous("My x axis", breaks = seq(3, 5, by = 0.05)) +
         scale_y_continuous("My y axis") +
         theme_bw() +
         theme(legend.position = "none")

# Save to PDF
output_path <- here("week4", "results", "MyBars.pdf")
pdf(output_path, width = 8, height = 6)
print(p)
dev.off()

cat("Plot saved to:", output_path, "\n")
