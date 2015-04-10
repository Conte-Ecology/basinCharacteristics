Zonal Statistics
================

This repo stores the necessary scripts and files to calculate basin characteristics for the layers created in the `basinCharacteristics` parent directory.

## Setup Info: 

- The completed rasters from other sections serve as input to these scripts. These rasters reside in the `zonalStatistics/gisFiles/rasters` sub-folder.
- The shapefile of the catchment polygons for which the statistics will be evaluated resides in the `zonalStatistics/gisFiles/vectors` sub-folder.
- These two folders must be created before running the scripts. All other folders are created within the scripts.
- The scripts to run begin with numbers to signify the order in which they should be executed. Letters preceding the numbers indicate scripts for a specified version (e.g. "RB" indicates the script series for Riparian Buffer stats. A description of this process for each version exists in the next sections. Each time a new version is added, this README file should be updated.


## Current Versions:

### Catchments for High Resolution Delineation:

#### Description
This section calculates the basin characteristics for the high resolultion delineation (HRD) catchments. For each catchment, 2 values are calculated:
1. Local - The spatial average of the variable within the individual catchment polygon.
2. Upstream - The spatial average of all of the local values calculated for all of the catchments in the upstream network. The spatial average is weighted buy indiviudal catchment area and is accurate to the downstream point of the specified catchment.

In addition to the values for each catchment, the percent of the catchment area with data is calculated for each catchment. This accounts for cases where there is missing raster data within the catchment boundary. This is determined by dividing the "AREA" column output by the Zonal Statistics tool by the area of the rasterized version of the catchments.


#### Steps to Run
1. `HRD_INPUTS.txt` - This file is used to specify common user inputs that will be used across python and R scripts

  Open this file in the `/scrpits` folder. Open the file and change the variables as necessary. Do not add extra lines or change the structure of this file other than changing the names.
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. `NortheastHRD` for all High Resolution Catchments)
 - "catchmentsFileName" is the name of the catchments shapefile without extension (e.g. `NortheastHRD_AllCatchments`)
 - "zoneField" is the name of the field that is used to identify features (e.g. `FEATUREID`)
 - "statType" is the statistic to calculate (e.g. `MEAN`)
 - "discreteRasters" is list of the discrete, or categorical, data layers  to run such as land use (e.g. `forest`)
 - "continuousRasters" is list of the continuous data layers  to run such as climate or elevation data (e.g. `ann_tmax_c`)

2. `HRD1_zonalStatisticsProcessing.py` - This script calculates statistics on the raster dataset for each of the catchments in the polygon shapefile. The primary tool used is "Zonal Statistics" in ArcGIS. Make sure that the zone field in the shapefile has been indexed. This step will increase the tool performance. The script outputs the specified spatial statistic for all of the catchments as `.dbf` tables in the `gisTables` folder in the run-specific versions folder (e.g. `zonalStatistics/versions/NortheastHRD/gisTables/forest_MEAN.dbf`). 

  Open this script and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder. Run the script in Arc Python. Allow script to run completely before moving on to the next script. This script does the following:
    a. Reads user-specified inputs from Step 1
    b. Sets up the folder structure in the specified directory
    c. Reprojects & resamples the rasters to match the zone layer (Catchments)
    d. Calculates the mean value for each zone in the zone shapefile (Zonal Statistics)
    e. Adds -9999 values for zones that are not assigned any value

  Example output:

  | FEATUREID | COUNT  |    AREA    |    MEAN    |
  |  :-----:  | ------ | ---------- | ---------- |
  |   350854  |   6    | 9608.108   | 0.00000000 |
  |   350855  |   1    | 1601.351   | 0.00000000 |
  |   350881  |  327   | 523641.872 | 0.20795107 |
  |   350888  |  105   | 168141.886 | 0.03809524 |
  |   350891  |  83    | 132912.157 | 0.22891566 |
  |   350897  |   6    | 9608.108   | 0.16666667 |


