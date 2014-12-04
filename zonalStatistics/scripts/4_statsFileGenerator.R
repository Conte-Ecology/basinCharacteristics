# Catchment Stats Generator

# Files directory

# Inputs 
# ------
versionDirectory <- "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/versions/NENY_HRD"
statType <- 'MEAN'
zoneField <- 'FEATUREID'


localStatFiles <- list.files(path=file.path(versionDirectory, "rTables"), pattern = "local_")

for ( L in 1:length(localStatFiles) ){
  
  localTemp <- read.csv(localStatFiles[L])
  
  # Get file name
  A <- gsub("*local_", "", localStatFiles[L])
  variableName <- gsub(paste0("*_", statType,".csv"), "", A)
  
  names(localTemp) <- c(zoneField, variableName)
  
  if( L == 1) {LocalStats <- localTemp} else(LocalStats <- left_join(LocalStats, localTemp) )
  
}


upstreamStatFiles <- list.files(path=file.path(versionDirectory, "rTables"), pattern = "upstream_")

for ( L in 1:length(upstreamStatFiles) ){
  
  upstreamTemp <- read.csv(upstreamStatFiles[L])
  
  # Get file name
  A <- gsub("*upstream_", "", upstreamStatFiles[L])
  variableName <- gsub(paste0("*_", statType,".csv"), "", A)
  
  names(upstreamTemp) <- c(zoneField, variableName)
  
  if( L == 1) {UpstreamStats <- upstreamTemp} else(UpstreamStats <- left_join(UpstreamStats, upstreamTemp) )
  
}



