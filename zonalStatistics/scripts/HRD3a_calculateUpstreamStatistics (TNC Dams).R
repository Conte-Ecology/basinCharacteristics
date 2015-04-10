rm(list=ls())

# ==============
# Load libraries
# ==============
library(reshape2)
library(foreign)
library(tcltk)
library(dplyr)
library(lazyeval)

#========================================================
# Set the Base Directory & file path to TNC barrier stats
#========================================================
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'

barrierStatsFilePath <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/tncDams/outputTables/barrierStats_NortheastHRD.dbf'


# ==========
# Load files
# ==========

# User inputs
# -----------
source( file.path(baseDirectory, "scripts", "HRD_INPUTS.txt") )

# Delineated catchments
# ---------------------
load(file.path(baseDirectory, "versions", outputName, paste0(outputName, "_delineatedCatchments.RData")))

# Barrier statistics
# ------------------
barrierStats <- read.dbf(barrierStatsFilePath)

# Catchment Areas
# ---------------
# Local
vectorArea   <- read.csv(file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_AreaSqKM.csv")))


# ==================
# Edit Barrier Stats
# ==================

# Remove extra column
barrierStats <- barrierStats[,-2]

# Summ all barrier types
barrierStats$deg_barr_all <- rowSums (barrierStats[,-1], na.rm = TRUE, dims = 1)

# Barrier type count
numBarriers <- ncol(barrierStats) - 1


# ========================
# Process local statistics
# ========================

# Loop through layers, reading files.
for (b in 1:numBarriers){

  # Separate individual barrier types
  gisStat <- barrierStats[,c(1, b + 1)]
  
  # Specify the output
  outputTable <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_", names(gisStat)[2], ".csv"))
  
  # Save the local stat file
  write.csv(gisStat, file = outputTable, row.names = F)
  
}


# ===========================
# Process upstream statistics
# ===========================

# Define features to compute
featureList <- barrierStats[,zoneField]

# Define storage dataframe
upstreamStats <- data.frame(matrix(NA, nrow = length(featureList), ncol = numBarriers + 1))
names(upstreamStats) <- names(barrierStats)


# Catchments loop
# ---------------
progressBar <- tkProgressBar(title = "progress bar", min = 0, max = length(featureList), width = 300)
for ( m in seq_along(featureList)){  

  # Get features in current basin
  features <- delineatedCatchments[[which(names(delineatedCatchments) == featureList[m])]]
  
  # Get individual catchment stats for current basin
  catchStats <- filter_(barrierStats, interp(~col %in% features, col = as.name(zoneField)))
   
  # Sum the weighted stats to get final values
  outStats <- colSums(catchStats, na.rm = T)
 
  # Upstream stats
  upstreamStats[m,1]                     <- featureList[m]
  upstreamStats[m,2:ncol(upstreamStats)] <- outStats[-1]
  
  # Progress bar update
  setTkProgressBar(progressBar, m, label=paste( round(m/length(featureList)*100, 2), "% done"))
}
close(progressBar)


# Output upstream statistics tables
# ---------------------------------

# Loop through variables writing tables with total number of dams upstream 
for ( n in 2:(ncol(upstreamStats))){
  
  # Name
  colName <- names(upstreamStats)[n]
  
  # Output dataframe
  upStat <- upstreamStats[,c(zoneField, colName)]

  # Write out file
  write.csv(upStat, 
            file = file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_", colName, ".csv")),
            row.names = F)
}