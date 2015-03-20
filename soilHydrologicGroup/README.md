Hydrologic Group
================

This script produces a spatial dataset of hydrologic group classifications based on the Soil Survey Geographic Database (SSURGO).


## Data Sources
| Layer   | Source                                                | Link                                                           |
|:-----:  | ------                                                | ----                                                           |
| SSURGO  | USDA-NRCS (download through Geospatial Data Gateway)  | http://datagateway.nrcs.usda.gov/GDGOrder.aspx?order=QuickState    Select: "2014 Gridded Soil Survey Geographic (gSSURGO) by State or Conterminous U.S."|

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be kept in the same format as it is downloaded.

1. Download the data by state and unzip the `soils\gssurgo_g_[state abbreviation].zip` sub-folder into the `sourceFolder` directory

Open the script `soilsHydrologicGroup`

2. Change the values in the "Specify inputs" section of the script
 - "baseDirectory" is the path to the `soilsHydrologicGroup` folder (current parent working directory)
 - "states" is the list of state abbreviations included in the desired range
 - "sourceFolder" is the source folder of the wetlands datasets by state
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. "Northeast")
 - "hydroGroups" is a list of lists describing the classifications to process. The first element in each sublist is the SQL where clause defining which hydrologic groups to select. The second element in the sublist is the name to assign to that selection.
 
3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Creates an empty raster of the entire specified range
   - Merges the necessary data tables in order to connect spatial data to necessary soil classification
   - Loops through the state polygons, creating state rasters of the surficial coarseness category
   - Mosaicks all of the state raster and the full range empty raster



## Output Rasters

In total, 5 rasters are generated. They table below lists the raster names and the hydrologic groups included in each.

|  Raster Name  |  Hydrologic Groups  |
|:-------------:| ------------------- |
| hydgrp_a      |  A                  |
| hydgrp_ab     |  A & B              |
| hydgrp_cd     |  C & D              |
| hydgrp_d1     |  D                  |
| hydgrp_d4     |  A/D, B/D, C/D, & D |


Description: These layers represent different combinations of hydrologic group classifications. This classification is defined in the Hydrologic Group ("hydgrp") column of SSURGO's Component ("component") table. A value of 1 indicates that the cell is classified as one of the hydrologic groups listed and 0 indicates another classification. The raster is meant to be run through the `zonalStatistics` process in the parent `basinCharacteristics` folder.


## Notes

- The range to run over is specified by state
- Different rasters may be created by editing the "hydroGroups" object in the script
