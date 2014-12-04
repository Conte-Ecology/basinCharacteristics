rm(list=ls())

# ==============
# Load libraries
# ==============
library(reshape2)
library(foreign)
library(tcltk)
library(dplyr)
library(lazyeval)

#=======================
# Set the Base Directory
#=======================
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'


# ========================
# Read user-defined inputs
# ========================
source( file.path(baseDirectory, "scripts", "INPUTS.txt") )

# ===========
# Load data
# ===========

# Tables
# ------
if ( all(rasterList %in% "ALL" == TRUE) ){
  
  # List raster files by looking at output folder
  rasterFiles <- list.files(path=paste0(baseDirectory, '/versions/', outputName, '/gisTables'), pattern = paste0("\\", statType, ".dbf$"))    #promt user for dir containing raster files
  
  # List raster names
  rasterList <- c(colsplit(rasterFiles, paste0("_", statType), names = c('raster', 'ext'))$raster)
}

# Delineated catchments
# ---------------------
load(file.path(baseDirectory, "versions", outputName, paste0(outputName, "_delineatedCatchments.RData")))


# ========================
# Process local statistics
# ========================

# Loop through rasters, grabbing files.
for (j in 1:length(rasterList)){

  # File path to table
  tableFilePath <- file.path(baseDirectory,"versions", outputName, "gisTables", paste0(rasterList[j], "_", statType, ".dbf"))
  
  # Open table
  gisStat <-read.dbf(tableFilePath)[,c(zoneField, statType)]
  
  # Replace "-9999"s with "NA"
  gisStat[which(gisStat[,statType] == -9999), statType] <- NA

  # Output filepath
  outputTable <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_", rasterList[j], "_", statType, ".csv"))
  
  # save this as a file
  write.csv(gisStat, file = outputTable, row.names = F)
  
  # Storing output
  # --------------
  # Rename
  names(gisStat) <- c(zoneField, rasterList[j])
  
  # Store for upstream averaging
  if ( j == 1 ) { zonalData <- gisStat } else( zonalData <- left_join(zonalData, gisStat, by = zoneField))
}


# =============
# Drainage Area
# =============

# Local
# -----
# Output filepath
areaFileLocal <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_AreaSqKM.csv"))

# If the area file doesn't exist, write it
if ( !file.exists(areaFileLocal) ){

  # Read the catchment attributes
  localArea <- read.dbf(file.path(baseDirectory, 'gisFiles/vectors', paste0(catchmentsFileName, '.dbf')) )[,c(zoneField, "AreaSqKM")]
  
  # Save file
  write.csv(localArea, file = areaFileLocal, row.names = F)
}

# Upstream
# --------
# Output filepath
areaFileUpstream <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_AreaSqKM.csv"))

if ( !file.exists(areaFileUpstream) ){
  
  # Read local catchment area file
  area <- read.csv(areaFileLocal)
  
  # List the features to loop through
  featureList <- area[,zoneField]
  
  # Create the output dataframe
  upstreamArea <- data.frame(matrix(nrow = length(featureList), ncol = 2))
  names(upstreamArea) <- c(zoneField, "AreaSqKM")
  
  
  # Loop through all features calculating upstream area
  for ( k in seq_along(featureList) ){
  
    # Get the upstream features
    features <- delineatedCatchments[[which(names(delineatedCatchments) == featureList[k])]]
    
    # Calculate area
    DA <- sum(filter(area, FEATUREID %in% features)$AreaSqKM, na.rm = T) 
    
    # Store result
    upstreamArea[k,] <- c(featureList[k], DA)
    
    print(k)
  }
  
  # Save file
  write.csv(upstreamArea, file = areaFileUpstream, row.names = F)
} else(print("Local area file does not exist. Please create this file before running this section."))




# ===========================
# Process upstream statistics
# ===========================


# If areas weren't calculated in this run then load them
if( !exists("localArea") )   {localArea    <- read.csv(areaFileLocal)}
if( !exists("upstreamArea") ){upstreamArea <- read.csv(areaFileUpstream)}

# Join area to dataframe
zonalData <- left_join(zonalData, localArea, by = zoneField)

# Define features to compute
featureList <- zonalData[,zoneField]


# Define storage dataframe
UpstreamStats <- data.frame(matrix(NA, nrow = length(featureList), ncol = length(rasterList) + 1))
names(UpstreamStats) <- c(zoneField, rasterList)

# Progress bar
progressBar <- tkProgressBar(title = "progress bar", min = 0, max = length(featureList), width = 300)

# Loop through all catchments
for ( m in seq_along(featureList)){  

  # Get features in current basin
  features <- delineatedCatchments[[which(names(delineatedCatchments) == featureList[m])]]
  
  #Pull DA from table:
  TotDASqKM <- filter_(upstreamArea, interp(~col == featureList[m], col = as.name(zoneField)))$AreaSqKM
  
  # Get current catchment stats
  catchStats <- filter_(zonalData, interp(~col %in% features, col = as.name(zoneField)))%>%
                  mutate(Weight = AreaSqKM/TotDASqKM)

  # Catchment ID
  UpstreamStats[m,1] <- featureList[m]
  
  # Area-weighted averages
  UpstreamStats[m,2:ncol(UpstreamStats)] <- sapply(rasterList,function(x){weighted.mean(catchStats[,x], catchStats$Weight, na.rm = TRUE)})
  
  # Progress bar update
  setTkProgressBar(progressBar, m, label=paste( round(m/length(featureList)*100, 2), "% done"))
} 


# Output upstream statistics tables
# ---------------------------------

# Loop through variables
for ( n in 2:(ncol(UpstreamStats))){
  
  # Name
  colName <- names(UpstreamStats)[n]
  
  # Output dataframe
  upStat <- UpstreamStats[,c(zoneField, colName)]
  
  # Output filepath
  outputTable <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_", colName, "_", statType, ".csv"))
  
  # save this as a file
  write.csv(upStat, file = outputTable, row.names = F)
}



