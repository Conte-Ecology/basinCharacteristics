Wetland & Open Water Area
=========================

This script produces a spatial dataset "Open Water" and "Wetland" land coverage, based on the USFWS National Wetlands Inventory.


## Data Sources
| Layer            | Source                                                 | Link                                                                         |
|:-----:           | ------                                                 | ----                                                                         |
| Wetlands Layer   | U.S. Fish & Wildlife National Wetlands Inventory       | http://www.fws.gov/wetlands/Data/Data-Download.html                          |
| State Boundaries | National Atlas of the United States                    | http://dds.cr.usgs.gov/pub/data/nationalatlas/statesp010g.shp_nt00938.tar.gz |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be kept in the same format as it is downloaded (unzip the state boundaries layer)

1. Open the script `fwsWetlandsProcessing_GIS`

2. Change the values in the "Specify inputs" section of the script
 - "baseDirectory" is the path to the `fwsWetlands` folder (current parent working directory) on GitHub
 - "states" is the list of state abbreviations that identify the layers to use from the FWS data
 - "stateNames" is the list of state names to match the FWS layers used. These names should match the names in the "STATE" column of the state boundaries shapefile.
 - "wetlandsFolder" is the source folder of the wetlands datasets by state
 - "statesFile" is the filepath to the state boundary shapefile
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. "Northeast")
 
3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Ensures constistency of projections
   - Creates an empty raster of the entire specified range based on the State Boundaries shapefile
   - Loops through the state polygons, creating state rasters of the categories described below
   - Mosaicks all of the state raster and the full range empty raster


## Output Rasters

In total two rasters are produced. A cell value of 1 indicates a waterbody and 0 indicates not. These rasters are meant to be run through the `zonalStatistics` process in the parent `basinCharacteristics` folder.

#### Open Water 
Raster name: fwsOpenWater <br>
Description: This layer represents the FWS wetlands defined as "open water" (where "WETLAND_TYPE" = "Freshwater Pond", "Lake", or "Estuarine and Marine Deepwater").

#### Wetlands
Raster name: fwsWetlands <br>
Description: This layer represents the FWS wetlands defined as "open water" (where "WETLAND_TYPE" = "Estuarine and Marine Wetland", "Freshwater Emergent Wetland", or "Freshwater Forested/Shrub Wetland").


## Notes

- The states included specify the final ranger

- The layers for Maryland (MD) and the District of Columbia (DC) overlap in the FWS data, but not in the state boundary layer. DC is not included in "states" (only MD is used). In the state boundaries layer, "District of Columbia" must be specified if including Maryland.

## Possible Future Work
- Classification definitions can be changed with relatively minimal effort. 
