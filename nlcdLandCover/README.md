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
 - "reclassTable" is the file path to the table used to reclassify the raw raster into individual categorical rasters. Example:
 
| Class                        | Value  |	forest | developed | devel_opn |
| -----                        | -----  | ------ | --------- | --------- |
| Open Water                   |	11    |	0      | 0         | 0         |
| Perennial Ice/Snow           |	12    |	0	     | 0         | 0         |
| Developed, Open Space        |	21    |	0      | 1         | 1         |
| Developed, Low Intensity     |	22    |	0      | 1         | 0         |
| Developed, Medium Intensity  |	23    |	0      | 1         | 0         |
| Developed, High Intensity    |	24    |	0      | 1         | 0         |
| Barren Land (Rock/Sand/Clay) |	31    |	0      | 0         | 0         |
 
 - "version" is the name that will be associated with this particular run of the tool (e.g. `NortheastHRD` for all High Resolution Catchments)
 - "keepFiles" specifies whether or not to keep the intermediate GIS files. Enter "NO" to delete or "YES" to keep.
 
3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Generates the processing boundary from the specified shapefile.
   - Creates the individual categorical rasters based on the reclassification table. These rasters are in the same projection as the shapefile used to determine the processing boundary.


## Output Rasters

The number of rasters generated by this script will be equal to the number of columns (beyond the first 2) specified in the reclassification table. The rasters will receive the same name as the column name (keep column names to a maximum of 13 characters). Each output raster will be categorical, describing the classification which it is defined by with a value of 1 for present in that cell or 0 for absent.

## Notes

- Typically, the "catchmentsFilePath" variable specifies a shapefile of hydrologic catchments defining the range over which the "Zonal Statistics" tool will be applied. It is possible to enter another polygon shapefile, such as state or town boundaries, as this variable. The primary purpose of this file is to trim the original raster, which represents the continental US, to a manageable size.

## Possible Future Work
- Classification definitions can be changed by editing the "reclassTable" CSV file.