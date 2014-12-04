delineateUpstreamCatchments <- function(catchmentsDataTable){
  
  # For prorgess bar
  require(tcltk)
  
  # Pull the catchment IDs to delineate
  features <- unique(catchmentsDataTable[,c(zoneField)])
  
  # Create empty list for saving
  delineatedCatchments <- list()
  
  # Set progress bar
  progressBar <- tkProgressBar(title = "progress bar", min = 0, max = length(features), width = 300)
  
  # Loop through all catchments
  for ( i in 1:length(features)){
  
    # List of flowline segments to save
    segments<-c() 
    
    # Queue of flowline segments that need to be traced upstream
    queue<-c(features[i]) 
    
    while (length(queue)>0) {
      
      # Save all of the segments
      segments<-c(segments,queue)
     
      # Which catchments flow into the ones in the current queue
      queue<-c(catchmentsDataTable[catchmentsDataTable$NextDownID %in% queue, zoneField])
      
      # Eliminate duplicates
      queue<-unique(queue)
      
      # Eliminates queuing flowlines that have already been added to segments
      queue<-queue[!(queue %in% segments)]
      
    }# end while loop
    
    # Double check duplicates
    delineatedCatchments[[i]] <-unique(segments)
    names(delineatedCatchments)[i] <- features[i]
    
    # Update progress bar
    setTkProgressBar(progressBar, i, label=paste( round(i/length(features)*100, 2), "% done"))
    
  }# end for loop
  
  close(progressBar)
  
  return(delineatedCatchments)
}
