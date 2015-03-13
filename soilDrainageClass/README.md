Soil Drainage Class
===================


# IN PROGRESS....



This script produces a spatial dataset of geology that is categorized as "surficial coarseness", based on the Soil Survey Geographic Database (SSURGO).


## Data Sources
| Layer   | Source                                                | Link                                                           |
|:-----:  | ------                                                | ----                                                           |
| SSURGO  | USDA-NRCS (download through Geospatial Data Gateway)  | http://datagateway.nrcs.usda.gov/GDGOrder.aspx?order=QuickState    Select: "2014 Gridded Soil Survey Geographic (gSSURGO) by State or Conterminous U.S."|

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be kept in the same format as it is downloaded.

1. Download the data by state and unzip the `soils\gssurgo_g_[state abbreviation].zip` sub-folder into the `soilsFolder`

Open the script `soils_surficialCoarseness`

2. Change the values in the "Specify inputs" section of the script
 - "baseDirectory" is the path to the `surficialCoarseness` folder (current parent working directory)
 - "states" is the list of state abbreviations included in the desired range
 - "soilsFolder" is the source folder of the wetlands datasets by state
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. "Northeast")

3. Run the script in ArcPython. It does the following:
   - Sets up the folder structure in the specified directory
   - Creates an empty raster of the entire specified range
   - Merges the necessary data tables in order to connect spatial data to necessary soil classification
   - Loops through the state polygons, creating state rasters of the surficial coarseness category
   - Mosaicks all of the state raster and the full range empty raster



## Output Rasters

Raster name: surfCoarse <br>


Description: This layer represents the soil parent material that is described as "surficially coarse". This classification is defined as a soil whose parent material texture is made up of sand, gravel, or a combination of the two. (In SSURGO's "Component Parent Material" table ("copm") the column "Textureal Modifier" ("pmmodifier") = "Sandy", "Sandy and gravelly", or "Gravelly"). A value of 1 indicates the cell is classified as surficial coarseness and 0 indicates not. The raster is meant to be run through the `zonalStatistics` process in the parent `basinCharacteristics` folder.


## Notes

- The range to run over is specified by state
