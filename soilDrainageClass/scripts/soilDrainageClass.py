import arcpy
from arcpy import env
from arcpy.sa import *

# ==============
# Specify inputs
# ==============

baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/soilDrainageClass"
states = ["MA", "CT", "RI", "ME", "NH", "VT", "NY", "DE", "MD", "NJ", "PA", "VA", "WV", "DC"]
states = ["MA", "CT"]
soilsFolder = "C:/KPONEIL/data/land/nrcsSSURGO/spatial"
outputName = "Northeast"

# ===========
# Folder prep
# ===========

# Create general folders if they don't exist
# ------------------------------------------
# Set the main GIS directory. Create one if it doesn't exist.
main_directory = baseDirectory + "/gisFiles"
if not arcpy.Exists(main_directory): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Create run specific folders if they don't exist
# -----------------------------------------------
# Set the run-specific sub-folder. Create one if it doesn't exist.
working_directory = main_directory + "/" + outputName
if not arcpy.Exists(working_directory): arcpy.CreateFolder_management(main_directory, outputName)

# Set the run-specific table database. Create one if it doesn't exist.
tableDB = working_directory + "/tables.gdb"
if not arcpy.Exists(tableDB): arcpy.CreateFileGDB_management (working_directory, "tables", "CURRENT")

# Set the run-specific vector database. Create one if it doesn't exist.
vectorDB = working_directory + "/vectors.gdb"
if not arcpy.Exists(vectorDB): arcpy.CreateFileGDB_management (working_directory, "vectors", "CURRENT")

## Set the run-specific raster folder. Create one if it doesn't exist.
rasterFolder = working_directory + "/rasters"
if not arcpy.Exists(rasterFolder): arcpy.CreateFolder_management(working_directory, "rasters")

## Set the run-specific output folder. Create one if it doesn't exist.
outputFolder = working_directory + "/outputFiles"
if not arcpy.Exists(outputFolder): arcpy.CreateFolder_management(working_directory, "outputFiles")


# Name the map and dataframe for removing layers
# ----------------------------------------------
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]


#
## I don't think we need the range raster for this type as no values get removed from drainage class...
#

# ===================
# Create Range Raster
# ===================

## Create a list of the state polygons
##for k in range(len(states)):
#	statePolyList.append(soilsFolder + "/" + "gssurgo_g_" + states[k] + ".gdb/SAPOLYGON")
#
## Merge state boundaries
#arcpy.Merge_management(statePolyList, vectorDB + "/SoilsStates")
#
## Create regional outline
#arcpy.Dissolve_management(vectorDB + "/SoilsStates", vectorDB + "/SoilsRange","#", "#", "SINGLE_PART", "DISSOLVE_LINES")
#
## Calculate the field that determines the raster value
#arcpy.AddField_management("SoilsRange", "rasterVal", "SHORT")
#arcpy.CalculateField_management ("SoilsRange", "rasterVal", 0, "PYTHON_9.3")	
#
## Create template for the final raster
#arcpy.PolygonToRaster_conversion("SoilsRange", 
#									"rasterVal", 
#									rasterFolder + "/rangeRaster", 
#									"MAXIMUM_COMBINED_AREA", 
#									"NONE", 
#									30)


# ========================
# Create the state rasters
# ========================
for i in range(len(states)): 

	# Copy the Mapunit polygon to the current directory for editing
	arcpy.FeatureClassToFeatureClass_conversion(soilsFolder + "/" + "gssurgo_g_" + states[i] + ".gdb/MUPOLYGON", 
													vectorDB, 
													"MUPOLYGON_" + states[i])

	## Add the field that will be taken from the tables
	#arcpy.AddField_management("MUPOLYGON_" + states[i], 
	#							"DrainClass", 
	#							"TEXT")


	# Join "component" table to the polygon
	# -------------------------------------
	# Add table to map
	addTable = arcpy.mapping.TableView(soilsFolder + "/" + "gssurgo_g_" + states[i] + ".gdb/component")
		
	#Export tables to new tables so the original tables don't get accidentally altered
	arcpy.TableToTable_conversion(addTable, tableDB, "component_" + states[i])
		
	# Join tables to polygon
	arcpy.AddJoin_management("MUPOLYGON_" + states[i], "mukey", "component" + "_" + states[i], "mukey")

	
	# Generate state rasters
	# ----------------------
	# Calculate the Drainage Class field in the Mapunit polygon
	#arcpy.CalculateField_management ("MUPOLYGON_" + states[i], "DrainClass", "!drainagecl!", "PYTHON_9.3")	

	#
	## Might be able to skip the step where a new field is calculated
	#

	# Convert to raster
	arcpy.PolygonToRaster_conversion("MUPOLYGON_" + states[i], 
											"component_" + states[i] + ".drainagecl", 
											rasterFolder + "/DrnCls_" + states[i], 
											"MAXIMUM_COMBINED_AREA", 
											"NONE", 
											30)
											
	# Remove some layers from the map
	# -------------------------------
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "DrnCls_" + states[i], df)[0] )
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "MUPOLYGON_"  + states[i], df)[0] )

# End state loop



# ==================										
# Mosaic the rasters
# ==================										


mosaicList = []
		
for s in range(len(states)): 
	mosaicList.append(rasterFolder + "/DrnCls_" + states[s])
del s

#Since there isn't a range raster, not entire sure how mosaicking will work...
		
## Set processing extent for rasterization
#arcpy.env.extent = rasterFolder + "/rangeRaster"
		
arcpy.MosaicToNewRaster_management(mosaicList,
									rasterFolder, 
									"rawDrnCls",
									"#",
									"8_BIT_UNSIGNED", 
									30, 
									1, 
									"MAXIMUM",
									"FIRST")

									

# Import system modules

#
## The reclassfication step needs to go within the loop, before mosaicking.
#

# Set environment settings
#env.workspace = "C:/sapyexamples/data"

# Set local variables
inRaster = "rawDrnCls"
reclassField = "DrainClass"
remap = RemapValue([["Excessively drained", 1], 
					["Somewhat excessively drained", 2],
					["Well drained", 3],
					["Moderately well drained", 4],
					["Somewhat poorly drained", 5],
					["Poorly drained", 6],
					["Very poorly drained", 7]])

# Check out the ArcGIS Spatial Analyst extension license
#arcpy.CheckOutExtension("Spatial")

# Execute Reclassify
outReclassify = Reclassify(rasterFolder + "/rawDrnCls", reclassField, remap, "NODATA")

# Save the output 
outReclassify.save(outputFolder + "/drainclass")





									
arcpy.AddField_management("DrainVal", "rasterVal", "SHORT")
arcpy.CalculateField_management ("SoilsRange", "rasterVal", 0, "PYTHON_9.3")	
									
1 = Excessively drained
2 = Somewhat excessively drained
3 = Well drained
4 = Moderately well drained
5 = Somewhat poorly drained
6 = Poorly drained
7 = Very poorly drained				
									
									