# Compare Missing data areas

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


for ( i in seq_along(rasterList)){

  print(i)
  
  upstream  <- read.csv(file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_", rasterList[i], "_", statType, ".csv")))[,c(zoneField, "percentAreaWithData")]
  names(upstream)[2] <- rasterList[i]
  
  if( i == 1 ) { allPcnts <- upstream } else( allPcnts <- left_join(allPcnts, upstream, by = zoneField))
}

nlcd <- c("agriculture", "devel_hi", "devel_low", "devel_med", "devel_opn", "developed", "forest", "forest_decid", "forest_evgrn", "forest_mixed", "herbaceous", "water", "wetland")
undev <- "undev_forest"
fws <- c("alloffnet", "allonnet", "fwsopenwater", "fwswetlands", "openoffnet", "openonnet")    
ssurgo <- "surfcoarse"
nalcc <- "elev_nalcc"




temp <- allPcnts[,c(1,which(names(allPcnts) %in% fws))]


temp[temp$FEATUREID == 730076,]



for( j in 3:length(names(temp))){
  
  diff <- temp[,j] - temp[,2]
  
  print(length(which(diff !=0)))
  print(range(diff))
  
}

ex <- temp[which(diff !=0),]








