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
source_db = working_directory + "/sourceFiles.gdb"
if not arcpy.Exists(source_db): arcpy.CreateFileGDB_management (working_directory, "sourceFiles", "CURRENT")

# Set the run database. Create one if it doesn't exist.
buffer_db = working_directory + "/bufferTiles.gdb"
if not arcpy.Exists(buffer_db): arcpy.CreateFileGDB_management (working_directory, "bufferTiles", "CURRENT")

# Set the run database. Create one if it doesn't exist.
value_db = working_directory + "/valueTiles.gdb"
if not arcpy.Exists(value_db): arcpy.CreateFileGDB_management (working_directory, "valueTiles", "CURRENT")

# Set the run database. Create one if it doesn't exist.
intersect_db = working_directory + "/intersectTiles.gdb"
if not arcpy.Exists(intersect_db): arcpy.CreateFileGDB_management (working_directory, "intersectTiles", "CURRENT")


#  Output Table Folders
# ---------------------
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
if not arcpy.Exists(source_db + "/buffersProj_" + bufferID ):

	# Compare spatial references
	if not polySRName == rasterSRName:
		
		# Project catchments
		zoneObject = arcpy.Project_management(catchmentsFilePath, 
													source_db + "/buffersProj_" + bufferID, 
													rasterDirectory + "/" + rasterList[0])				
	else: zoneObject = catchmentsFilePath												
																						
else: zoneObject = source_db + "/buffersProj_" + bufferID

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
if not arcpy.Exists(source_db + "/hucsProj"):

	# Compare spatial references
	if not hucsSRName == rasterSRName:

		# Project HUCs
		hucsObject = arcpy.Project_management(hucFilePath, 
												source_db + "/hucsProj", 
												rasterDirectory + "/" + rasterList[0])
	else: hucsObject = hucFilePath
else: hucsObject = source_db + "/hucsProj"

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

	print(huc)

	# Define the current section buffer filepath
	bufferTilePath = buffer_db + "/buffers" + bufferID + "_" + "HUC" + huc
	
	# Check if the file exists from the previous run
	if not arcpy.Exists(bufferTilePath):

		# Select the HUC boundary for selecting buffer polygons
		hucSelection = arcpy.SelectLayerByAttribute_management("hucsObject_Lyr", 
																"NEW_SELECTION", 
																'"HUC6" = ' + "'" + huc + "'")

		# Select the buffer polygons that are within the HUC boundary (including those on the edge)
		zoneSelection = arcpy.SelectLayerByLocation_management("zoneObject_Lyr", 
																"INTERSECT", 
																hucSelection, 
																"#", 
																"NEW_SELECTION")
		
		# Export the selection as a separate file
		bufferTile =  arcpy.FeatureClassToFeatureClass_conversion(zoneSelection,
																	buffer_db,
																	"buffers" + bufferID + "_" + "HUC" + huc)
																	
	else: bufferTile = bufferTilePath
	
	
	# Define the current section buffer filepath
	hucMaskPath = value_db + "/hucMask_HUC" + huc
	
	# Check if the file exists from the previous run
	if not arcpy.Exists(hucMaskPath):
	
		hucMask = arcpy.Buffer_analysis(hucSelection, 
											hucMaskPath, 
											"10 Kilometers", 
											"FULL", 
											"ROUND", 
											"NONE", 
											"#")
	else: hucMask = hucMaskPath


	# Loop through 
	for raster in rasterList:
	
		print(raster)
	
		outputTable = gisTables_directory + "/" + raster + bufferID + "_HUC" + huc + ".dbf"
	
		if not arcpy.Exists(outputTable):
	
			# 
			valueTilePath = value_db + "/" + raster + "_HUC" + huc
		
			# Check if the file exists from the previous run
			if not arcpy.Exists(valueTilePath):
				clipRaster = ExtractByMask(rasterDirectory + "/" + raster, 
											hucMask)
				
				valueTile = arcpy.RasterToPolygon_conversion(clipRaster, 
																valueTilePath, 
																"NO_SIMPLIFY",
																"VALUE")

				arcpy.Delete_management(clipRaster)
			else: valueTile = valueTilePath
			
			
			
			intersectTilePath = intersect_db + "/" + raster + bufferID + "_HUC" + huc
			
			if not arcpy.Exists(intersectTilePath):
				intersectTile = arcpy.Intersect_analysis ([bufferTile, valueTile],
														intersectTilePath,
														"ALL", "", "")	
			else: intersectTile = intersectTilePath
			
			
			arcpy.AlterField_management(intersectTile, 'gridcode', 'Value', 'Value')
			
			arcpy.AddField_management       (intersectTile, "AreaSqM", "DOUBLE")
			arcpy.CalculateField_management (intersectTile, "AreaSqM", "!SHAPE.AREA@SQUAREMETERS!", "PYTHON_9.3")

			
			
			arcpy.CopyRows_management(intersectTile, 
										outputTable)
		
		
		
			# Delete fields
			# -------------	
			fieldList  = arcpy.ListFields(outputTable)
			fieldsToDelete = []

			for f in range(len(fieldList)):

				field = fieldList[f]
				curName = str(field.name)
				if not curName in ["OID", zoneField, "Value", "AreaSqM"]: fieldsToDelete.append(curName)
						
			arcpy.DeleteField_management(outputTable, fieldsToDelete)		
											
											
										
			# Remove intermediate layers from map
			# -----------------------------------
			allLyrs = []
			for lyr in arcpy.mapping.ListLayers(mxd, "", df):
				allLyrs.append(lyr.name)
			
			# intersectTile
			if(raster + bufferID + "_HUC" + huc in allLyrs):	
				lyr = arcpy.mapping.Layer(raster + bufferID + "_HUC" + huc)
				arcpy.mapping.RemoveLayer(df, lyr)
					
			# valueTile
			if(raster + "_HUC" + huc in allLyrs):	
				lyr = arcpy.mapping.Layer(raster + "_HUC" + huc)
				arcpy.mapping.RemoveLayer(df, lyr)
			
		# End if
		
	# hucMask
				
	allLyrs = []
	for lyr in arcpy.mapping.ListLayers(mxd, "", df):
		allLyrs.append(lyr.name)
	
	# HUC extraction polygon
	if("hucMask_HUC" + huc in allLyrs):	
		lyr = arcpy.mapping.Layer("hucMask_HUC" + huc)
		arcpy.mapping.RemoveLayer(df, lyr)
			
	# HUC buffer polygon
	if("buffers" + bufferID + "_" + "HUC" + huc in allLyrs):	
		lyr = arcpy.mapping.Layer("buffers" + bufferID + "_" + "HUC" + huc)
		arcpy.mapping.RemoveLayer(df, lyr)


									
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
