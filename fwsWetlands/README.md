Wetland & Open Water Area
=========================

This script produces a spatial dataset "Open Water" and "Wetland" land coverage, based on the USFWS National Wetlands Inventory.


## Data Sources
| Layer           | Source                                                 | Link                                               |
|:-----:          | ------                                                 | ----                                               |
| Wetlands Layer  | U.S. Fish & Wildlife National Wetlands Inventory       | http://www.fws.gov/wetlands/Data/Data-Download.html|

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be kept in the same format as it is downloaded.

1. Open the script `fwsWetlandsProcessing_GIS`

2. Change the values in the "Specify inputs" section of the script
 - "baseDirectory" is the path to the `fwsWetlands` folder (current parent working directory)
 - The order of states in the "states" and "stateNames" variables should match. These should be checked against actual file names (see note on Vermont layers)
 - "wetlandsFolder" is the source folder of the wetlands datasets by state
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. "Northeast")

 
3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Creates an empty raster of the entire specified range
   - Loops through the state polygons, creating state rasters of the categories described below
   - Mosaicks all of the state raster and the full range empty raster



## Output Rasters

In total two rasters in total are produced. A cell value of 1 indicates a waterbody and 0 indicates not. These rasters are meant to be run through the `zonalStatistics` process in the parent `basinCharacteristics` folder.

#### Open Water 
Raster name: fwsOpenWater <br>
Description: This layer represents the FWS wetlands defined as "open water" (where "WETLAND_TYPE" = "Freshwater Pond", "Lake", or "Estuarine and Marine Deepwater").

#### Wetlands
Raster name: fwsWetlands <br>
Description: This layer represents the FWS wetlands defined as "open water" (where "WETLAND_TYPE" = "Estuarine and Marine Wetland", "Freshwater Emergent Wetland", or "Freshwater Forested/Shrub Wetland").


## Notes

- The range to run over is specified by state

- There is an inconsistency in the VT Wetlands layers. While all of the other state boundary polygons are named by the full state name, the Vermont state outline is abbreviated. This is reflected in the default names list. File names should be checked when adding new states.

## Possible Future Work
- Classification definitions can be changed with relatively minimal effort. 
