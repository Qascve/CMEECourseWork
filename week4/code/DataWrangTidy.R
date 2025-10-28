################################################################
################## Wrangling the Pound Hill Dataset (tidyverse) #
################################################################

library(tidyverse)  # includes dplyr, tidyr, readr, ggplot2, etc.
library(here)       # for constructing file paths

############# Load the dataset ###############
# header = FALSE because the raw data don't have real headers
MyData <- read_csv(here("week4", "data", "PoundHillData.csv"), col_names = FALSE)

# header = TRUE because metadata has real headers
MyMetaData <- read_csv2(here("week4", "data", "PoundHillMetaData.csv"))

############# Inspect the dataset ###############
head(MyData)
dim(MyData)
glimpse(MyData)

############# Transpose ###############
# convert tibble to matrix for transposing
MyData <- t(as.matrix(MyData))
head(MyData)
dim(MyData)

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
glimpse(data)
head(data)
dim(data)
