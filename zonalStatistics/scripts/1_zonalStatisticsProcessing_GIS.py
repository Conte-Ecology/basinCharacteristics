#Import System Modules:
import arcpy
from arcpy import env
from arcpy.sa import *

# ======================
# Specify Base Directory
# ======================

# Set base directory
baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics"


# =========================
# Read use specified inputs
# =========================

# Open file with input parameters
with open (baseDirectory + "/scripts/INPUTS.txt", "r") as myfile:
    lines = myfile.readlines()

outputName          = lines[1] .replace('outputName', '')         .replace('=', '').replace('\n','').replace('"','').replace(' ','')
catchmentsFileName  = lines[4] .replace('catchmentsFileName' , '').replace('=', '').replace('\n','').replace('"','').replace(' ','') + ".shp"
zoneField           = lines[7] .replace('zoneField' , '')         .replace('=', '').replace('\n','').replace('"','').replace(' ','')
statType            = lines[10].replace('statType' , '')          .replace('=', '').replace('\n','').replace('"','').replace(' ','')
rasterList          = lines[13].replace('rasterList', '')         .replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').split(",")


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
if not arcpy.Exists(vector_directory): arcpy.CreateFolder_management(vector_directory, "vectors")

# GIS files versions directory
gisVersion_directory = gisFiles_directory + "/versions"
if not arcpy.Exists(gisVersion_directory): arcpy.CreateFolder_management(gisVersion_directory, "versions")


#  Run-specific folders
# ---------------------
# Run-specific gisFiles directory
working_directory = gisVersion_directory + "/" + outputName
if not arcpy.Exists(working_directory): arcpy.CreateFolder_management(gisVersion_directory, outputName)

# Run-specific files
working_directory_processingFiles = working_directory + "/processingFiles"
if not arcpy.Exists(working_directory_processingFiles): arcpy.CreateFolder_management(working_directory, "processingFiles")

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



# ===============================
# Add Catchments shapefile to map
# ===============================
addLayer = arcpy.mapping.Layer(vector_directory + "/" + catchmentsFileName)

arcpy.mapping.AddLayer(df, addLayer, "AUTO_ARRANGE")


# If the zonal shapefile has not been rasterized, then do so.
	# This particular catchment file is derived from a 30m DEM and the coordinate system is in meters, so 30 works here.
if not arcpy.Exists(working_directory_processingFiles + "/catRaster"):

	arcpy.FeatureToRaster_conversion(vector_directory + "/" + catchmentsFileName, 
										zoneField, 
										working_directory_processingFiles + "/catRaster", 
										30)


# ============================
# Indexing Rasters
# ============================

if rasterList == ["ALL"]: 

	arcpy.env.workspace = raster_directory
	rasterList = [x.encode('UTF8') for x in arcpy.ListRasters()]

	
arcpy.env.workspace = working_directory
projectedRasters = [x.encode('UTF8') for x in arcpy.ListRasters()]





# RESAMPLE RASTERS....


for j in raster_count:
	out_file = "C:/KPONEIL/USGS/GIS/DATA/BrookTroutRange/Zonal Stats Layers/" + out_raster[j]
	arcpy.Resample_management(in_value_raster[j],out_file,0.00035088407,"NEAREST")

	
#Method will depend on type... not sure how to automate this easily(???)
# ... how about listing rasters with continuous data. 
# Default method will be "NEAREST", but pick a different one for any rasters that are continuous datasets (climate, elevation, etc.)


# =========================================
# Reproject Rasters to Catchment Projection
# =========================================

if (set(rasterList) <= set(projectedRasters)) == False:

	# List rasters that need to be projected
	rastersToProject = [x for x in rasterList if x not in projectedRasters]

	# Define the projection to use (that of the wetlands)
	projection_definition = vector_directory + "/" + catchmentsFileName

	# Name the spatial reference of the catchment
	catchSpatialRef = arcpy.Describe( vector_directory + "/" + catchmentsFileName ).spatialReference.name

	# Set directory
	arcpy.env.workspace = raster_directory

	# Copy each file with a .csv extension to a dBASE file
	for raster in rastersToProject:
		
		# Get spatial reference of raster
		rasterSpatialRef  = arcpy.Describe( raster_directory + "/" + raster ).spatialreference.name
		
		# Reproject the raster if needed
		if rasterSpatialRef != catchSpatialRef:
			arcpy.ProjectRaster_management (raster_directory + "/" + raster, 
												working_directory + "/" + raster,  
												projection_definition)
		else: arcpy.CopyRaster_management(raster_directory + "/" + raster, 
											working_directory + "/" + raster)


# ====================
# Run Zonal Statistics
# ====================

for raster in rasterList: # raster loop
	
	# -------------------------
	# Run zonal statistics tool
	# -------------------------
	
	#Name layers:
	outTable = gisTables_directory + "/" + raster + "_" + statType + ".dbf"

	#Produce zonal statistics
	ZonalStatisticsAsTable(vector_directory + "/" + catchmentsFileName,
									zoneField,
									working_directory + "/" + raster,
									outTable,
									"DATA",
									statType)
						
	# --------------------
	# Fill in missing data 
	# --------------------
	# Calculate raster values at centroid of catchment.
		
	# Join the output table to the catchments shapefile								
	attributeJoin = arcpy.AddJoin_management (catchmentsFileName, 
								zoneField, 
								outTable, 
								zoneField)

	# Define the query
	qry = raster +   "_"  + statType +  "."  + zoneField + ' IS NULL'
				
	# Select catchments					
	arcpy.FeatureClassToFeatureClass_conversion(attributeJoin, 
													working_directory_processingFiles, 
													raster + "MissingCatchments.shp", 
													qry)

	# Remove the join
	arcpy.RemoveJoin_management(catchmentsFileName)
		
	del attributeJoin
		
	# Get the centroids of the missing catchments
	arcpy.FeatureToPoint_management(working_directory_processingFiles + "/" + raster + "MissingCatchments.shp", 
										working_directory_processingFiles + "/" + raster + "MissingCentroids", 
										"INSIDE")
					
	# Extract the raster values at centroids (need Spatial Analyst enabled)
	ExtractValuesToPoints (working_directory_processingFiles + "/" + raster + "MissingCentroids.shp", 
									working_directory + "/" + raster, 
									working_directory_processingFiles + "/" + raster + "MissingValues.shp", 
									"INTERPOLATE",
									"VALUE_ONLY")

	# Add a new field for the raster value to match the zonal statistics output table
	arcpy.AddField_management(working_directory_processingFiles + "/" + raster + "MissingValues.shp", statType, "DOUBLE")
	arcpy.CalculateField_management (working_directory_processingFiles + "/" + raster + "MissingValues.shp", statType, "!RASTERVALU!", "PYTHON_9.3")							
									
	# Export the missing values table
	arcpy.TableToTable_conversion(working_directory_processingFiles + "/" + raster + "MissingValues.shp",
									gisTables_directory,
									raster + "_" + statType + "_" + "MissingValues.dbf")

	# Append the missing values to the existing table
	arcpy.Append_management(gisTables_directory + "/" + raster + "_" + statType + "_" + "MissingValues.dbf", 
								outTable, 
								"NO_TEST")

	# Remove the layers to save space
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, raster + "MissingCatchments", df)[0] )
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, raster + "MissingCentroids", df)[0] )
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, raster + "MissingValues", df)[0] )