3. `HRD2_delineateUpstreamCatchments.R` - This script uses the catchment relationships built into the shapefile to generate a delineation of the network from each catchment. The output is a file in `.RData` containing a list of lists. The greater list is comprised of all of the catchments in the original shapefile. Each sublist contains all of the catchments upstream of that particuar catchment. The sublists are named by their primary (most downstream) catchment and can be accesed by the $ operator (e.g. `delineatedCatchments$'730076'`).

  If this script has not been run and the delineated catchments `.RData` file does not exist, then open this script in R and set the "baseDirectory" as in previous scripts. Run the script which outputs the file to the proper folder. If the delineated catchments file does exist in the proper location, the script will not run. If the file is created separately, ensure proper naming of the file and move it to the same directory as the tables folders (e.g. `zonalStatistics/versions/NortheastHRD/NortheastHRD_delineatedCatchments.RData`).


4. `HRD3_calculateUpstreamStatistics.R` - The primary function of this script is to use the output from the zonal statistics step with the `_delineatedCatchments` object to generate values for upstream statistics in each catchment. The variables listed in the `HRD_INPUTS.txt` file will be processed. For each individual catchment, the variable values for all catchments in the upstream network are averaged (weighted by area). For each catchment, the percent of the area with data is calculated. This is to account for missing raster data within the catchments. The output from the zonal statistics step (`.dbf` tables) to `.csv` files for uniformity. The script outputs two `.csv` files, 1 upstream and 1 local, for each variable into the `rTables` directory (e.g. `zonalStatistics\versions\NortheastHRD\rTables\upstream_forest_MEAN.csv`). 

  Open this script in R and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder and run the script. 
  
  Example output:
  
  | FEATUREID |     MEAN    | percentAreaWithData |
  | :-------: | ----------- | ------------------- |
  | 730236    |	0.24288425	|  0.654682783        |
  | 730243    |	0.052083333	|  3.098773402        |
  | 730246    |	0.237735849	|  0.936120106        |
  | 730252    |	0.400487975	|  11.82605111        |
  | 730254    |	0.412833724	|  93.07699015        |

 
5. `HRD4_statsFileGenerator.R` - This is a simple script to generate custom `.RData` files of zonal statistics for both local and upstream variables. It reads in the individual `.csv` files and outputs a combined `.RData` file with two dataframes: "LocalStats" and "UpstreamStats". It also outputs a long format dataframe for input into the web system database.

  Open this script in R and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder and run the script. Specify the variables to include in "outputVariables". There are 3 options for specifying the variables to output:
  1. "ALL" will include all of the variables present in the folder
  2. NULL will include the variables from the "rasterList" object in the "RB_INPUTS.txt" file
  3. Manually list the variables to output (do not include the buffer specification)
  
  This script also pulls factors from the "Covariate Data Status - High Res Delineation.csv" (a duplicate of the excel spreadsheet with the same name). The factors convert the zonal values to the values used in models and on the web system (e.g. fraction to percent).
 
 
### Riparian Buffers for High Resolution Flowlines:

#### Description
The scripts in this section are dependent on some elements of the overall HRD zonal statistics process, which should be completed first for all layers and ranges used in this section. First, the rasters are processed in the HRD section to be resampled and reprojected to match the catchments and each other. The scripts in this section rely on these previously processed rasters, pointing to the repo that contains the existing files. Second, the network delineation is identical to the HRD network. The `NortheastHRD_delineatedCatchments.RData` file from that section is referenced directly from this section. These steps are taken primarily to save time and data storage space. Development of stand-alone repos is possible.

The calculation of basin characteristics for the riparian buffers is based on the overlapping polygons. The process does not account for the overlapping area of the polygons which essentially gets double counted. This area amounts to a roughly 0.001 - 0.01 square kilometers.

In the scripts in this section, the term "catchments" is often used in place of "buffers". This is simply for ease of use in making code interchangeable and not meant to cause confusion.

