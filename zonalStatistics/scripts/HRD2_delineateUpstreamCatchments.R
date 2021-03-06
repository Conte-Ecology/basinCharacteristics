# This script delineates the upstream catchments of the arcHydro output shapefile.

rm(list=ls())

# Load libraries
library(tcltk)
library(foreign)

# ======================
# Specify base directory
# ======================
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'

# Read user-defined inputs
source( file.path(baseDirectory, "scripts", "HRDV2_INPUTS.txt") )

# ============
# Read in data
# ============

# Define the output file
outputFilePath <- file.path(baseDirectory, 'versions', outputName, paste0(outputName, '_delineatedCatchments.RData') )

#Check the existence of the delineated catchments file, stopping the script if it exists.
if( !file.exists( outputFilePath ) ){
  
  # Read the catchment attributes
  catchmentData <- read.dbf(file.path(baseDirectory, 'gisFiles/vectors', paste0(catchmentsFileName, '.dbf')) )
  
  # ====================
  # Delineate catchments
  # ====================
  
  # Pull the catchment IDs ("HydroID")
  features <- unique(catchmentData[,c(zoneField)])
  
  # Empty list for saving
  delineatedCatchments <- list()
  
  # Set progress bar
  progressBar <- tkProgressBar(title = "progress bar", min = 0, max = length(features), width = 300)
  
  # Loop through all catchments
  for ( i in 1:length(features)){
  
    segments<-c() #list of flowline segments to save
    queue<-c(features[i]) #queue of flowline segments that need to be traced upstream
    
    while (length(queue)>0) {
      
      # Save all of the segments
      segments<-c(segments,queue)
     
      # Which catchments flow into the ones in the current queue
      queue<-c(catchmentData[catchmentData$NextDownID %in% queue, zoneField])
      
      # Eliminate duplicates
      queue<-unique(queue)
      
      # Eliminates queuing flowlines that have already been added to segments
      queue<-queue[!(queue %in% segments)]
    }# end while loop
    
    # Double check duplicates
    delineatedCatchments[[i]] <-unique(segments)
    names(delineatedCatchments)[i] <- features[i]
    
    setTkProgressBar(progressBar, i, label=paste( round(i/length(features)*100, 2), "% done"))
    
  }# end for loop
  
  close(progressBar)
  
  # Save catchments
  save(delineatedCatchments, file = outputFilePath )

}else("Delineated Catchments file already exists. If this is the desired file there is no need to run this script.")