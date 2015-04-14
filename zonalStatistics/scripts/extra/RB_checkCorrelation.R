rm(list = ls())

library(dplyr)
library(ggplot2)

setwd('C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/versions/riparianBuffers/completedStats')


# 50 ft buffer
# ------------
load('zonalStatsForDB_riparianBuffers50ft_2015-04-10.RData')

b50 <- mutate(dbStats, variable = sub("_50ft","",variable)) %>%
        filter(variable != "AreaSqKM") %>%
        mutate(buf_50ft = value)%>%
        select ( - value)

# 200 ft buffer
# ------------
load('zonalStatsForDB_riparianBuffers200ft_2015-04-10.RData')

b200 <- mutate(dbStats, variable = sub("_200ft","",variable)) %>%
          filter(variable != "AreaSqKM") %>%
          mutate(buf_200ft = value)%>%
          select ( - value)


buffMaster <- left_join(b200, b50, by = c('FEATUREID', 'variable', 'zone'))


save(buffMaster, file = "C:/KPONEIL/workspace/buffMasterFlex.RData")

load( file = "C:/KPONEIL/workspace/buffMaster.RData")


corrPlot <- ggplot( buffMaster, aes(buf_50ft, buf_200ft)) +  
                      geom_point(aes(buf_50ft, buf_200ft), size = 0.5) +
                      facet_wrap(~variable)

