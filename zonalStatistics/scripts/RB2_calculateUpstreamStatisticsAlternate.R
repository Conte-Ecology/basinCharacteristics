rm(list=ls())

# ===========
# Description
# ===========
# This script reads the output from the ArcPy zonal statistics script. It uses the table with polygon areas to calculate the upstream average of the variable.
# The averaging does not account for the overlapping areas between the polygons. This is an accepted error.


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

# Set the Base Directory
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'


# ==========
# Load files
# ==========

# User inputs
source( file.path(baseDirectory, "scripts", "RB_INPUTS.txt") )

# Delineated catchments
load(file.path(baseDirectory, "versions/NortheastHRD/NortheastHRD_delineatedCatchments.RData"))

# Catchment Areas
vectorArea <- read.dbf(file.path(baseDirectory, 'versions', outputName,'gisTables',  paste0('AreaSqKM_', bufferID,'.dbf')))

# ==========
# Spatial averageing of zonal statistics
# ==========


# ========================
# Process local statistics
# ========================

# Save local area as CSV
areaFileLocal <- file.path(baseDirectory, 'versions', outputName,'rTables',  paste0('local_AreaSqKM_', bufferID,'.csv'))

if(!file.exists(areaFileLocal)){
  write.csv(vectorArea, areaFileLocal, row.names = F)
}

zonalData <- NULL
zonalAreas <- NULL

setwd(file.path(baseDirectory,"versions", outputName, "gisTables"))

for (raster in rasterList){

  tiles <- list.files(".", pattern = paste0("^",raster, bufferID, ".*", ".dbf$"))  

  allValues <- NULL

  for (t in seq_along(tiles)){
    
    curTile <- read.dbf(tiles[t])
    
    # Weighted average by area
    curValues <- data.frame(arrange_(curTile, .dots = zoneField) %>%
                              mutate(AreaSqKM = AreaSqM/1000000)%>%
                              select(-AreaSqM) %>%
                              group_by_(.dots = zoneField) %>%
                              mutate(totalArea = sum(AreaSqKM))%>%
                              mutate(weightedValue = AreaSqKM/totalArea*Value)%>%
                              select(-c(Value, totalArea))%>%
                              summarise_each(funs(sum))
                                )
    
    #curValues <- as.data.frame(curValues)

    # Join HUC tiles
    if (is.null(allValues)) {
      allValues <- curValues
    } else{
      
      toJoin <- curValues[!curValues[,zoneField] %in% allValues[,zoneField],]
       
      allValues <- rbind(allValues, toJoin)
    }
    
  }#End tile loop
  
  names(allValues)[3] <- statType
  
  # Missing Zones
  # -------------
  # Account for zones missing completely from output
  missingZones <- vectorArea[!(vectorArea[,zoneField] %in% allValues[,zoneField]),zoneField]
  
  missingData <- as.data.frame(matrix(nrow = length(missingZones), ncol = 3))
  missingData[,1] <- missingZones
  missingData[,2] <- 0
  missingData[,3] <- NA
  
  names(missingData) <- c(zoneField, "AreaSqKM", statType)
  
  allValues <- rbind(allValues, missingData)
  
  # Prep dataframes for upstream averaging
  # --------------------------------------
  # Zonal data
  dat <- allValues[,c(zoneField, statType)]
  names(dat)[2] <- raster
  if ( is.null(zonalData) ) { 
    zonalData <- dat 
  } else{ zonalData <- left_join(zonalData, dat, by = zoneField)}
  
  # Zone areas
  wt <- allValues[,c(zoneField, "AreaSqKM")]
  names(wt)[2] <- raster
  if ( is.null(zonalAreas) ) { 
    zonalAreas <- wt 
  } else{ zonalAreas <- left_join(zonalAreas, wt, by = zoneField)}

  # Calculate the percent area with data
  localOutput <- left_join(allValues, vectorArea, by = zoneField) %>%
                              mutate(percentAreaWithData = round(AreaSqKM.x/AreaSqKM.y*100, digits = 3))%>%
                              select(-c(AreaSqKM.x, AreaSqKM.y))
  
  # Save as CSV
  write.csv(localOutput, 
          file = file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_", raster, "_", bufferID, ".csv")),
          row.names = F)
 
}#End raster loop    
    



# ===========================
# Process upstream statistics
# ===========================

# Define features to compute
featureList <- zonalData[,zoneField]

# Define storage dataframes
# -------------------------
# Upstream area (from vector)
areaFileUpstream <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_AreaSqKM_", bufferID, ".csv"))

# If Upstream area file doesn't exist, calculate it based on the vectors
if ( !file.exists(areaFileUpstream) ){
  upstreamArea <- data.frame(matrix(NA, nrow = length(featureList), ncol = 2))
  names(upstreamArea) <- c(zoneField, "AreaSqKM")
}

# Upstream stats
upstreamStats <- data.frame(matrix(NA, nrow = length(featureList), ncol = length(rasterList) + 1))
names(upstreamStats) <- c(zoneField, rasterList)

# Catchments loop
# ---------------
progressBar <- tkProgressBar(title = "progress bar", min = 0, max = length(featureList), width = 300)
for ( m in seq_along(featureList)){  

  # Get features in current basin
  features <- delineatedCatchments[[which(names(delineatedCatchments) == featureList[m])]]
  
  # Get individual catchment stats for current basin
  catchStats <- filter_(zonalData, interp(~col %in% features, col = as.name(zoneField)))#%>%
  
  # Get individual catchment areas with data for current basin
  catchAreas <- filter_(zonalAreas, interp(~col %in% features, col = as.name(zoneField)))#%>%

  # Calculate the weights of each element in the dataframe (creates a matching dataframe)
  weights <- sweep(catchAreas, 2, colSums(catchAreas), `/`)
  
  # Weight the zonal data by area
  weightedStats <- catchStats*weights
  
  # Sum the weighted stats to get final values. (Account for the case where all values are NA, preventing it from returning a 0)
  outStats <- colSums(weightedStats, na.rm=TRUE) + ifelse(colSums(is.na(weightedStats)) == nrow(weightedStats), NA, 0)
   
  # Save to output dataframe
  upstreamStats[m,1]                     <- featureList[m]
  upstreamStats[m,2:ncol(upstreamStats)] <- outStats[-1]
  
  # Calculate the upstream area based on the buffer polygon file
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
# Loop through variables writing tables with upstream data
for (n in 2:(ncol(upstreamStats))){
  
  # Name
  colName <- names(upstreamStats)[n]
  
  # Output dataframe
  upStat <- upstreamStats[,c(zoneField, colName)]
  names(upStat)[2] <- statType

  # Save output
  outputUpstream  <- file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_", colName, "_", bufferID, ".csv"))
  write.csv(upStat, file = outputUpstream,  row.names = F)
  
}

# Save area file
if ( !file.exists(areaFileUpstream) ){
  write.csv(upstreamArea, file = areaFileUpstream, row.names = F)
}