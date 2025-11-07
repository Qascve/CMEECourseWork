################################################################
################## Wrangling the Pound Hill Dataset (tidyverse) #
################################################################

# Check if required packages are installed
if(!requireNamespace("tidyverse", quietly = TRUE)) {
  cat("Error: 'tidyverse' package is not installed.\n")
  quit(save = "no", status = 0)
}
if(!requireNamespace("here", quietly = TRUE)) {
  cat("Error: 'here' package is not installed.\n")
  quit(save = "no", status = 0)
}

# Load required packages
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(here))
options(readr.show_col_types = FALSE)


############# Load the dataset ###############
# header = FALSE because the raw data don't have real headers
MyData <- suppressMessages(read_csv(here("week4", "data", "PoundHillData.csv"), col_names = FALSE))

# header = TRUE because metadata has real headers
MyMetaData <- suppressMessages(read_csv2(here("week4", "data", "PoundHillMetaData.csv")))

############# Inspect the dataset ###############
# invisible(head(MyData))
# invisible(dim(MyData))
# invisible(glimpse(MyData))

############# Transpose ###############
# convert tibble to matrix for transposing
MyData <- t(as.matrix(MyData))
# invisible(head(MyData))
# invisible(dim(MyData))

############# Replace species absences with zeros ###############
MyData[MyData == ""] <- 0

############# Convert raw matrix to data frame ###############
TempData <- as_tibble(MyData[-1, ], .name_repair = "minimal")
colnames(TempData) <- MyData[1, ]

############# Convert from wide to long format ###############
data <- TempData %>%
  pivot_longer(
    cols = -c(Cultivation, Block, Plot, Quadrat),
    names_to = "Species",
    values_to = "Count"
  )

############# Change data types ###############
data <- data %>%
  mutate(
    Cultivation = as.factor(Cultivation),
    Block = as.factor(Block),
    Plot = as.factor(Plot),
    Quadrat = as.factor(Quadrat),
    Count = as.integer(Count)
  )

############# Inspect final dataset ###############
# invisible(glimpse(data))
# invisible(head(data))
# invisible(dim(data))
print("DataWrangTidy.R completed successfully")