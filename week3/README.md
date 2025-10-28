# Week 3

Directory contains Week 3 CMEECourseWork (R Programming Week).

## Structure

- **code:** All R scripts and related files

- **data:** Data files for R analysis

- **results:** Output files from scripts (only .gitkeep tracked)

- **sandbox:** Testing and temporary files

## Scripts in week3

##### Basic R Scripts
* `boilerplate.R`: 
  - Basic R script template with function structure. Demonstrates function arguments, type checking, and return values

* `basic_io.R`:
  - File input/output operations in R. Shows reading and writing text files

* `read_csv.R`:
  - CSV file handling examples. Demonstrates reading and manipulating CSV data

##### Control Flow Scripts
* `control_flow.R`:
  - Basic control structures in R. Includes if-else statements, for loops, and conditional execution

* `R_conditionals.R`:
  - Advanced conditional statement examples. Shows nested conditions and logical operators

* `break.R`:
  - Using break statements in loops. Demonstrates early loop termination

* `next.R`:
  - Using next statements to skip iterations. Shows loop control flow

* `try.R`:
  - Error handling with try-catch blocks. Demonstrates exception handling in R

* `browse.R`:
  - Debugging techniques using browser(). Shows interactive debugging methods

##### Apply Functions
* `apply1.R`:
  - Basic apply family function examples. Shows apply, sapply, and lapply usage

* `apply2.R`:
  - Advanced apply function applications. Demonstrates complex data transformations

##### Performance Optimization
* `Vectorize1.R`:
  - Vectorization basics and performance comparison. Shows loops vs vectorized operations

* `Vectorize2.R`:
  - Advanced vectorization techniques. Demonstrates efficiency improvements

* `preallocate.R`:
  - Memory preallocation importance. Compares preallocated vs growing vectors

* `sample.R`:
  - Sampling and random number generation. Shows different sampling techniques

##### Data Analysis Scripts
* `TreeHeight.R`:
  - Calculates tree heights from angle and distance measurements. Uses trigonometric formulas and reads from trees.csv

* `Florida.R`:
  - Temperature data analysis and correlation. Generates Florida analysis plots and Florida.csv results

* `Ricker.R`:
  - Ricker model implementation for population dynamics. Demonstrates ecological modeling

* `PP_Regress.R`:
  - Predator-prey regression analysis practice.

##### LaTeX Integration
* `Florida.tex`:
  - LaTeX document for Florida temperature analysis. Shows R and LaTeX integration

* `Florida.pdf`:
  - Compiled PDF output from Florida.tex

## Data Files
* `trees.csv`:
  - Tree measurement data including angles and distances. Used by TreeHeight.R

* `KeyWestAnnualMeanTemperature.RData`:
  - Historical temperature data from Key West. Used in Florida temperature analysis
