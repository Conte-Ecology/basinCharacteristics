rm(list=ls())

library(dplyr)

# ======
# Inputs 
# ======
baseDirectory <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics'

bufferIDs <- c("50ft", "100ft", "200ft")

# ========================
# Read user-defined inputs
# ========================
source( file.path(baseDirectory, "scripts", "RB_INPUTS.txt") )


covariates <- NULL

for (buff in bufferIDs){

  print(paste0("Processing the covariates for the ", buff, " buffer file."))
  
  # Save the output as CSV
  curTable <- read.csv(file = file.path(baseDirectory, "versions", outputName, "completedStats", paste0("zonalStatsForDB_", outputName, buff, "_", Sys.Date(), ".csv")))
  
  vars <- unique(curTable$variable)
  
  for ( i in seq_along(vars) ) {
  
    curVar <- filter(curTable, variable == vars[i])%>%
                select(value)
  
    print(paste0("Range of variable ", vars[i], " is ", range(curVar, na.rm = T)[1], " to ", range(curVar, na.rm = T)[2]))
  }
  
  if( is.null(covariates) ){ covariates <- curTable } else( covariates <- rbind(covariates, curTable) )

}




a <- filter(covariates, variable == "impervious_50ft") %>% select(featureid, value)
b <- filter(covariates, variable == "impervious_100ft") %>% select(featureid, value)
C <- filter(covariates, variable == "impervious_200ft") %>% select(featureid, value)



test <- left_join(a, b, by = "featureid")









# Save the output as CSV
write.csv(covariates, 
          file = file.path(baseDirectory, "versions", outputName, "completedStats", paste0("covariates.csv")),
          row.names = FALSE)









