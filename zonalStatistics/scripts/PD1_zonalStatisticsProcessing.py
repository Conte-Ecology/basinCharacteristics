#Import System Modules:
import arcpy
from arcpy import env
from arcpy.sa import *


# ======================
# Specify Base Directory
# ======================
baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics"

# =================
# Enter user inputs
# =================
# What name to use to specify the run
outputName = "pointDelineation"

# Catchments file path
catchmentsFilePath =  "C:/KPONEIL/delineation/northeast/pointDelineation/outputFiles/delin_basins_deerfield_2_17_2015.shp"

# Field name defining the zones
zoneField = "DelinID"

# Stat to calculate
statType = "MEAN"

# Raster Directory
rasterDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/gisFiles/versions/NortheastHRD/projectedRasters.gdb"

# Raster names
rasterList = ["forest", "agriculture", "impervious", "fwswetlands", "fwsopenwater", "slope_pcnt", "elevation", "surfcoarse", "percent_sandy", "drainageclass", "hydrogroup_ab"] 

# =============
# Install Tools
# =============
# Import the supplemental tools (downloaded from here: http://blogs.esri.com/esri/arcgis/2013/11/26/new-spatial-analyst-supplemental-tools-v1-3/#comment-7007)
arcpy.ImportToolbox("C:/KPONEIL/tools/ArcGIS/SpatialAnalystSupplementalTools/Spatial Analyst Supplemental Tools.pyt")


# ===========
# Folder prep
# ===========
# Check if folders exist, create them if they don't

# Parent directories
# ------------------
# Main versions directory
version_directory = baseDirectory + "/versions"
if not arcpy.Exists(version_directory): arcpy.CreateFolder_management(baseDirectory, "versions")

# Main gisFiles directory
gisFiles_directory = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFiles_directory): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# GIS files versions directory
gisVersion_directory = gisFiles_directory + "/versions"
if not arcpy.Exists(gisVersion_directory): arcpy.CreateFolder_management(gisFiles_directory, "versions")


#  Run-specific folders
# ---------------------
# Run-specific gisFiles directory
working_directory = gisVersion_directory + "/" + outputName
if not arcpy.Exists(working_directory): arcpy.CreateFolder_management(gisVersion_directory, outputName)

# Set the run database. Create one if it doesn't exist.
working_db = working_directory + "/processingFiles.gdb"
if not arcpy.Exists(working_db): arcpy.CreateFileGDB_management (working_directory, "processingFiles", "CURRENT")

# Run-specific output folder.
outputVersion_directory = version_directory + "/" + outputName
if not arcpy.Exists(outputVersion_directory): arcpy.CreateFolder_management(version_directory, outputName)

# Run-specific GIS tables.
gisTables_directory = outputVersion_directory + "/gisTables"
if not arcpy.Exists(gisTables_directory): arcpy.CreateFolder_management(outputVersion_directory, "gisTables")

# Run-specific R tables.
rTables_directory = outputVersion_directory + "/rTables"
if not arcpy.Exists(rTables_directory): arcpy.CreateFolder_management(outputVersion_directory, "rTables")

# Run-specific completed statistics.
completedStats_directory = outputVersion_directory + "/completedStats"
if not arcpy.Exists(completedStats_directory): arcpy.CreateFolder_management(outputVersion_directory, "completedStats")


# ==========
# Add layers
# ==========
# Define map
mxd = arcpy.mapping.MapDocument("CURRENT")
# Define dataframe
df = arcpy.mapping.ListDataFrames(mxd)[0]

# Add the catchments layer to the map
addLayer = arcpy.mapping.Layer(catchmentsFilePath)
arcpy.mapping.AddLayer(df, addLayer, "AUTO_ARRANGE")


# ========================
# Project catchments layer
# ========================

rasterDescribe = arcpy.Describe(rasterDirectory + "/" + rasterList[0])
rasterSR = rasterDescribe.SpatialReference
rasterSRName = rasterSR.Name

polyDescribe = arcpy.Describe(catchmentsFilePath)
polySR = polyDescribe.SpatialReference
polySRName = polySR.Name

# Check if projections are the same
if not polySRName == rasterSRName:

	if not arcpy.Exists(working_db + "/catchmentsProj"):
		# Project polygon to raster projection
		zoneObject = arcpy.Project_management(catchmentsFilePath, 
													working_db + "/catchmentsProj", 
													rasterDirectory + "/" + rasterList[0])
else: zoneObject = catchmentsFilePath


# Add attribute index to increase performance
arcpy.AddIndex_management(zoneObject, zoneField, "zStatInd", "UNIQUE", "NON_ASCENDING")

# ====================
# Run Zonal Statistics
# ====================
for raster in rasterList:
		
	# Name of output table
	outTable = gisTables_directory + "/" + raster + ".dbf"
		
	arcpy.ZonalStatisticsAsTable02_sas(zoneObject,
										zoneField,
										rasterDirectory + "/" + raster,
										outTable,
										statType,
										"DATA")	
											
	# Check for missing catchments. If some catchments are missing from the output table, then run the script to fill these in.
	cat = arcpy.GetCount_management(zoneObject) 
	catRows = int(cat.getOutput(0))
	tab = arcpy.GetCount_management(outTable)
	tabRows = int(tab.getOutput(0))

	# Might want to write this as a function
	if tabRows < catRows:

		arcpy.MakeFeatureLayer_management(zoneObject, "zoneObject_Lyr")
	
		# Calculate catchments with missing data
		# --------------------------------------
		# Join the output file to the catchments file
		attributeJoin = arcpy.AddJoin_management ("zoneObject_Lyr", 
													zoneField, 
													outTable, 
													zoneField)
		
		# Define the query
		qry = raster + "."  + zoneField + ' IS NULL'
		
		# Export the missing features as a new table
		missingVals = arcpy.TableToTable_conversion("zoneObject_Lyr",
													gisTables_directory,
													raster + "_" + "MissingValues.dbf",
													qry)
		
		# Delete the temporary feature layer
		arcpy.Delete_management("zoneObject_Lyr")		
		
		# Add a new field for the table to match the zonal statistics output table
		arcpy.AddField_management(missingVals, "AREA", "DOUBLE")
		arcpy.AddField_management(missingVals, statType, "DOUBLE")

		arcpy.CalculateField_management (missingVals, "AREA", 0, "PYTHON_9.3")
		arcpy.CalculateField_management (missingVals, statType, -9999, "PYTHON_9.3")							

		# Append the missing values to the existing table
		arcpy.Append_management(missingVals,
									outTable,
									"NO_TEST")