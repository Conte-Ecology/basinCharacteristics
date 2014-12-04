rm(list = ls())

# Load libraries
library(foreign)
library(maptools)
library(dplyr)
library(tcltk)
library(RSQLite)
library(RSQLite.extfuns)

# User Input
# ==========
# Set the base directory
baseDirectory <- "C:/KPONEIL/GitHub/projects/basinCharacteristics/impoundments"

# Read in the dbf table of the catchments shapefile to get a list of the catchments to get impoundment data for.
COMIDs <- read.dbf ( "C:/KPONEIL/gis/nhdPlusV2/NENY_NHDCatchment.dbf" )$FEATUREID


# Read in data
# ============
# Read in the user input file
source( file.path(baseDirectory, "scripts/INPUTS.txt") )

# Read in NHDPlus tables
for( r in seq_along(nhdplusRanges)){

  # Plusflow tables
  plusFlowPath <- file.path(nhdplusFolder, paste0('NHDPlus', nhdplusRanges[r]), "NHDPlusAttributes/PlusFlow.dbf")
  plus <- read.dbf(plusFlowPath)
  if( r == 1 ) {plusflow <- plus} else( plusflow <- rbind(plusflow, plus) )

  # VAA tables
  VAAPath <- file.path(nhdplusFolder, paste0('NHDPlus', nhdplusRanges[r]), "NHDPlusAttributes/PlusFlowlineVAA.dbf")
  VAA <- read.dbf(VAAPath)[,c('ComID', 'LengthKM', 'TotDASqKM', 'Divergence')]
  if( r == 1 ) {reachInfo <- VAA} else( reachInfo <- rbind(reachInfo, VAA) )

}# end for (r)

# Read in impoundments tables created from GIS processing
for( s in seq_along(states)){
  
  # Impoundments tables
  impoundmentsPath <- file.path(baseDirectory, "outputFiles", outputName, paste0("impoundments_", states[s],".dbf") )
  impsState <- read.dbf(impoundmentsPath)
  impsState$Object_ID <- paste0(states[s], impsState$Object_ID)
  
  if( s == 1 ) {impoundments <- impsState} else( impoundments <- rbind(impoundments, impsState) )

}# end for (s)


# Edit tables
# ===========

# Rename for consistency
names(reachInfo) <- c('COMID', 'LENGTHKM', 'TotDASqKM', 'Divergence')
names(impoundments)[ which(names(impoundments) == 'RID' )] <- 'COMID'

# Correct for M-value which creates a slight offset/negative values.
mOffset <- min(impoundments$FMEAS)

if ( min(impoundments$FMEAS) < 0 ) {impoundments <-  arrange(impoundments, FMEAS) %>% 
                                      mutate(FMEAS =  FMEAS + abs(mOffset) ) %>%
                                      mutate(TMEAS =  TMEAS + abs(mOffset) )}
# Duplicates
# ----------
# Eliminate duplicate waterbodies in spatially overlapping areas. ("Object_ID" values differ because of differing source files, but all other attributes are the same.)
impoundments <- tbl_df(impoundments) %>% 
                  group_by(COMID, FMEAS, TMEAS, AreaSqKM) %>% # group to determine duplicates
                  arrange(Object_ID)%>%                       # arrange by Object_ID to ensure consistency in removal order(alphabetical)
                  filter(row_number() == 1)%>%                # filter out duplicates
                  group_by()                                  # remove grouping

# Eliminate duplicate waterbodies within catchments. If 2 waterbodies in a catchment have the exact same area then they should be removed.(see description)
impoundments <- arrange(impoundments, COMID, AreaSqKM) %>%  # order dataframe
      group_by(COMID, AreaSqKM) %>%              # group by catchment and waterbody
      filter(FMEAS == min(FMEAS)) %>%            # filter out the duplicate waterbodies within the catchment
      group_by()                                 # ungroup


# Add reach length
impInfo <- left_join(impoundments, reachInfo, by = 'COMID', all.x = T, all.y = F, sort = F)

# Calcualte the distance within the catchment from the endpoint of the flowline
impInfo <- mutate(impInfo, DistKM = FMEAS*LENGTHKM/100)

# Divergences to ignore in delineation
ignore <- reachInfo$COMID[reachInfo$Divergence == 2]

# Loop through all Catchment IDs getting impoundment info.
progressBar <- tkProgressBar(title = "Progress bah", 
                             min = 0, 
                             max = length(COMIDs), 
                             width = 300)

# Create output storage
impOut <- rep( list(list()), length(COMIDs) )

