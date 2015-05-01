rm(list=ls())

# Catchment Stats Generator
library(dplyr)
library(reshape2)

# ======
# Inputs 
# ======
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'

# There are 3 options for specifying the variables to output:
#   1) "ALL" will include all of the variables present in the folder
#   2) NULL will include the variables from the "rasterList" object in the "RB_INPUTS.txt" file
#   3) Manually list the variables to output (do not include the buffer specification)
outputVariables <- c("ALL")

# ========================
# Read user-defined inputs
# ========================
source( file.path(baseDirectory, "scripts", "RB_INPUTS.txt") )

# ==================
# Conversion Factors
# ==================
# Read the conversion factors file
setwd(baseDirectory); setwd('..')
conversionFactors <- read.csv("Covariate Data Status - High Res Delineation.csv")[,c("Name", "Conversion.Factor")]

# Rename columns
names(conversionFactors) <- c("variable", "factor")

# Include the bufferID
conversionFactors$variable <- paste0(conversionFactors$variable , "_", bufferID)

# ======================
# Group stats for output
# ======================

# Set the directory where the tables are located
rTablesDirectory <- file.path(baseDirectory, "versions", outputName, "rTables")                            

if(is.null(outputVariables)){outputVariables <- rasterList}

# Local
# -----

# Create list of variables to compile
if ( all(outputVariables %in% "ALL" == TRUE) ){
  localStatFiles <- list.files(path = rTablesDirectory, pattern = paste0("^local_.*_", bufferID,".csv$"))  
  
}else{
  localStatFiles <- c()
  
  outputVariables <- paste0(outputVariables, "_", bufferID)
  
  for( LF in seq_along(outputVariables) ){
    localStatFiles <- c(localStatFiles, list.files(path = rTablesDirectory, pattern = paste0("local_",outputVariables[LF] ) ) )
  }
}

# Loop through files. Pull data and join together for output.
for ( L in seq_along(localStatFiles) ){
  
  # Print status
  print(L)
  
  # Read the CSV
  localTemp <- read.csv(file.path(rTablesDirectory, localStatFiles[L]) )
  
  # Get file name
  A <- gsub("*local_", "", localStatFiles[L])
  variableName <- gsub(paste0("*.csv"), "", A)

  # Rename the columns
  names(localTemp) <- c(zoneField, variableName)
  
  # Pull the variable specifc factor
  factor <- filter(conversionFactors, variable == variableName)%>%
              select(factor)
  
  # Account for missing factors  
  if(is.na(as.numeric(factor))) {
    print(paste0("Factor missing for '", variableName, "'. Assigning a default factor of 1."))
    factor <- 1
  }
  
  # Multiply the raw variable value by the conversion factor
  localTemp[,names(localTemp) == variableName] <- localTemp[,names(localTemp) == variableName]*as.numeric(factor)
  
  # Join to main dataframe
  if( L == 1) {LocalStats <- localTemp} else(LocalStats <- left_join(LocalStats, localTemp, by = zoneField) )
}

# Upstream
# --------

# Create list of variables to compile
if ( all(outputVariables %in% "ALL" == TRUE) ){
  upstreamStatFiles <- list.files(path = rTablesDirectory, pattern = paste0("^upstream_.*_", bufferID,".csv$"))
}else{
  upstreamStatFiles <- c()
  
  for( UF in seq_along(outputVariables) ){
    upstreamStatFiles <- c(upstreamStatFiles, list.files(path = rTablesDirectory, pattern = paste0("upstream_",outputVariables[UF] ) ) )
  }
}


# Loop through files. Pull data and join together for output.
for ( U in 1:length(upstreamStatFiles) ){
  
  # Print status
  print(U)
  
  # Read the CSV  
  upstreamTemp <- read.csv(file.path(rTablesDirectory, upstreamStatFiles[U]) )
  
  # Get file name
  A <- gsub("*upstream_", "", upstreamStatFiles[U])
  variableName <- gsub(paste0("*.csv"), "", A)
  
  # Rename the columns. 
  names(upstreamTemp) <- c(zoneField, variableName)
  
  # Pull the variable specific factor
  factor <- filter(conversionFactors, variable == variableName)%>%
    select(factor)
  
  # Account for missing factors
  if(is.na(as.numeric(factor))) {
    print(paste0("Factor missing for '", variableName, "'. Assigning a default factor of 1."))
    factor <- 1
  }
  
  # Multiply the raw variable value by the conversion factor
  upstreamTemp[,names(upstreamTemp) == variableName] <- upstreamTemp[,names(upstreamTemp) == variableName]*as.numeric(factor)
  
  # Join to main dataframe
  if( U == 1) {UpstreamStats <- upstreamTemp} else(UpstreamStats <- left_join(UpstreamStats, upstreamTemp, by = zoneField) )
}

# ===================
# Format for Database
# ===================

locLong <- melt(LocalStats,'FEATUREID')
locLong$zone <- "local"

upLong <- melt(UpstreamStats,'FEATUREID')
upLong$zone <- "upstream"

dbStats <- rbind(locLong, upLong)

# Names need to be all lower-case
names(dbStats) <- tolower(names(dbStats))

# make sure columns are correctly named and ordered
stopifnot(all(names(dbStats) == c('featureid', 'variable', 'value', 'zone')))

# Save the output as CSV
write.csv(dbStats, 
            file = file.path(baseDirectory, "versions", outputName, "completedStats", paste0("zonalStatsForDB_", outputName, bufferID, "_", Sys.Date(), ".csv")),
            row.names = FALSE)






