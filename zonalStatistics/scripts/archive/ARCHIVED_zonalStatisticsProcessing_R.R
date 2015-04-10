# Clear workspace
rm(list=ls())

# ==============
# Load libraries
# ==============
library(rgdal)
library(reshape2)
library(raster)
library(foreign)


#=======================
# Set the Base Directory
#=======================
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'


# ========================
# Read user-defined inputs
# ========================
source( file.path(baseDirectory, "scripts", "inputFiles", "inputs_NENY_HRD.txt") )


# =================
# Load spatial data
# =================
# Load catchments
catchments <- readOGR(dsn = paste0(baseDirectory, '/gisFiles/vectors'), layer = catchmentsFileName)

# Get the projection to read the rasters
projection <- proj4string(catchments)

if ( all(rasterList %in% "ALL" == TRUE) ){
  
  # List raster files by looking at output folder
  rasterFiles <- list.files(path=paste0(baseDirectory, '/versions/', outputName, '/gisTables'), pattern = "\\.dbf$")    #promt user for dir containing raster files
  
  # List raster names
  rasterList <- c(colsplit(rasterFiles, paste0("_", statType), names = c('raster', 'ext'))$raster)
}


# ====================
# Retrieve zonal stats
# ====================
# Any missing catchment uses the "extract" function which returns the value of the raster at the centroid of the polygon.

#Loop through all of the rasters
for (j in 1:length(rasterList)){
  
  # File path to raster
  rasterFilePath <- file.path(baseDirectory, 'gisFiles/versions', outputName, rasterList[j])
  
  # Read raster
  currentRaster <- raster(rasterFilePath ,proj4string=CRS(projection))
  
  # File path to table
  tableFilePath <- file.path(baseDirectory,"versions", outputName, "gisTables", paste0(rasterList[j], "_", statType, ".dbf"))
  
  # Open table
	gisStat <-read.dbf(tableFilePath)[,c(zoneField, statType)]
	
	#Find the FEATUREIDs that Zonal Stats missed in Arc:
	missingCatchments <- catchments[!catchments@data[,zoneField] %in% gisStat[,zoneField],]
	
	#Get the polygon centroids
	centroids <- coordinates(missingCatchments)	
  
  # Calculate the specified statistic at the centroids
  centValue <- extract (currentRaster[[j]], centroids, method = 'simple', fun=statType)

  # Match formatting
	rStat <- data.frame (missingCatchments@data[,zoneField], centValue)
	names(rStat) <- c(zoneField, statType)
	
  # Full list of stats
	zonalStatistics <- rbind(gisStat, rStat)
  
  # Output filepath
  outputTable <- file.path(baseDirectory,"versions", outputName, "rTables", paste0(rasterList[j], "_", statType, ".csv"))
  
  # save this as a file
  write.csv(zonalStatistics, file = outputTable, row.names = F)
}