for ( i in seq_along(COMIDs) ){
  
  print(i)
  # Progress bar
  setTkProgressBar(progressBar, i, label=paste( round(i/length(COMIDs)*100, 0), "% done"))
  
  # Get the current catchment
  feature <- COMIDs[i]

  # Set up delineation list
  delin <- list(feature)  
  names(delin) <- reachInfo$LENGTHKM[ reachInfo$COMID == feature ]
  
  # Delineate upstream until distance limit is reached or the headwater is reached.
  while( any( as.numeric(names(delin)[ names(delin) != 'DONE' ]) < upstreamLimitKM ) ){
      
    # Get the next branch that needs to be delineated
    index <- which( as.numeric( names(delin) ) < upstreamLimitKM & names(delin) != 'DONE' )[1] 
    
    # Get the next reach of which to find the upstream reach
    curCOMID <- delin[[index]][1]
    
    # Get steram reaches immediately upstream. Coastal delineations are ignored (DIRECTION ==714). If FROMCOMID = 0 then it has no upstream segment.
    upstreamSegs <- plusflow$FROMCOMID[ which( plusflow$TOCOMID == curCOMID & plusflow$DIRECTION != 714 & plusflow$FROMCOMID != 0)  ]
    
    # Ignore minor reaches in a divergence
    upstreamSegs <- upstreamSegs[! upstreamSegs %in% ignore]
    
    # If there is no upstream segment then the delineation is complete, otherwise update the list of catchments and add to "delin"
    if( length(upstreamSegs) == 0 ) { names(delin)[index] <- 'DONE' 
      } else{
    
        # Where to start adding the new lists
        newIndex <- length(delin)
        
        # Loop through the immediate upstream segments
        for(k in seq_along(upstreamSegs)){
          
          # Append new list and name it with the total length
          delin[[ newIndex + k ]] <- c(upstreamSegs[k], delin[[index]])
          names(delin)[ newIndex + k ] <- as.numeric( names(delin)[index] ) + reachInfo$LENGTHKM[ reachInfo$COMID == upstreamSegs[k] ]
        }# End for (k)
  
      # Remove the old list
      delin <- delin[-index] 
    }# end if
  }# end while

  # List of all catchments in the delineation
  network <- unique(unlist(delin, use.names = F))
  
  t2 <- filter(impInfo, COMID %in% network)

  # Set up storage with current featureID. This also prevents script from dealing with end of branch in "downSegs"
  primary <- filter(t2, COMID %in% feature) %>%
              select(COMID, Object_ID, AreaSqKM, TotDASqKM, DistKM) 
  
  # Set up the queue of catchments to get values for
  queue <- network[-which(network == feature)]
  
  # Loop through the entire delineation
  for (j in 1:length(delin)){
    
    #Select the branch
    branch <- delin[[j]]
    
    # Add impoundments for all catchments in that branch
    while( any(queue %in% branch) ){
    
      # Current catchment
      curID <- queue[queue %in% branch][1]
    
      ind <- which(branch == curID)
      
      # Downstream segments
      downSegs <- branch[(ind + 1): length(branch)]
    
      # Total length to catchment
      curDist <- sum ( filter(reachInfo, COMID %in% downSegs) %>% select(LENGTHKM) )
    
      # Get info for all impoundments in current catchment
      newImps <- filter(impInfo, COMID == curID) %>%
                  mutate(DistKM = DistKM + curDist) %>%
                  select(COMID, Object_ID, AreaSqKM, TotDASqKM, DistKM)
    
      # Join with primary dataframe
      primary <- rbind(primary, newImps)
    
      # Remove current catchment from queue
      queue <- queue[-which(queue == curID)]
    }# end while
  }# end for (j)
  
  
  # If there are impoundments in the catchment, do some manipulation, else add one row of NAs
  # Remove duplicate waterbodies 
    # Take the minimum distance to each one. (The same waterbody upstream is an error from incosistency between flowlines and waterbodies)
    # Might want to check the efficacy of "Object_ID" vs "AreaSqKM" here
  if( nrow(primary) > 0 ) {primary <- group_by(primary, Object_ID) %>% 
                                       filter(DistKM == min(DistKM)) %>% 
                                       group_by() %>% 
                                       mutate(FEATUREID = feature)}    # Add FEATUREID
    else( primary <- tbl_df(data.frame(COMID = NA, Object_ID = NA, AreaSqKM = NA, TotDASqKM = NA, DistKM = NA, FEATUREID = feature)) )
  
  # Store output
  impOut[[i]] <- primary
  
}# end for (i)
close(progressBar)

save(impOut, file = file.path(baseDirectory, 'products' , paste0('impoundmentsByNHDCatchment_', outputName, '_RAW.RData')) )


require(data.table)
impoundmentsByNHDCatchment <- rbindlist(impOut)

save(impoundmentsByNHDCatchment, file = file.path(baseDirectory, 'products' , paste0('impoundmentsByNHDCatchment_', outputName, '.RData')) )




# Eliminate duplicated 
# Check for  duplicates: compare the results here with some instances of large waterbodies that get assigned to multiple catchments
###########################################
#if ( any(duplicated(primary$AreaSqKM) == TRUE) )
#group_by(impOut, FEATUREID, AreaSqKM, Object_ID) %>% 
#  filter(DistKM == min(DistKM)) %>% 
#  group_by() %>% 
###########################################






# Re-format
impoundmentsByNHDCatchment <- as.data.frame(impOut)

# Write out results
save(impoundmentsByNHDCatchment, file = file.path(baseDirectory, 'products' , paste0('impoundmentsByNHDCatchment_', outputName, '.RData')) ) 

