Impounded Area
==============

This script produces a spatial dataset of on- and off- stream network water bodies, based on the USFWS National Wetlands Inventory and NHD high resolution flowlines that have been edited by the UMass Landscape Ecology lab. This product aims to represent impounded water bodies. 


## Data Sources
| Layer           | Source                                                 | Link                                                                         |
|:-----:          | ------                                                 | ----                                                                         |
| Wetlands Layer  | U.S. Fish & Wildlife National Wetlands Inventory       | http://www.fws.gov/wetlands/Data/Data-Download.html                          |
| Flowlines       | UMass Landscape Ecology Lab                            | http://www.umass.edu/landeco/research/dsl/products/dsl_products.html#settings|

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be kept in the same format as it is downloaded.

1. Open the script `impoundedAreaProcessing_GIS`

2. Change the values in the "Specify inputs" section of the script
 - "baseDirectory" is the path to the `impoundedArea` folder
 - The order of states in the "states" and "stateNames" variables should match. These should be checked against actual file names (see note on Vermont layers)
 - "wetlandsFolder" is the source folder of the wetlands datasets by state
 - "flowlinesFile" is the source file of the flowlines vector data
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. "Northeast")

 
3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Creates an empty raster of the entire specified range
   - Loops through the state polygons, intersecting them with the flowlines, and creating state rasters of the 4 categories described below
   - Mosaicks all of the state raster and the full range empty raster



## Output Rasters

In total four rasters in total are produced. A cell value of 1 indicates a waterbody and 0 indicates not. These rasters are meant to be run through the `zonalStatistics` process in the parent `basinCharacteristics` folder.

#### Open Water On Stream Network
Raster name: openOnNet <br>
Description: This layer represents the FWS wetlands defined as "open water" (where "WETLAND_TYPE" = "Freshwater Pond" or "Lake") that intersect the stream network.

#### Open Water Off Stream Network
Raster name: openOffNet <br>
Description: This layer represents the FWS wetlands defined as "open water" (where "WETLAND_TYPE" = "Freshwater Pond" or "Lake") that are not intersected by the stream network.

#### All Water Bodies On Stream Network
Raster name: allOnNet <br>
Description: This layer represents the FWS wetlands defined as "all water bodies" (where "WETLAND_TYPE" = "Freshwater Emergent Wetland", "Freshwater Forested/Shrub Wetland", "Freshwater Pond", "Lake", or "Other") that intersect the stream network.

#### All Water Bodies Off Stream Network
Raster name: allOffNet <br>
Description: This layer represents the FWS wetlands defined as "all water bodies" (where "WETLAND_TYPE" = "Freshwater Emergent Wetland", "Freshwater Forested/Shrub Wetland", "Freshwater Pond", "Lake", or "Other") that are not intersected by the stream network.

## Notes

- The stream network is defined as the high resolution flowlines as well as the "Riverine" classification polygons of the FWS wetlands layer.

- The range to run over is specified by state

- There is an inconsistency in the VT Wetlands layers. While all of the other state boundary polygons are named by the full state name, the Vermont state outline is abbreviated. This is reflected in the default names list. File names should be checked when adding new states.

- The layers for Maryland (MD) and the District of Columbia (DC) overlap. DC is not included and only MD is used.

## Possible Future Work
- Classification definitions can be changed with relatively minimal effort. 
- The data sources (wetlands and flowlines) can also be changed with a bit more work.

