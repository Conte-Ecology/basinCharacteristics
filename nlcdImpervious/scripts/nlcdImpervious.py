import arcpy
from arcpy.sa import *
from arcpy import env

# -----------------
# Enter user inputs
# -----------------

# Define working directory
baseDirectory      = "C:/KPONEIL/GitHub/projects/basinCharacteristics/nlcdImpervious"

# Define catchments file
catchmentsFilePath = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/northeastHRD/NortheastHRD_AllCatchments.shp"

# Define NLCD Impervious raster
rasterFilePath = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/land/nlcd/spatial/nlcd_2006_impervious_2011_edition_2014_10_10/nlcd_2006_impervious_2011_edition_2014_10_10.img"

# Create a version ID for saving
version = "NortheastHRD"


# ---------------
# Folder creation
# ---------------

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Create version folder
versionDir = gisFilesDir + "/" + version
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, version)

# Create version database
geoDatabase = versionDir + "/workingFiles.gdb"
if not arcpy.Exists(geoDatabase): arcpy.CreateFileGDB_management(versionDir, "workingFiles.gdb")

# Create output folder
outputDir = versionDir + "/outputFiles"
if not arcpy.Exists(outputDir): arcpy.CreateFolder_management(versionDir, "outputFiles")


# --------------------------
# Prepare the boundary layer
# --------------------------

# Create regional outline
if not arcpy.Exists(geoDatabase + "/outline"):
	outline = arcpy.Dissolve_management(catchmentsFilePath, 
											geoDatabase + "/outline",
											"#", 
											"#", 
											"SINGLE_PART", 
											"DISSOLVE_LINES")
else: outline = geoDatabase + "/outline"

# Buffer outline
if not arcpy.Exists(geoDatabase + "/boundary"):
	boundary = arcpy.Buffer_analysis(outline, 
										geoDatabase + "/boundary", 
										"1 Kilometers", 
										"#", 
										"#", 
										"ALL")
else: boundary = geoDatabase + "/boundary"

# Reproject the boundary to match the NLCD raster
if not arcpy.Exists(geoDatabase + "/boundaryProj"):
	boundaryProj = arcpy.Project_management(boundary, 
											geoDatabase + "/boundaryProj", 
											rasterFilePath)
else: boundaryProj = geoDatabase + "/boundaryProj"

# ------------------
# Process the raster
# ------------------

# Trim the raster to the boundary	
if not arcpy.Exists(geoDatabase + "/extractedRaster"):
	arcpy.env.extent = rasterFilePath
	trimmedRaster = ExtractByMask(rasterFilePath, boundaryProj)
	trimmedRaster.save(geoDatabase + "/extractedRaster")
else: trimmedRaster = geoDatabase + "/extractedRaster"

# Remove cells without data
# -------------------------
# All values should be between 0 and 100. Values outside of this range indicates that the cells need to be removed. (NLCD indicates missing data in this layer with a value of 127)
outCon = Con(trimmedRaster, trimmedRaster, "", "VALUE >= 0 AND VALUE <= 100")
outCon.save(outputDir + "/impervious")