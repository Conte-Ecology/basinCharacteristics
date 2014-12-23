import arcpy
from arcpy.sa import *
from arcpy import env

catchmentsFile = "F:/KPONEIL/SourceData/streamStructure/northeastHRD/NENYHRD_AllCatchments.shp"

# -----------------
# Enter user inputs
# -----------------

# Define directories
baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/nlcdLandCover"
catchmentsFolder = "F:/KPONEIL/SourceData/streamStructure/northeastHRD"
rasterFolder = "F:/KPONEIL/SourceData/landCover/nlcd/raw/nlcd_2006_landcover_2011_edition_2014_03_31"

outRasterFolder = "C:/KPONEIL/GitHub/projects/basinCharacteristics/nlcdLandCover/gisFiles"

# Name of catchments file
catchmentsFileName = "NortheastHRD_AllCatchments.shp"
rasterFileName = "nlcd_2006_landcover_2011_edition_2014_03_31.img"



# Create a version ID for saving
version = "NortheastHRD"

# Do you want to keep the intermediate GIS files ( "YES" or "NO" ) 
keepFiles = "YES"

#      ***** DO NOT CHANGE SCRIPT BELOW THIS POINT ****

# ---------------
# Folder creation
# ---------------

# Defines the path to the catchments file
catchmentsFilePath = catchmentsFolder + "/" + catchmentsFileName
rasterFilePath = rasterFolder + "/" + rasterFileName

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Create version folder
versionDir = gisFilesDir + "/" + version
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, version)

# Create version database
geoDatabase = versionDir + "/workingFiles.gdb"
if not arcpy.Exists(geoDatabase): arcpy.CreateFileGDB_management(versionDir, "workingFiles.gdb")

# Create tables folder
tablesDir = versionDir + "/tables"
if not arcpy.Exists(tablesDir): arcpy.CreateFolder_management(versionDir, "tables")



# Define the projection to use (that of the wetlands)
projection_definition = catchmentsFilePath

# Name the spatial reference of the catchment
catchSpatialRef = arcpy.Describe( catchmentsFilePath ).spatialReference.name

# Set directory
arcpy.env.workspace = geoDatabase


reclassTable = "F:/KPONEIL/SourceData/landCover/nlcd/reclassTableNLCD.csv"

fieldList = arcpy.ListFields(reclassTable)


fieldCount = range(2, len(fieldList))




for category in fieldList

category = fieldList[2]




recRaster = ReclassByTable(rasterFilePath, reclassTable,"Value","Value", str(category.name), "NODATA")


recRaster.save(outRasterFolder + "/" + category)



