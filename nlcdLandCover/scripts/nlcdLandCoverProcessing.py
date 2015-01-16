import arcpy
from arcpy.sa import *
from arcpy import env

# -----------------
# Enter user inputs
# -----------------

# Define working directory
baseDirectory      = "C:/KPONEIL/GitHub/projects/basinCharacteristics/nlcdLandCover"

# Define catchments file
catchmentsFilePath = "F:/KPONEIL/SourceData/streamStructure/northeastHRD/NortheastHRD_AllCatchments.shp"

# Define NLCD Land Use raster
rasterFilePath = "F:/KPONEIL/SourceData/landCover/nlcd/raw/nlcd_2006_landcover_2011_edition_2014_03_31/nlcd_2006_landcover_2011_edition_2014_03_31.img"

# Define reclassification table
reclassTable = "C:/KPONEIL/GitHub/projects/basinCharacteristics/nlcdLandCover/reclassTable.csv"

# Create a version ID for saving
version = "NortheastHRD"

# Do you want to keep the intermediate processing files ( "YES" or "NO" )
keepFiles = "YES"

#      ***** DO NOT CHANGE SCRIPT BELOW THIS POINT ****

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


# -----------------------------------	
# Prepare raster for reclassification
# -----------------------------------

# Create regional outline
outline = arcpy.Dissolve_management(catchmentsFilePath, 
										geoDatabase + "/outline",
										"#", 
										"#", 
										"SINGLE_PART", 
										"DISSOLVE_LINES")

# Buffer outline
boundary = arcpy.Buffer_analysis(outline, 
									geoDatabase + "/boundary", 
									"1 Kilometers", 
									"#", 
									"#", 
									"ALL")

# Reproject the boundary to match the NLCD raster
boundaryProj = arcpy.Project_management(boundary, 
										geoDatabase + "/boundaryProj", 
										rasterFilePath)

# Trim the raster to the boundary	
arcpy.env.extent = rasterFilePath
rangeRaster = ExtractByMask(rasterFilePath, boundaryProj)	

# Get spatial references
catchSpatialRef  = arcpy.Describe(catchmentsFilePath).spatialReference.name
rasterSpatialRef = arcpy.Describe(rasterFilePath).spatialreference.name

# Reproject if necessary
if rasterSpatialRef != catchSpatialRef:	
	projectedRaster = arcpy.ProjectRaster_management(rangeRaster, 
														geoDatabase + "/rangeRasterPrj",
														catchmentsFilePath)
else: projectedRaster = rangeRaster


# -------------------------
# Create individual rasters
# -------------------------

# Set directory
arcpy.env.workspace = geoDatabase

# List of column names
fieldList = arcpy.ListFields(reclassTable)

# Category position and count
fieldCount = range(2, len(fieldList))

# Loop through categories and reclassify raster
for i in fieldCount:

	# Category name
	category = fieldList[i]

	# Reclassify the raster according to the table provided
	recRaster = ReclassByTable(projectedRaster, 
								reclassTable,
								"Value",
								"Value", 
								str(category.name), 
								"NODATA")

	# Save the new raster
	recRaster.save(outputDir + "/" + str(category.name))

	# Delete the temporary object
	del(recRaster)

# If specified, delete processing files
if keepFiles == "NO":
	arcpy.Delete_management(geoDatabase)
	
	
	
	
	
	
	
	
	
	
	

