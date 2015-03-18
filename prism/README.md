PRISM Climate Data
==================

IN PROGRESS...

This script produces impervious surface raster based on the National Land Cover Dataset.


## Data Sources
| Layer           | Source                      | Link                    |
|:-----:          | ------                      | ----                    |
| Land Use Raster | National Land Cover Dataset | http://www.mrlc.gov/    |
| Catchments      | Conte Ecology Group         | NA                      |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be unzipped, but otherwise kept in the same format as it is downloaded.

1. Open the script `nlcdImperviousProcessing_GIS`

2. Change the values in the "Specify inputs" section of the script
 - "baseDirectory" is the path to the `nlcdLandCover` folder
 - "catchmentsFilePath" is the file path to the catchments polygons shapefile. (See "Notes" section")
 - "rasterFilePath" is the file path to the raw NLCD Land Use raster (.img format)
 - "version" is the name that will be associated with this particular run of the tool (e.g. `NortheastHRD` for all High Resolution Catchments)

3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Generates the processing boundary from the specified shapefile and clips the source raster to this range
   - Trims the raw raster to the boundary and removes the missing data. (The result in the same projection as the shapefile used to determine the processing boundary)


## Output Rasters

One raster named "impervious".

## Notes

- Typically, the "catchmentsFilePath" variable specifies a shapefile of hydrologic catchments defining the range over which the "Zonal Statistics" tool will be applied. It is possible to enter another polygon shapefile, such as state or town boundaries, as this variable. The primary purpose of this file is to trim the original raster, which represents the continental US, to a manageable size.

## Possible Future Work
