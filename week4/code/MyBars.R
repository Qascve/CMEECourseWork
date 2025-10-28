library(ggplot2)
library(here)

file_path <- here("week4", "data", "Results.txt")
if (!file.exists(file_path)) {
  warning("Warning: '../data/Results.txt' not found. Skipping plot creation.")
  quit(status = 0)
}


a <- read.table(file_path, header = TRUE)


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

# Add text labels
p <- p + geom_text(data = a, aes(x = x, y = -500, label = Label))

# Axis labels and theme
p <- p + scale_x_continuous("My x axis", breaks = seq(3, 5, by = 0.05)) +
         scale_y_continuous("My y axis") +
         theme_bw() +
         theme(legend.position = "none")

# Save to PDF
pdf("../results/MyBars.pdf")
print(p)
dev.off()
