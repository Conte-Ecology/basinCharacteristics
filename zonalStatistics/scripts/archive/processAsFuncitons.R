# This script delineates the upstream catchments of the arcHydro output shapefile.

rm(list=ls())

# Load libraries
library(foreign)

# ======================
# Specify base directory
# ======================
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'

# ============
# Read in data
# ============

# Read user-defined inputs
source( file.path(baseDirectory, "scripts", "INPUTS.txt") )

# Read the catchment attributes
catchmentData <- read.dbf(file.path(baseDirectory, 'gisFiles/vectors', paste0(catchmentsFileName, '.dbf')) )

# ====================
# Delineate catchments
# ====================
#Check the existence of the delineated catchments file, stopping the script if it exists.

delineationFilePath <- file.path(baseDirectory, 'versions', outputName, paste0(outputName, '_delineatedCatchments2.RData') )

# If the delineation file exists, load it and proceed. If it doesn't exist, create it.
if( file.exists( delineationFilePath ) ){
  
  print("Delineated Catchments file already exists. Loading file...")
  
  load( delineationFilePath )
}else{
  delineatedCatchments <- delineateUpstreamCatchments(catchmentsDataTable = catchmentData)
  
  save(delineatedCatchments, file = delineationFilePath ) 
}
