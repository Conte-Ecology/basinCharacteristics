Zonal Statistics
================

This folder is set up to run zonal statistics on the rasters produced in other sections of the `basinCharacteristics` repo. 


## Setup: 

- The completed rasters from other sections serve as input to these scripts. These rasters reside in the `zonalStatistics/gisFiles/rasters` folder.
- The shapefile of the catchments for which the statistics will be evaluated resides in the `zonalStatistics/gisFiles/vectors` folder.
- These two folders are not created automatically and must exist before running the scripts.
- The scripts to run begin with numbers to signify the order in which they should be executed. A description of this process exists in the next section.

## Steps to Run:

1. `INPUTS.txt` - This file is used to specify common user inputs that will be used across python and R scripts

  Open this file in the `/scrpits` folder. Open the file and change the variables as necessary. Do not add extra lines or change the structure of this file other than changing the names.
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. `NortheastHRD` for all High Resolution Catchments)
 - "catchmentsFileName" is the name of the catchments shapefile without extension (e.g. `NortheastHRD_Catchments`)
 - "zoneField" the name of the field that is used to identify features (e.g. `FEATUREID`)
 - "statType" is the statistic to calculate (e.g. `MEAN`)
 - "rasterList" is a list of the rasters to run (e.g. `c("forest", "agricuture", "fwswetlends")` ). If all rasters in the `raster` directory are to be run, set this variable to `c("ALL")`

2. `1_zonalStatisticsProcessing_GIS.py` - This script calculates statistics on the raster dataset for each of the catchments in the polygon shapefile. The primary tool used is "Zonal Statistics" in ArcGIS. If the "ZonalStatisticsAsTable" tool runs slowly, make sure that the zone field has been indexed. Also try closing other programs that may be using excessive memory/CPU processing power. This script outputs the specified spatial statistic for all of the catchments as `.dbf` tables in the `gisTables` folder in the run-specific versions folder (e.g. `zonalStatistics/versions/NortheastHRD/gisTables/forest_MEAN.dbf`). Example output:

  | FEATUREID | COUNT  |    AREA    |    MEAN    |
  |  :-----:  | ------ | ---------- | ---------- |
  |   350854  |   6    | 9608.108   | 0.00000000 |
  |   350855  |   1    | 1601.351   | 0.00000000 |
  |   350881  |  327   | 523641.872 | 0.20795107 |
  |   350888  |  105   | 168141.886 | 0.03809524 |
  |   350891  |  83    | 132912.157 | 0.22891566 |
  |   350897  |   6    | 9608.108   | 0.16666667 |


  Open this script and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder. Run the script in Arc Python. Allow script to run completely before moving on to the next script. 


3. `2_delineateUpstreamCatchments.R` - This script uses the catchment relationships built into the shapefile to generate a delineation of the network from each catchment. The output is a file in `.RData` containing a list of lists. The greater list is comprised of all of the catchments in the original shapefile. Each sublist contains all of the catchments upstream of that particuar catchment.

  If this script has not been run and the delineated catchments `.RData` file does not exist, then open this script in R and set the "baseDirectory" as in previous scripts. Run the script. If the delineated catchments file does exist, ensure proper naming of the file, and move it to the same directory as the tables folders (e.g. `zonalStatistics/versions/NortheastHRD/NortheastHRD_delineatedCatchments.RData`). If the script has already been run, the file should already be in the proper folder.



4. `3_calculateUpstreamStatistics.R` - The primary function of this script is to use the output from the zonal statistics step with the `_delineatedCatchments` to generate values for upstream statistics in each catchment. For each individual catchment, the average of the values of all catchments in the upstream network are averaged (weighted by drainage area). The script also converts the stats output from the zonal statistics step (`.dbf` tables) to `.csv` files for uniformity. The script outputs two `.csv` files, 1 upstream and 1 local, for each variable into the `rTables` directory (e.g. `zonalStatistics\versions\NortheastHRD\rTables\upstream_forest_MEAN.csv`). Example output:

  | FEATUREID |    COUNT     |
  |  :-----:  | ------------ |
  |   730262  |  0.308928975 |
  |   730263  |  0.341887629 |
  |   730264  |     NA       |
  |   730265  |  0.461261261 |
  |   730266  |  0.199       |

  Open this script in R and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder and run the script. 

  

5. `4_statsFileGenerator.R` - This is a simple script to generate custom `.RData` files of zonal statistics for both local and upstream variables. It reads in the individual `.csv` files and outputs a combined `.RData` file with two dataframes: "LocalStats" and "UpstreamStats"

  Open this script in R and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder and run the script. Specify the variables to include in "outputVariables" (set as "ALL" to include all variables present).
 

## Future Work:

This repo is currently set up for functional use. Converting the processes to functions for packaging is in progress, but will depend on whether or not this is going to be used outside of the web system.


