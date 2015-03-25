Hydrologic Unit Code
====================

This script maps catchments to Hyrdologic Unit Codes as defined in the Watershed Boundary Dataset.


## Data Sources
| Layer                 | Source                                | Link                        |
|:-----:                | ------                                | ----                        |
| HUC Outline Polygons  | USGS Watershed Boundary Dataset       | http://nhd.usgs.gov/wbd.html|

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be kept in the same format as it is downloaded.

1. Open the script `matchHUCsWithCatchments`

2. Change the values in the "Specify inputs" section of the script
 - "baseDirectory" is the path to the `hucs` folder (current parent working directory)
 - "catchmentsFolder" is the source folder of the catchments shapefile
 - "hucFilesDir" is the source foler of the HUC shapefiles
 - "catchmentsFileName" is the name of the catchments shapefile with extention
 - "hucs" is a list of the HUC levels to process
 - "version" is the ID used to differentiate runs
 - "keepFiles" - A "YES" or "NO" option specifies whether or not to delete the intermediate files
 
3. Run the script in ArcPython. It does the following:
   - Calculates the centroids of the catchments
   - Spatially maps the catchment centroids to the HUC polygons
   - Determines which centroids do not fall within the HUC outlines
   - Calculates the nearest HUC for the missed centroids
   - Outputs the results as a separate `.dbf` file for each HUC level


## Output Tables

One `.dbf` table is created for every HUC level processed. The file contains a column for catchment IDs that is linked to relevant HUC information. The table may be further processed in R to select relevant columns.