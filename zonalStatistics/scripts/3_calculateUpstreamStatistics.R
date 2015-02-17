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


# ==========
# Load files
# ==========

# User inputs
# -----------
source( file.path(baseDirectory, "scripts", "INPUTS.txt") )

rasterList <- c(discreteRasters, continuousRasters)


# Delineated catchments
# ---------------------
load(file.path(baseDirectory, "versions", outputName, paste0(outputName, "_delineatedCatchments.RData")))

# ========================
# Process local statistics
# ========================

# Loop through layers, reading files.
for (j in 1:length(rasterList)){

  # Output filepath
  outputTable <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_", rasterList[j], "_", statType, ".csv"))
  
  if ( !file.exists(outputTable) ){
  
    # File path to table
    tableFilePath <- file.path(baseDirectory,"versions", outputName, "gisTables", paste0(rasterList[j], "_", statType, ".dbf"))
    
    # Open table
    gisStat <-read.dbf(tableFilePath)[,c(zoneField, statType, "AREA")]
    gisStat$AREA <- gisStat$AREA*0.000001 # convert to square kilometers
    names(gisStat)[3] <- "dataAreaSqKM"
    
    # Replace all "-9999" values with "NA"
    gisStat[which(gisStat[,statType] == -9999), statType] <- NA
 
    # save this as a file
    write.csv(gisStat, file = outputTable, row.names = F)
  } else { gisStat <- read.csv(outputTable) }
  
  # Prep dataframes for upstream averaging
  # --------------------------------------
  # Data
  dat <- gisStat[,c(zoneField, statType)]
  names(dat)[2] <- rasterList[j]
  if ( j == 1 ) { zonalData <- dat } else( zonalData <- left_join(zonalData, dat, by = zoneField))

  # Areas
  wt <- gisStat[,c(zoneField, "dataAreaSqKM")]
  names(wt)[2] <- rasterList[j]
  if ( j == 1 ) { zonalAreas <- wt } else( zonalAreas <- left_join(zonalAreas, wt, by = zoneField))
}


# =============
# Drainage Area
# =============
# The areas based on the vectors are saved as the areas, though the raster areas are used to define the percentage of area with data. 
#   These areas match up with the data layers which

# Vector
# ------
# Input file
vectorFile <- file.path(baseDirectory, 'gisFiles/vectors', paste0(catchmentsFileName, '.dbf'))

# Output filepath (local)
areaFileLocal <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_AreaSqKM.csv"))

# If the area file doesn't exist, write it. Else load it.
if ( !file.exists(areaFileLocal) ){

  # Read the catchment attributes
  vectorArea <- read.dbf(vectorFile)[,c(zoneField, "AreaSqKM")]
  
  # Save file
  write.csv(vectorArea, file = areaFileLocal, row.names = F)
} else {vectorArea <- read.csv(areaFileLocal)}


# Raster
# ------
localArea <- read.dbf(file.path(baseDirectory,"versions", outputName, "gisTables/catRasterAreas.dbf"))[,c(zoneField, "AREASQKM")]
names(localArea)[2] <- "AreaSqKM"



# ===========================
# Process upstream statistics
# ===========================

# Define features to compute
featureList <- zonalData[,zoneField]

# Define storage dataframes
# -------------------------

# Upstream stats
upstreamStats <- data.frame(matrix(NA, nrow = length(featureList), ncol = length(rasterList) + 1))
names(upstreamStats) <- c(zoneField, rasterList)

# Areas with data
pcntUpstreamWithData <- data.frame(matrix(NA, nrow = length(featureList), ncol = length(rasterList) + 1))
names(pcntUpstreamWithData) <- c(zoneField, rasterList)

# Upstream area (from vector)
areaFileUpstream <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_AreaSqKM.csv"))

# If Upstream area file doesn't exist, calculate it based on the vectors
if ( !file.exists(areaFileUpstream) ){
  upstreamArea <- data.frame(matrix(NA, nrow = length(featureList), ncol = 2))
  names(upstreamArea) <- c(zoneField, "AreaSqKM")
}


# Catchments loop
# ---------------
progressBar <- tkProgressBar(title = "progress bar", min = 0, max = length(featureList), width = 300)
for ( m in seq_along(featureList)){  

  # Get features in current basin
  features <- delineatedCatchments[[which(names(delineatedCatchments) == featureList[m])]]
  
  # Sum the areas of the individual catchments in the basin (raster version)
  TotDASqKM <- sum(filter_(localArea, interp(~col %in% features, col = as.name(zoneField)))$AreaSqKM)
  
  # Get individual catchment stats for current basin
  catchStats <- filter_(zonalData, interp(~col %in% features, col = as.name(zoneField)))#%>%
  
  # Get individual catchment areas with data for current basin
  catchAreas <- filter_(zonalAreas, interp(~col %in% features, col = as.name(zoneField)))#%>%

  # Calculate the weights of each element in the dataframe (creates a matching dataframe)
  weights <- sweep(catchAreas, 2, colSums(catchAreas), `/`)
   
  # Sum the weighted stats to get final values
  outStats <- colSums(catchStats*weights, na.rm = T)
  
  # Get the percentage of catchment area with data
  outAreas <- colSums(catchAreas)/TotDASqKM
  
  # Account for the rare case of catchments area = 0 (product of rasterizing catchments polygons)
  if (TotDASqKM == 0) {
    outStats[2:length(outStats)] <- NA
    outAreas[2:length(outAreas)] <- 0
  }
  
  # Upstream stats
  upstreamStats[m,1]                     <- featureList[m]
  upstreamStats[m,2:ncol(upstreamStats)] <- outStats[-1]
  
  # Area with data
  pcntUpstreamWithData[m,1]                     <- featureList[m]
  pcntUpstreamWithData[m,2:ncol(upstreamStats)] <- outAreas[-1]
  
  
  # Total drainage area
  # -------------------
  # This is calculated based on the vector file
  if ( !file.exists(areaFileUpstream) ){
    upstreamArea[m,1] <- featureList[m]
    upstreamArea[m,2] <- sum(filter_(vectorArea, interp(~col %in% features, col = as.name(zoneField)))$AreaSqKM, na.rm = T)
  }
  
  # Progress bar update
  setTkProgressBar(progressBar, m, label=paste( round(m/length(featureList)*100, 2), "% done"))
}
close(progressBar)

# Output upstream statistics tables
# ---------------------------------

# Loop through variables writing tables with upstream data and the percent of the area with data
for ( n in 2:(ncol(upstreamStats))){
  
  # Name
  colName <- names(upstreamStats)[n]
  
  # Output dataframe
  upStat <- upstreamStats[,c(zoneField, colName)]
  names(upStat)[2] <- statType
  
  upPcnt <- pcntUpstreamWithData[,c(zoneField, colName)]
  upPcnt <- upPcnt[2]*100
  names(upPcnt)[2] <- "percentUpstreamWithData"
  
  #
  ##
  ###
  test <- left_join(upStat, upPcnt, by = zoneField)
  ###
  ##
  #
  
  # Output filepath
  outputUpstream  <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_", colName, "_", statType, ".csv"))
  percentUpstream <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("pcntData_", colName, "_", statType, ".csv"))
  
  # Store outputs as CSVs
  write.csv(upStat, file = outputUpstream,  row.names = F)
  write.csv(upPcnt, file = percentUpstream, row.names = F)
}




# Save area file
if ( !file.exists(areaFileUpstream) ){
  write.csv(upstreamArea, file = areaFileUpstream, row.names = F)
}