#### Steps to Run
1. `RB_INPUTS.txt` - This file is used to specify common user inputs that will be used across python and R scripts

  Open this file in the `/scrpits` folder. Open the file and change the variables as necessary. Do not add extra lines or change the structure of this file other than changing the names.
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. `riparianBuffers` for all High Resolution Catchments)
 - "catchmentsFilePath" is the name of the catchments shapefile without extension (e.g. `"C:/KPONEIL/gis/riparianBuffers/NortheastHRD/overlappingBuffers.gdb/riparianBufferOverlap_ALL_200ft"`)
 - "bufferID" the name of the field that is used to identify the buffer distance and separate runs (e.g. `200ft`)
 - "zoneField" is the name of the field that is used to identify features (e.g. `FEATUREID`)
 - "statType" is the statistic to calculate (e.g. `MEAN`)
 - "rasterList" is list of the rasters to run (e.g. `c("devel_hi", "devel_low", "devel_med", "devel_opn", "developed", "forest", "impervious", "tree_canopy")`)
 - "hucFilePath" is the file path to the shapefile used to split the large buffer files into sections small enough to process (e.g. `"C:/KPONEIL/gis/riparianBuffers/NortheastHRD/processingFiles.gdb/overlappingHucs"`)
- "rasterDirectory" is the path to the directory containing the rasters to run (e.g. `"C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/gisFiles/versions/NortheastHRD/projectedRasters.gdb"`)
 
 
2. `RB1_zonalStatisticsProcessing.py` - This script calculates statistics on the raster dataset for each of the buffers in the polygon shapefile. The primary tool used is "Zonal StatisticsAsTable2" in ArcGIS. This tool is modified from the original to be able to run zonal statistics on overlapping polygons. The tool is downloaded from here: http://blogs.esri.com/esri/arcgis/2013/11/26/new-spatial-analyst-supplemental-tools-v1-3/#comment-7007. Make sure that the zone field in the shapefile has been indexed. This step will increase the tool performance. The script outputs the specified spatial statistic for all of the buffer polygons as `.dbf` tables in the `gisTables` folder in the run-specific versions folder (e.g. `zonalStatistics/versions/riparianBuffers/gisTables/forest_MEAN.dbf`). The script also outputs the polygon areas as a `.dbf` file. 

  Open this script and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder. Run the script in Arc Python. Allow script to run completely before moving on to the next script. This script does the following:
    a. Reads user-specified inputs from Step 1
    b. Sets up the folder structure in the specified directory
    c. Reprojects the zone and HUC polygons as needed
    d. Calculates the mean value for each zone in the zone shapefile (broken up by section)
    e. Joins all of the sections and elminiates duplicate features
    f. Adds -9999 values for zones that are not assigned any value
    g. Calculates the areas for the buffer polygons in the shapefile

  Example output:

  | FEATUREID | COUNT  |    AREA    |    MEAN    |
  |  :-----:  | ------ | ---------- | ---------- |
  |   350854  |   6    | 9608.108   | 0.00000000 |
  |   350855  |   1    | 1601.351   | 0.00000000 |
  |   350881  |  327   | 523641.872 | 0.20795107 |
  |   350888  |  105   | 168141.886 | 0.03809524 |
  |   350891  |  83    | 132912.157 | 0.22891566 |
  |   350897  |   6    | 9608.108   | 0.16666667 |


3. `RB2_calculateUpstreamStatistics.R` - The primary function of this script is to use the output from the zonal statistics step with the `_delineatedCatchments` object to generate values for upstream statistics in each catchment. The variables listed in the `RB_INPUTS.txt` file will be processed. For each individual buffer polygon, the variable values for all buffers in the upstream network are averaged (weighted by area). The script also converts the stats output from the zonal statistics step (`.dbf` tables) to `.csv` files for uniformity. The script outputs two `.csv` files, 1 upstream and 1 local, for each variable into the `rTables` directory (e.g. `zonalStatistics\versions\riparianBuffers\rTables\upstream_forest_200ft.csv`). 

  Open this script in R and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder and run the script. 

  Example output:

  | FEATUREID |    MEAN      |
  |  :-----:  | ------------ |
  |   730243  |      0       |
  |   730254  |  0.296062992 |
  |   730258  |       0.25   |
  |   730259  |  0.029126214 |
  |   730260  |  0.266112266 |


