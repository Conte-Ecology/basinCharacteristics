#Import System Modules:
import arcpy
from arcpy import env
from arcpy.sa import *

# ===========
# Description
# ===========
# This script uses the previously generated overlapping riparian buffer files to calculate zonal statistics for specified rasters. These rasters have already been projected and resampled to the same spatial reference and cell size.

# It is strongly suggested that this script is run in ArcPy with background processing turned off. With background processing enabled, errors tend to occur (e.g. "background server threw an exception" or "RuntimeLocalServer.exe crashed").
# This may a result of running larger zone objects in the ZonalStatisticsAsTable2 tool. Sectioning the buffer polyogns into smaller sections (HUC8 or 12) may be done in future versions.

# ======================
# Specify Base Directory
# ======================
baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics"


# =========================
# Read use specified inputs
# =========================

# Open file with input parameters
with open (baseDirectory + "/scripts/RB_INPUTS.txt", "r") as myfile:
    lines = myfile.readlines()

outputName          = lines[1] .replace('outputName', '')         .replace('=', '').replace('\n','').replace('"','').replace(' ','')
catchmentsFilePath  = lines[4] .replace('catchmentsFilePath' , '').replace('=', '').replace('\n','').replace('"','').replace(' ','')
bufferID            = lines[7] .replace('bufferID', '')         .replace('=', '').replace('\n','').replace('"','').replace(' ','')
zoneField           = lines[10] .replace('zoneField' , '')        .replace('=', '').replace('\n','').replace('"','').replace(' ','')
statType            = lines[13].replace('statType' , '')          .replace('=', '').replace('\n','').replace('"','').replace(' ','')
rasterList          = lines[16].replace('rasterList', '')    .replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').split(",")
hucFilePath         = lines[19] .replace('hucFilePath' , '')       .replace('=', '').replace('\n','').replace('"','').replace(' ','')
rasterDirectory     = lines[22] .replace('rasterDirectory' , '')       .replace('=', '').replace('\n','').replace('"','').replace(' ','')

# =============
# Install Tools
# =============
# Import the "ZonalStatisticsAsTable02" from the supplemental tools (downloaded from here: http://blogs.esri.com/esri/arcgis/2013/11/26/new-spatial-analyst-supplemental-tools-v1-3/#comment-7007)
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

# Set the run database. Create one if it doesn't exist.
working_tables = working_directory + "/processingTables"
if not arcpy.Exists(working_tables): arcpy.CreateFolder_management(working_directory, "processingTables")

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


# ===============
# Map Definitions
# ===============
# Define map
mxd = arcpy.mapping.MapDocument("CURRENT")
# Define dataframe
df = arcpy.mapping.ListDataFrames(mxd)[0]


# ================
# Define Functions
# ================
# Unique Values function	
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


# ==========
# Add layers
# ==========
# Add the catchments layer to the map
addLayer = arcpy.mapping.Layer(catchmentsFilePath)
arcpy.mapping.AddLayer(df, addLayer, "AUTO_ARRANGE")


# ========================
# Project catchments layer
# ========================
# Raster spatial reference
rasterDescribe = arcpy.Describe(rasterDirectory + "/" + rasterList[0])
rasterSR = rasterDescribe.SpatialReference
rasterSRName = rasterSR.Name

# Buffer polygon spatial reference
polyDescribe = arcpy.Describe(catchmentsFilePath)
polySR = polyDescribe.SpatialReference
polySRName = polySR.Name

# Check if projected version exists from a previous run
if not arcpy.Exists(working_db + "/catchmentsProj_" + bufferID ):

	# Compare spatial references
	if not polySRName == rasterSRName:
		
		# Project catchments
		zoneObject = arcpy.Project_management(catchmentsFilePath, 
													working_db + "/catchmentsProj_" + bufferID, 
													rasterDirectory + "/" + rasterList[0])				
	else: zoneObject = catchmentsFilePath												
												
	# Add attribute index to increase performance
	arcpy.AddIndex_management(zoneObject, zoneField, "zStatInd", "UNIQUE", "NON_ASCENDING")										
else: zoneObject = working_db + "/catchmentsProj_" + bufferID

# Count the rows (for adding missing features later)
cat = arcpy.GetCount_management(zoneObject)
catRows = int(cat.getOutput(0))

# Make the zone object a feature layer
arcpy.MakeFeatureLayer_management(zoneObject, "zoneObject_Lyr")


# ==================
# Project hucs layer
# ==================
# Raster spatial reference
rasterDescribe = arcpy.Describe(rasterDirectory + "/" + rasterList[0])
rasterSR = rasterDescribe.SpatialReference
rasterSRName = rasterSR.Name

# HUC polygon spatial reference
hucsDescribe = arcpy.Describe(hucFilePath)
hucsSR = hucsDescribe.SpatialReference
hucsSRName = hucsSR.Name

# Check if projected version exists from a previous run
if not arcpy.Exists(working_db + "/hucsProj"):

	# Compare spatial references
	if not hucsSRName == rasterSRName:

		# Project HUCs
		hucsObject = arcpy.Project_management(hucFilePath, 
												working_db + "/hucsProj", 
												rasterDirectory + "/" + rasterList[0])
	else: hucsObject = hucFilePath
else: hucsObject = working_db + "/hucsProj"

# Make the hucsObject a feature layer
arcpy.MakeFeatureLayer_management(hucsObject, "hucsObject_Lyr")


