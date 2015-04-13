basinCharacteristics
====================

# Outline notes

1. What this project is and what it does
2. small code example
3. required libraries, functions, packages, etc. (installation)
4. contact info


Contains the scripts, procedures and some of the ouputs for the basin characteristics generated in the models and maps. Currently the dataset is based on the NHDplus medium res delineation.

## fwsWetlands
Creates the raster layers that describe the presence of wetlands.

## impoundedArea
Creates the raster layers that describe the presence of "impounded" waterbodies.

## impoundments
Calculates the distance, surface area, and contributing drainage area to each waterbody on the stream network.

## surficialCoarseness
Creates the raster layer indicating the surficial geology that is described as coarse.

## zonalStatistics

Calcuates spatial averages of the raster layers across a specified shapefile containing catchment polygons.