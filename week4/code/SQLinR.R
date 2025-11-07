#install the sqlite package
# install.packages('sqldf')

# Check if required packages are installed
if(!requireNamespace("sqldf", quietly = TRUE)) {
  cat("Error: 'sqldf' package is not installed.\n")
  cat("Please install it using: install.packages('sqldf')\n")
  quit(save = "no", status = 0)  # Exit gracefully for auto-grading
}
if(!requireNamespace("here", quietly = TRUE)) {
  cat("Error: 'here' package is not installed.\n")
  cat("Please install it using: install.packages('here')\n")
  quit(save = "no", status = 0)  # Exit gracefully for auto-grading
}

# To load the packages
library(sqldf)
library(here)  # For robust path management

# The command below opens a connection to the database.
#If the database does not yet exist, one is created in the working directory of R.
db <- dbConnect(SQLite(), dbname='Test.sqlite')

# Drop existing tables if they exist to avoid duplication
# This allows the script to run multiple times without errors
if (dbExistsTable(db, "Consumer")) {
  dbRemoveTable(db, "Consumer")
  cat("Existing 'Consumer' table removed.\n")
}

if (dbExistsTable(db, "Resource")) {
  dbRemoveTable(db, "Resource")
  cat("Existing 'Resource' table removed.\n")
}

# Now let's enter some data to the table
# Using the db connection to our database, the data are entered using SQL queries
# The next command just create the table
dbExecute(conn = db,
          "CREATE TABLE Consumer
       (OriginalID TEXT,
        ConKingdom TEXT,
        ConPhylum TEXT,
        ConSpecies TEXT)")

# Once the table is created, we can enter the data.
#INSERT specifies where the data is entered (here the School table).
#VALUES contains the data

dbExecute(conn = db,
          "INSERT INTO Consumer
         VALUES (1, 'Animalia', 'Arthropoda', 'Chaoborus trivittatus')")
dbExecute(conn = db,
          "INSERT INTO Consumer
         VALUES (2, 'Animalia', 'Arthropoda', 'Chaoborus americanus')")
dbExecute(conn = db,
          "INSERT INTO Consumer
         VALUES (3, 'Animalia', 'Chordata', 'Stizostedion vitreum')")


# Once we have our table, we can query the results using:

dbGetQuery(db, "SELECT * FROM Consumer")
dbGetQuery(db, "SELECT * FROM Consumer WHERE ConPhylum='Chordata'")


# Tables can be also imported from csv files.
# As example, let's use the Biotraits dataset.
# The easiest way is to read the csv files into R as data frames.
# Then the data frames are imported into the database.

Resource <- read.csv(here("week4", "data", "Resource.csv"))  # Read csv files into R

# Import data frames into database
 dbWriteTable(conn = db, name = "Resource", value = Resource, row.names = FALSE)

# Check that the data have been correctly imported into the School table.
 dbListTables(db)                 # The tables in the database
 dbListFields(db,"Resource")       # The columns in a table
 dbReadTable(db, "Resource")    # The data in a table

# Before leaving RSQLite, there is a bit of tidying-up to do.
# The connection to the database is closed, and as precaution
# the three data frames are removed from R’s environment.
 dbDisconnect(db)            # Close connection
 rm(list = c("Resource"))   # Remove data frames