# ================
# List HUCs to use
# ================
# Create list
hucList = []
fcSearch = arcpy.SearchCursor(hucsObject, "", "", "HUC6")
for fcRow in fcSearch:
	
	# Get HUC number
	hucNum = str(fcRow.getValue("HUC6"))
	
	# Append HUC to list
	hucList.append(hucNum)


# ====================
# Run Zonal Statistics
# ====================
# Loop through HUCs to section 
for huc in hucList:

	# Define the current section buffer filepath
	bufferFile = working_db + "/buffers_HUC_" + huc + "_" + bufferID

	# Check if the file exists from the previous run
	if not arcpy.Exists(bufferFile):

		# Select the HUC boundary for selecting buffer polygons
		hucSelection = arcpy.SelectLayerByAttribute_management("hucsObject_Lyr", "NEW_SELECTION", '"HUC6" = ' + "'" + huc + "'")

		# Select the buffer polygons that are within the HUC boundary (including those on the edge)
		zoneSelection = arcpy.SelectLayerByLocation_management("zoneObject_Lyr", "INTERSECT", hucSelection, "#", "NEW_SELECTION")

		# Export the selection as a separate file
		selectHUC =  arcpy.FeatureClassToFeatureClass_conversion(zoneSelection,
																	working_db,
																	"buffers_HUC_" + huc + "_" + bufferID)
	else: selectHUC = bufferFile
																	
	# If no buffers fall into the HUC, then skip the zonal statistics
	table = arcpy.GetCount_management(selectHUC) 
	tableRows = int(table.getOutput(0))
	
	if tableRows > 0:
		# Loop through all rasters
		for raster in rasterList:
				
			# Name of output table
			outTable = working_tables + "/" + raster + "_HUC" + huc + "_" + bufferID + ".dbf"
			
			# Only run if the output doesn't exist
			if not arcpy.Exists(outTable):	
				# Run overlapping zonal statistics tool
				arcpy.ZonalStatisticsAsTable02_sas(selectHUC,
												zoneField,
												rasterDirectory + "/" + raster,
												outTable,
												statType,
												"DATA")	
			else: print("Output table already exists for " + raster)

	# Check if the buffer layer section is in the dataframe. If yes, then remove it.
	lyr = arcpy.mapping.Layer(bufferFile)	
	if lyr in arcpy.mapping.ListLayers(mxd, "", df):
		arcpy.mapping.RemoveLayer(df, lyr)			
										

# ============================
# Join zonal statistics output
# ============================
# Loop through all rasters
for raster in rasterList:									

	# Merge all of the section tables together
	arcpy.env.workspace = working_tables
	listTable = arcpy.ListTables(raster + "_HUC*")
	mainTable = arcpy.Merge_management(listTable, gisTables_directory + "/" + raster + "_" + bufferID + ".dbf")

	# Delete the identical records
	uniqueTable = arcpy.DeleteIdentical_management(mainTable, [zoneField])

	# Get number of catchments in the output
	tab = arcpy.GetCount_management(uniqueTable)
	tabRows = int(tab.getOutput(0))

	# If some catchments are missing from the output table, then run the script to fill these in with NAs (-9999s)
	if tabRows < catRows:
		
		# Get the missing zone IDs
		# ------------------------
		mainIDs = unique_values(mainTable,  zoneField)
		allIDs  = unique_values(zoneObject, zoneField)
		
		missingIDs = list(list(set(allIDs) - set(mainIDs)))

		# Export missing features to new table
		# ------------------------------------
		
		# Define query
		qry = '"' + zoneField + '" IN ' + str(tuple(missingIDs))

		# Select the missing features from the source object
		arcpy.SelectLayerByAttribute_management ("zoneObject_lyr", 
													"NEW_SELECTION", 
													qry)

		# Export the missing features as a new table
		missingVals = arcpy.TableToTable_conversion("zoneObject_Lyr",
															gisTables_directory,
															raster + "_" + bufferID + "_MissingValues" + ".dbf")

		# Add fields to match the primary table
		# -------------------------------------
		arcpy.AddField_management(missingVals, "COUNT", "DOUBLE")
		arcpy.AddField_management(missingVals, "AREA", "DOUBLE")
		arcpy.AddField_management(missingVals, statType, "DOUBLE")

		arcpy.CalculateField_management (missingVals, "COUNT", 0, "PYTHON_9.3")
		arcpy.CalculateField_management (missingVals, "AREA", 0, "PYTHON_9.3")
		arcpy.CalculateField_management (missingVals, statType, -9999, "PYTHON_9.3")															

		# Append the missing values to the primary table
		# ----------------------------------------------
		arcpy.Append_management(missingVals,
									mainTable,
									"NO_TEST")

									
# ==================
# Export Area Tables
# ==================
# Check if the area table exists
if not arcpy.Exists(gisTables_directory + "/AreaSqKM" + bufferID + ".dbf"):

	# Export full table
	areaTable = arcpy.TableToTable_conversion(catchmentsFilePath, 
												gisTables_directory, 
												"AreaSqKM_" + bufferID + ".dbf")
	
	# List all fields
	fieldList  = arcpy.ListFields(areaTable)
	fieldsToDelete = []

	# Loop through all fields selecting those to delete
	for f in range(len(fieldList)):

		field = fieldList[f]
			
		curName = str(field.name)
		
		if not curName in ["OID", zoneField, "AreaSqKM"]: fieldsToDelete.append(curName)
		
	# Delete all fields that aren't the area or zone ID ("OID" can't be deleted)
	arcpy.DeleteField_management(areaTable, 
									fieldsToDelete)		