4. `RB3_statsFileGenerator.R` - This is a simple script to generate custom `.RData` files of zonal statistics for both local and upstream variables. It reads in the individual `.csv` files and outputs a combined `.RData` file with two dataframes: "LocalStats" and "UpstreamStats". It also outputs a long format dataframe for input into the web system database.

  Open this script in R and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder and run the script. Specify the variables to include in "outputVariables". There are 3 options for specifying the variables to output:
  1. "ALL" will include all of the variables present in the folder
  2. NULL will include the variables from the "rasterList" object in the "RB_INPUTS.txt" file
  3. Manually list the variables to output (do not include the buffer specification)
  
This script also pulls factors from the "Covariate Data Status - High Res Delineation.csv" (a duplicate of the excel spreadsheet with the same name). The factors convert the zonal values to the values used in models and on the web system (e.g. fraction to percent).
 
### Point Delineation for MassDOT Project: 

#### Description
The scripts in this section are dependent on the raster processing completed in the HRD section (resampling and reprojecting each raster to match the catchments and each other). The scripts in this section point to the repo that contains the existing files. These steps are taken primarily to save time and data storage space. Development of stand-alone repos is possible.

#### Steps to Run

1. `PD1_zonalStatisticsProcessing.py` - This script calculates statistics on the raster dataset for each of delineated basins in the polygon shapefile. The primary tool used is "Zonal StatisticsAsTable2" in ArcGIS. This tool is modified from the original to be able to run zonal statistics on overlapping polygons. The tool is downloaded from here: http://blogs.esri.com/esri/arcgis/2013/11/26/new-spatial-analyst-supplemental-tools-v1-3/#comment-7007. Make sure that the zone field in the shapefile has been indexed. This step will increase the tool performance. The script outputs the specified spatial statistic for all of the buffer polygons as `.dbf` tables in the `gisTables` folder in the run-specific versions folder (e.g. `zonalStatistics/versions/pointDelineation/gisTables/forest_MEAN.dbf`). The script also outputs the polygon areas as a `.dbf` file. 

  Open this script and set the "baseDirectory" variable to the path up to and including the `zonalStatistics` folder. Unlike other versions, the user inputs are entered directly in the script file and not a separate input file.
  
   - "outputName" is the name that will be associated with this particular run of the tool (e.g. `riparianBuffers` for all High Resolution Catchments)
 - "catchmentsFilePath" is the name of the catchments shapefile without extension (e.g. `"C:/KPONEIL/delineation/northeast/pointDelineation/outputFiles/delin_basins_deerfield_2_17_2015.shp`)
 - "zoneField" is the name of the field that is used to identify features (e.g. `DelinID`)
 - "rasterDirectory" is the path to the directory containing the rasters to run (e.g. `"C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/gisFiles/versions/NortheastHRD/projectedRasters.gdb"`)
 - "rasterList" is list of the rasters to run (e.g. `["forest", "agriculture", "impervious", "fwswetlands", "fwsopenwater", "slope_pcnt", "elevation", "surfcoarse", "percent_sandy", "drainageclass", "hydrogroup_ab"]`)
 - "statType" is the statistic to calculate (e.g. `MEAN`)

  This script does the following:
    a. Sets up the folder structure in the specified directory
    b. Reprojects the zone polygon as needed
    c. Calculates the mean value for each zone in the zone shapefile
    d. Adds -9999 values for zones that are not assigned any value

  Example output:

  | FEATUREID | COUNT  |    AREA    |    MEAN    |
  |  :-----:  | ------ | ---------- | ---------- |
  |   350854  |   6    | 9608.108   | 0.00000000 |
  |   350855  |   1    | 1601.351   | 0.00000000 |
  |   350881  |  327   | 523641.872 | 0.20795107 |
  |   350888  |  105   | 168141.886 | 0.03809524 |
  |   350891  |  83    | 132912.157 | 0.22891566 |
  |   350897  |   6    | 9608.108   | 0.16666667 | 
 
2. `PD2_finalizeZonalStatistics.R` - 

