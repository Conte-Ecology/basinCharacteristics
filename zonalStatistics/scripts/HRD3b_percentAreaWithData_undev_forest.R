rm(list=ls())

# ==============
# Load libraries
# ==============
#library(reshape2)
#library(foreign)
#library(tcltk)
library(dplyr)
#library(lazyeval)

#=======================
# Set the Base Directory
#=======================
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'

# ==========
# Load files
# ==========

# User inputs
# -----------
source( file.path(baseDirectory, "scripts", "HRD_INPUTS.txt") )

# ===================================
# Replace percentAreaWithData columns
# ===================================

# Local files
indLocal <- read.csv(file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_forest_", statType, ".csv")))

depLocal <- read.csv(file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_undev_forest_", statType, ".csv")))

depLocalOut <- select(depLocal, -percentAreaWithData)%>%
                left_join(select(indLocal, -MEAN), by = zoneField)

write.csv(depLocalOut, 
            file = file.path(baseDirectory, "versions", outputName, "rTables", paste0("local_undev_forest_", statType, ".csv")),
            row.names = F)


# Upstream Files
indUpstream <- read.csv(file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_forest_", statType, ".csv")))

depUpstream <- read.csv(file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_undev_forest_", statType, ".csv")))

depUpstreamOut <- select(depUpstream, -percentAreaWithData)%>%
                    left_join(select(indUpstream, -MEAN), by = zoneField)

write.csv(depUpstreamOut, 
            file = file.path(baseDirectory, "versions", outputName, "rTables", paste0("upstream_undev_forest_", statType, ".csv")),
            row.names = F)

