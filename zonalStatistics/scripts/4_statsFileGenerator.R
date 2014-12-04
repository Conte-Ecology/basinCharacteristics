# Catchment Stats Generator

library(dplyr)

# ======
# Inputs 
# ======
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'

# Specify variables to output. "ALL" will include all of the variables prsent in the folder.
outputVariables <- c('ALL')

# ========================
# Read user-defined inputs
# ========================
source( file.path(baseDirectory, "scripts", "INPUTS.txt") )

rTablesDirectory <- file.path(baseDirectory, "versions", outputName, "rTables")                            

# Local
# -----

if ( all(outputVariables %in% "ALL" == TRUE) ){
  localStatFiles <- list.files(path = rTablesDirectory, pattern = "local_")  
  
}else{
  localStatFiles <- c()
  
  for( LF in seq_along(outputVariables) ){
    localStatFiles <- c(localStatFiles, list.files(path = rTablesDirectory, pattern = paste0("local_",outputVariables[LF] ) ) )
  }
}


for ( L in 1:length(localStatFiles) ){
  
  localTemp <- read.csv(file.path(rTablesDirectory, localStatFiles[L]) )
  
  # Get file name
  A <- gsub("*local_", "", localStatFiles[L])
  variableName <- gsub(paste0("*_", statType,".csv"), "", A)
  variableName <- gsub(paste0("*.csv"), "", variableName)
  
  names(localTemp) <- c(zoneField, variableName)
  
  if( L == 1) {LocalStats <- localTemp} else(LocalStats <- left_join(LocalStats, localTemp, by = zoneField) )
}

# Upstream
# --------

if ( all(outputVariables %in% "ALL" == TRUE) ){
  upstreamStatFiles <- list.files(path = rTablesDirectory, pattern = "upstream_")
}else{
  upstreamStatFiles <- c()
  
  for( UF in seq_along(outputVariables) ){
    upstreamStatFiles <- c(upstreamStatFiles, list.files(path = rTablesDirectory, pattern = paste0("upstream_",outputVariables[UF] ) ) )
  }
}


for ( U in 1:length(upstreamStatFiles) ){
  
  upstreamTemp <- read.csv(file.path(rTablesDirectory, upstreamStatFiles[U]) )
  
  # Get file name
  A <- gsub("*upstream_", "", upstreamStatFiles[U])
  variableName <- gsub(paste0("*_", statType,".csv"), "", A)
  variableName <- gsub(paste0("*.csv"), "", variableName)
  
  names(upstreamTemp) <- c(zoneField, variableName)
  
  if( U == 1) {UpstreamStats <- upstreamTemp} else(UpstreamStats <- left_join(UpstreamStats, upstreamTemp, by = zoneField) )
}

# Save output
save(LocalStats, UpstreamStats, file = file.path(baseDirectory, "versions", outputName, "completedStats", "zonalStats.RData") )
