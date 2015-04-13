rm(list=ls())

# ==============
# Load libraries
# ==============
library(dplyr)
library(foreign)


# ======================
# Set the Base Directory
# ======================
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'

# ==============
# Specify Inputs
# ==============
rasterList       <- c("forest", "agriculture", "impervious", "fwswetlands", "fwsopenwater", "slope_pcnt", "elevation", "surfcoarse", "percent_sandy", "drainageclass", "hydrogroup_ab")
conversionValues <- c(     100,           100,            1,           100,            100,            1,           1,          100,             100,               1,             100)

tableFolder <- "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/versions/pointDelineation/gisTables"

zoneField <- "DelinID"

statType = "MEAN"

catchmentsFilePath <- "C:/KPONEIL/delineation/northeast/pointDelineation/outputFiles/delin_basins_deerfield_2_17_2015.dbf"

outputName <- "pointDelineation"

damsFile <- "C:/KPONEIL/GitHub/projects/basinCharacteristics/tncDams/outputTables/barrierStats_pointDelineation.dbf"

# ==========
# Load files
# ==========

# Shapefile
# -----------
shapeAreas <- read.dbf(catchmentsFilePath)[,c(zoneField, "AreaSqKM")]


# Rasters
# -------
finalDF <- shapeAreas

# Loop through layers, reading files.
for (j in seq_along(rasterList)){
  
  # File path to table
  tableFilePath <- file.path(tableFolder, paste0(rasterList[j], ".dbf"))
  
  # Open table
  dbfTable <-read.dbf(tableFilePath)[,c(zoneField, statType, "AREA")]
  dbfTable$AREA <- dbfTable$AREA*0.000001 # convert to square kilometers
  dbfTable[which(dbfTable[,statType] == -9999), statType] <- NA # Replace all "-9999" values with "NA"
  
  # Output filepath
  outputTable <- file.path(baseDirectory, "versions", outputName, "rTables", paste0(rasterList[j], "_", statType, ".csv"))
  
  if ( !file.exists(outputTable) ){
    
    # Calculate the % of the catchment area with data and include in the output
    gisStat <- left_join(dbfTable, shapeAreas, by = zoneField) %>%
      mutate(percentAreaWithData = AREA/AreaSqKM*100)%>%
      select(-c(AREA, AreaSqKM))
    
    
    # save this as a file
    write.csv(gisStat, file = outputTable, row.names = F)
  } else (gisStat <- read.csv(outputTable))
  
  names(gisStat) <- c(zoneField, rasterList[j], paste0(rasterList[j], ".percentAreaWithData"))
  
  gisStat[names(gisStat) == rasterList[j]] <- gisStat[names(gisStat) == rasterList[j]] * conversionValues[j]
  
  
  
  if(is.null(finalDF)){finalDF <- gisStat} else(finalDF <- left_join(finalDF, gisStat, zoneField))
}


# TNC Dams
# --------

dams <- read.dbf(damsFile)

dams <- dams[,-2]

names(dams) <- c("DelinID", "deg_barr_1", "deg_barr_2", "deg_barr_3", "deg_barr_4", "deg_barr_6", "deg_barr_7")

dams$deg_barr_all <- rowSums (dams[,-1], na.rm = TRUE, dims = 1)



finalDF <- left_join(finalDF, dams, zoneField)

# Output file
# -----------

pointDelineationStats <- finalDF

# Save file
save(pointDelineationStats, file = paste0(baseDirectory, "/versions/pointDelineation/completedStats/pointDelineationStats.RData"))


#write.dbf(pointDelineationStats, file = paste0(baseDirectory, "/versions/pointDelineation/completedStats/pointDelineationStats.dbf"))
