Topography
==========

This script produces rasters representing the elevation and slope of the landscape.


## Data Sources
|    Layer   | Source                                                             | Link                      |
|   :-----:  | ------                                                             | ----                      |
|     DEM    | National Elevation Dataset (Edited by UMass Landscape Ecology Lab) | http://nationalmap.gov/   |


## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. 

1. Open the script `topography.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the `\topography` folder
 - `demFilePath` is the file path to the raw DEM
 - `version` is the name that will be associated with this particular run of the tool (e.g. "NortheastHRD" for all High Resolution Catchments)

3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Calculates the slope raster from the DEM
   - Copies & renames the DEM to the `basinCharacteristics` repo
   - Saves the completed rasters to the `topography\gisFiles\Northeast\outputFiles` directory

## Output Rasters

#### Digital Elevation Model
Raster name: dem <br>
Description: This layer represents the elevation (meters) of the landscape. No editing is done to this layer, it is copied as is into the proper folder

#### Slope Raster
Raster name: slope_pcnt <br>
Description: This layer represents the slope (percent rise) of the landscape.

## Possible Future Work
- Additional topographical layers such as slope aspect can be produced