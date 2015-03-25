Impounded Area
==============

This script produces a spatial dataset of on- and off- stream network water bodies, based on the USFWS National Wetlands Inventory and NHD high resolution flowlines that have been edited by the UMass Landscape Ecology lab. This product aims to represent impounded water bodies. The categorical rasters represent the presence or absence of water bodies (as classified) with a value of 1 or 0 respectively.


## Data Sources
| Layer            | Source                                                 | Link                                                                          |
|:-----:           | ------                                                 | ----                                                                          |
| Wetlands Layer   | U.S. Fish & Wildlife National Wetlands Inventory       | http://www.fws.gov/wetlands/Data/Data-Download.html                           |
| Flowlines        | UMass Landscape Ecology Lab                            | http://www.umass.edu/landeco/research/dsl/products/dsl_products.html#settings |
| State Boundaries | National Atlas of the United States                    | http://dds.cr.usgs.gov/pub/data/nationalatlas/statesp010g.shp_nt00938.tar.gz  |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be kept in the same format as it is downloaded.

1. Open the script `impoundedArea`

2. Change the values in the "Specify inputs" section of the script
 - "baseDirectory" is the path to the `impoundedArea` folder(current parent working directory) on GitHub
 - "states" is the list of state abbreviations that identify the layers to use from the FWS data
 - "stateNames" is the list of state names to match the FWS layers used. These names should match the names in the "STATE" column of the state boundaries shapefile.
 - "wetlandsFolder" is the source folder of the wetlands datasets by state
 - "flowlinesFile" is the source file of the flowlines vector data
 - "statesFile" is the filepath to the state boundary shapefile
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. "Northeast")

3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Ensures constistency of projections
   - Creates an empty raster of the entire specified range based on the State Boundaries shapefile
   - Loops through the state polygons, intersecting them with the flowlines, and creating state rasters of the 4 categories described below
   - Mosaicks all of the state raster and the full range empty raster



## Output Rasters

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

- The layers for Maryland (MD) and the District of Columbia (DC) overlap in the FWS data, but not in the state boundary layer. DC is not included in "states" (only MD is used). In the state boundaries layer, "District of Columbia" must be specified if including Maryland.

## Possible Future Work
- Classification definitions can be changed with relatively minimal effort. 
- The data sources (wetlands and flowlines) can also be changed with a bit more work.

