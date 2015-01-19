Impounded Area
==============

This script produces the categorical rasters for specified land use types based on the National Land Cover Dataset.


## Data Sources
| Layer           | Source                      | Link                    |
|:-----:          | ------                      | ----                    |
| Land Use Raster | National Land Cover Dataset | http://www.mrlc.gov/    |
| Catchments      | Conte Ecology Group         | NA                      |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be unzipped, but otherwise kept in the same format as it is downloaded.

1. Open the script `nlcdLandCoverProcessing_GIS`

2. Change the values in the "Specify inputs" section of the script
 - "baseDirectory" is the path to the `nlcdLandCover` folder
 - "catchmentsFilePath" is the file path to the catchments polygons shapefile. (See "Notes" section")
 - "rasterFilePath" is the file path to the raw NLCD Land Use raster (.img format)
 - "reclassTable " is the file path to the table used to reclassify the raw raster into individual categorical rasters. Example:
 - "version" is the name that will be associated with this particular run of the tool (e.g. `NortheastHRD` for all High Resolution Catchments)
 - "keepFiles" specifies whether or not to keep the intermediate GIS files. Enter "NO" to delete or "YES" to keep.
 
3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Generates the processing boundary from the specified shapefile.
   - Creates the individual categorical rasters based on the reclassification table. These rasters are in the same projection as the shapefile used to determine the processing boundary.

## IN PROGRESS: Below this point is a copy from a different readme.



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

