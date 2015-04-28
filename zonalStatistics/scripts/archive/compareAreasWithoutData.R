# Compare Missing data areas

rm(list=ls())

# ==============
# Load libraries
# ==============
library(reshape2)
library(foreign)
library(tcltk)
library(dplyr)
library(ggplot2)

#=======================
# Set the Base Directory
#=======================
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'

# ==========
# Load files
# ==========

source( file.path(baseDirectory, "scripts", "HRD_INPUTS.txt") )

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
elevation <- "elevation"
undevFor <- c("undev_forest")


# =================================
# Measure if missing data are equal
# =================================
temp <- allPcnts[,c(1,which(names(allPcnts) %in% fws))]

for( j in 3:length(names(temp))){
  
  diff <- temp[,j] - temp[,2]
  
  print(names(temp)[j])
  print(paste0("Number of differences: ", length(which(diff !=0))))
  print(paste0("Range of differences: ", range(diff)[1], " to ", range(diff)[2]))
  print(paste0("Number of catchments missing data: ", length(which(temp[,j] < 100))))
  
}


# ===============================
# Look at missing data histograms
# ===============================

VARS <- c("agriculture", "fwswetlands", "surfcoarse", "elevation", "aug_prcp_mm", "undev_forest")
#VARS <- "undev_forest"

toHist <- allPcnts[,c(which(names(allPcnts) %in% VARS))]

toHist_melt <- melt(toHist)

# Use this one
# ------------
trimHist <- ggplot(toHist_melt,aes(x=value)) + 
  geom_histogram(binwidth = 0.5) + 
  coord_cartesian(ylim = c(0, 50000)) +
  xlab("Percent Area With Data") +
  ylab("Number of Catchments") +
  theme(text = element_text(size=20)) +
  facet_wrap(~variable, nrow = 3)

print(trimHist)
ggsave("C:/KPONEIL/presentations/plt.png", width = 12, height = 9, dpi = 120)

rawHist <- ggplot(toHist_melt,aes(x=value)) + 
  geom_histogram(binwidth = 0.5) + 
  facet_wrap(~variable)



trimHist2 <- ggplot(toHist_melt,aes(x=value)) + 
  geom_histogram(binwidth = 0.5) + 
  coord_cartesian(ylim = c(0, 1000)) +
  facet_wrap(~variable)


# ==================================
# Look at missing across all sources
# ==================================


toMin <- allPcnts[,c(1, which(names(allPcnts) %in% VARS))]

out <- group_by(toMin, FEATUREID) %>%
  mutate(MIN = min(agriculture, fwswetlands, surfcoarse, elevation))%>%
  ungroup()

allMissing <- ggplot(out,aes(x=MIN)) + 
  geom_histogram(binwidth = 0.5) + 
  coord_cartesian(ylim = c(0, 10000))

names(out) <- c('FEATUREID', 'NLCD', 'FWS_Wetlands', 'SSURGO', 'NALCC_Elevation', 'All_Catchments')


# ===============================
# Compare amounts of missing data
# ===============================

outTable <- out[,-1]

comparePcnts <- c(100, 95, 90, 50)

pcnts <- apply(outTable,2, function(x) {length(which(x == 100) == TRUE)})/nrow(outTable)*100

for( m in comparePcnts){
  
  under <- apply(outTable,2, function(x) {length(which(x < m) == TRUE)})/nrow(outTable)*100

  pcnts <- rbind(pcnts, under) 
}


# Add 0%
pcnts <- rbind(pcnts, apply(outTable,2, function(x) {length(which(x == 0) == TRUE)})/nrow(outTable)*100)


rownames(pcnts) <- c("100%", paste0("Less than ", comparePcnts, "%"), "0%")




