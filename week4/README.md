# Week 4

Directory contains Week 4 CMEECourseWork (Statistics in R and some Python).

## Structure

- **code:** All R and Python scripts

- **data:** Data files for  analysis

- **results:** Output files from scripts (only .gitkeep tracked)

## Scripts in week4

##### Data Wrangling (R)
* `DataWrang.R`: 
  - Data manipulation using base R. Works with PoundHill ecological dataset, demonstrates transpose, subsetting, and reshaping

* `DataWrangTidy.R`:
  - Data wrangling using tidyverse (dplyr, tidyr). Modern approach to data transformation and tidying

##### Statistical Analysis (R)
* `PP_Regress.R`:
  - Predator-prey mass relationship analysis. Performs linear regressions by feeding type and life stage, generates faceted plots and statistical summary CSV

* `PP_Dists.R`:
  - Distribution analysis of predator-prey data. Explores data distributions and statistical properties

* `GPDD_Data.R`:
  - Maps Global Population Dynamics Database locations. Creates world map with data points, includes geographic bias analysis

* `MyBars.R`:
  - Bar plot annotation examples. Creates customized bar plots with multiple line ranges and saves to PDF

* `Girko.R`:
  - Girko's circular law visualization. Demonstrates eigenvalue distribution of random matrices

* `SQLinR.R`:
  - SQL database operations in R. Shows how to use SQL queries within R environment

##### Numerical Methods (Python)
* `LV1.py`:
  - Lotka-Volterra predator-prey model implementation. Numerically solves differential equations and visualizes population dynamics

* `LV2.py`:
  - Extended Lotka-Volterra model. Advanced version with additional parameters or scenarios

##### Performance Profiling (Python)
* `profileme.py`:
  - Code profiling examples. Demonstrates how to identify performance bottlenecks

* `profileme2.py`:
  - Advanced profiling techniques. Compares different optimization approaches

## Data Files
* `EcolArchives-E089-51-D1.csv`:
  - Large ecological dataset (~35K rows) with predator-prey mass relationships. Used by PP_Regress.R and PP_Dists.R

* `GPDDFiltered.RData`:
  - Global Population Dynamics Database. Contains species population time series locations (147 locations)

* `PoundHillData.csv`:
  - Ecological community data matrix from Pound Hill. Used in data wrangling exercises

* `PoundHillMetaData.csv`:
  - Metadata for Pound Hill dataset. Describes species and sampling information

