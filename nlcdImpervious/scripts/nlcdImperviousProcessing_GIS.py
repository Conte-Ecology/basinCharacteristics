import arcpy
from arcpy.sa import *
from arcpy import env

# -----------------
# Enter user inputs
# -----------------

# Define working directory
baseDirectory      = "C:/KPONEIL/GitHub/projects/basinCharacteristics/nlcdImpervious"

# Define catchments file
catchmentsFilePath = "F:/KPONEIL/SourceData/streamStructure/northeastHRD/NortheastHRD_AllCatchments.shp"

# Define NLCD Impervious raster
rasterFilePath = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/land/nlcd/spatial/nlcd_2006_impervious_2011_edition_2014_10_10/nlcd_2006_impervious_2011_edition_2014_10_10.img"

# Define reclassification table
#reclassTable = baseDirectory + "/reclassTable.csv"

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
	rangeRaster = ExtractByMask(rasterFilePath, boundaryProj)
	rangeRaster.save(geoDatabase + "/extractedRaster")
else: rangeRaster = geoDatabase + "/extractedRaster"

# Get spatial references
catchSpatialRef  = arcpy.Describe(catchmentsFilePath).spatialReference.name
rasterSpatialRef = arcpy.Describe(rangeRaster).spatialreference.name

# Reproject if necessary
if not arcpy.Exists(geoDatabase + "/rangeRasterPrj"):
	if rasterSpatialRef != catchSpatialRef:	
		projectedRaster = arcpy.ProjectRaster_management(rangeRaster, 
															geoDatabase + "/rangeRasterPrj",
															catchmentsFilePath)
	else: projectedRaster = rangeRaster
else: projectedRaster = geoDatabase + "/rangeRasterPrj"

# Remove cells without data
# -------------------------
# Count number of unique values
uniqueValues = arcpy.GetRasterProperties_management(projectedRaster, "UNIQUEVALUECOUNT")

# All values should be between 0 and 100. Values outside of this range indicates that the cells need to be removed. (NLCD indicates missing data with a value of 127)

outCon = Con(projectedRaster, projectedRaster, "", "VALUE >= 0 AND VALUE <= 100")


outCon.save(outputDir + "/impervious")
