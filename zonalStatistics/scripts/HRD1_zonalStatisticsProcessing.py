#Import System Modules:
import arcpy
from arcpy import env
from arcpy.sa import *

# ======================
# Specify Base Directory
# ======================

baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics"


# =========================
# Read use specified inputs
# =========================

# Open file with input parameters
with open (baseDirectory + "/scripts/HRD_INPUTS.txt", "r") as myfile:
    lines = myfile.readlines()

outputName          = lines[1] .replace('outputName', '')         .replace('=', '').replace('\n','').replace('"','').replace(' ','')
catchmentsFileName  = lines[4] .replace('catchmentsFileName' , '').replace('=', '').replace('\n','').replace('"','').replace(' ','') + ".shp"
zoneField           = lines[7] .replace('zoneField' , '')         .replace('=', '').replace('\n','').replace('"','').replace(' ','')
statType            = lines[10].replace('statType' , '')          .replace('=', '').replace('\n','').replace('"','').replace(' ','')
discreteRasters     = lines[13].replace('discreteRasters', '')    .replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').split(",")
continuousRasters   = lines[14].replace('continuousRasters', '')  .replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').split(",")


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

# Raster directory
raster_directory = gisFiles_directory + "/rasters"
if not arcpy.Exists(raster_directory): arcpy.CreateFolder_management(gisFiles_directory, "rasters")

# Vector directory
vector_directory = gisFiles_directory + "/vectors"
if not arcpy.Exists(vector_directory): arcpy.CreateFolder_management(gisFiles_directory, "vectors")

# GIS files versions directory
gisVersion_directory = gisFiles_directory + "/versions"
if not arcpy.Exists(gisVersion_directory): arcpy.CreateFolder_management(gisFiles_directory, "versions")


#  Run-specific folders
# ---------------------
# Run-specific gisFiles directory
working_directory = gisVersion_directory + "/" + outputName
if not arcpy.Exists(working_directory): arcpy.CreateFolder_management(gisVersion_directory, outputName)

# Set the run database. Create one if it doesn't exist.
rasters_db = working_directory + "/projectedRasters.gdb"
if not arcpy.Exists(rasters_db): arcpy.CreateFileGDB_management (working_directory, "projectedRasters", "CURRENT")

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


# Name the map and dataframe for removing layers
# ----------------------------------------------
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]


# Add Catchments shapefile to map
# -------------------------------
addLayer = arcpy.mapping.Layer(vector_directory + "/" + catchmentsFileName)
arcpy.mapping.AddLayer(df, addLayer, "AUTO_ARRANGE")


# ======================================================
# Reproject & Resample Rasters to match catchment raster
# ======================================================
# If the zonal shapefile has not been rasterized, then do so.
	# This particular catchment file is derived from a 30m DEM and the coordinate system is in meters, so 30 works here for the cell size.
if not arcpy.Exists(working_directory + "/catRaster"):

	arcpy.FeatureToRaster_conversion(vector_directory + "/" + catchmentsFileName, 
										zoneField, 
										working_directory + "/catRaster", 
										30)

	# Generate the attribute field
	arcpy.BuildRasterAttributeTable_management(working_directory + "/catRaster", "NONE")
	
	# Add zoneField
	arcpy.AddField_management(working_directory + "/catRaster", zoneField, "LONG")
	arcpy.CalculateField_management (working_directory + "/catRaster", zoneField, "!VALUE!", "PYTHON_9.3")
	
	cellSize = int(arcpy.GetRasterProperties_management(working_directory + "/catRaster", "CELLSIZEX").getOutput(0))
	
	# Add zoneField
	arcpy.AddField_management(working_directory + "/catRaster", "AreaSqKM", "DOUBLE")
	arcpy.CalculateField_management("catRaster", "AreaSqKM", "[COUNT]*900/1000000", "VB", "#")
	
	arcpy.TableToTable_conversion("catRaster", gisTables_directory, "catRasterAreas.dbf")
	
	
# Define template raster (derived from catchments)
zonalRaster = working_directory + "/catRaster"	
cellX = int(arcpy.GetRasterProperties_management(zonalRaster, "CELLSIZEX").getOutput(0))

# Master list of rasters
rasterList = discreteRasters + continuousRasters

# Remove NAs if there are any
if "NA" in rasterList: rasterList.remove("NA")

# List rasters that have already been projected
arcpy.env.workspace = rasters_db
projectedRasters = [x.encode('UTF8') for x in arcpy.ListRasters()]

# Check if any of the rasters need to be projected/resampled
if not(set(rasterList) <= set(projectedRasters)):

	# List rasters that need to be projected
	rastersToProject = [x for x in rasterList if x not in projectedRasters]

	# Set directory
	arcpy.env.workspace = raster_directory

	# Copy each file with a .csv extension to a dBASE file
	for raster in rastersToProject:
		
		arcpy.env.snapRaster = zonalRaster
		
		# Project and resample discrete (categorical) rasters with appropriate resampling method
		if (raster in discreteRasters):
			arcpy.ProjectRaster_management(raster_directory + "/" + raster, 
											rasters_db + "/" + raster,  
											zonalRaster,
											"NEAREST",
											cellX,
											"#","#","#")
		# Project and resample continuous rasters with appropriate resampling method		
		if (raster in continuousRasters):
			arcpy.ProjectRaster_management(raster_directory + "/" + raster, 
											rasters_db + "/" + raster,  
											zonalRaster,
											"BILINEAR",
											cellX,
											"#","#","#")


# ====================
# Run Zonal Statistics
# ====================
for raster in rasterList: # raster loop
	
	# -------------------------
	# Run zonal statistics tool
	# -------------------------
	#Name layers:
	outTable = gisTables_directory + "/" + raster + "_" + statType + ".dbf"

	# Run zonal statistics over each layer using the rasterized catchments file
	ZonalStatisticsAsTable(zonalRaster,
								zoneField,
								rasters_db + "/" + raster,
								outTable,
								"DATA",
								statType)	

	# Calculate catchments with missing data
	# --------------------------------------
	# Join the output file to the catchments file
	attributeJoin = arcpy.AddJoin_management (catchmentsFileName, 
												zoneField, 
												outTable, 
												zoneField)
	
	# Define the query
	qry = raster +   "_"  + statType +  "."  + zoneField + ' IS NULL'
	
	arcpy.SelectLayerByAttribute_management (attributeJoin, "NEW_SELECTION", qry)
	
	missingVals = arcpy.TableToTable_conversion(catchmentsFileName,
												gisTables_directory,
												raster + "_" + statType + "_" + "MissingValues.dbf")
	
	# Remove the join & clear the selection
	arcpy.RemoveJoin_management(catchmentsFileName)
	arcpy.SelectLayerByAttribute_management(catchmentsFileName, "CLEAR_SELECTION")
	
	# Add a new field for the table to match the zonal statistics output table
	arcpy.AddField_management(missingVals, "AREA", "DOUBLE")
	arcpy.AddField_management(missingVals, statType, "DOUBLE")

	arcpy.CalculateField_management (missingVals, "AREA", 0, "PYTHON_9.3")
	arcpy.CalculateField_management (missingVals, statType, -9999, "PYTHON_9.3")							
			

	# Append the missing values to the existing table
	arcpy.Append_management(missingVals, 
								outTable, 
								"NO_TEST")