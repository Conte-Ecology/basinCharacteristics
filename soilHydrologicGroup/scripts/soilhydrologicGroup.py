import arcpy

# ==============
# Specify inputs
# ==============

baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/soilHydrologicGroup"
states = ["MA", "CT", "RI", "ME", "NH", "VT", "NY", "DE", "MD", "NJ", "PA", "VA", "WV", "DC"]
soilsFolder = "F:/KPONEIL/SourceData/geology/SSURGO"
outputName = "Northeast"


# Hydrologic group Combos	
a =		""" "HYDGRP" = 'A' """

ab = 	""" "HYDGRP" = 'A' OR 
			"HYDGRP" = 'B' """
	
cd = 	""" "HYDGRP" = 'C' OR 
			"HYDGRP" = 'D' OR 
			"HYDGRP" = 'C/D' """

d1 = 	""" "HYDGRP" = 'D' """

d4 =	""" "HYDGRP" = 'A/D' OR 
			"HYDGRP" = 'B/D' OR 
			"HYDGRP" = 'C/D' OR
			"HYDGRP" = 'D' """
	
grpList = [a, ab, cd, d1, d4]
grpListNames = ["a", "ab", "cd", "d1", "d4"]


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



# ===================
# Create Range Raster
# ===================

# Create a list of the state polygons
statePolyList = []
for k in range(len(states)):
	statePolyList.append(soilsFolder + "/" + "gssurgo_g_" + states[k] + ".gdb/SAPOLYGON")

# Merge state boundaries
arcpy.Merge_management(statePolyList, vectorDB + "/SoilsStates")

# Create regional outline
arcpy.Dissolve_management(vectorDB + "/SoilsStates", vectorDB + "/SoilsRange","#", "#", "SINGLE_PART", "DISSOLVE_LINES")

# Calculate the field that determines the raster value
arcpy.AddField_management("SoilsRange", "rasterVal", "SHORT")
arcpy.CalculateField_management ("SoilsRange", "rasterVal", 0, "PYTHON_9.3")	

# Create template for the final raster
arcpy.PolygonToRaster_conversion("SoilsRange", 
									"rasterVal", 
									rasterFolder + "/rangeRaster", 
									"MAXIMUM_COMBINED_AREA", 
									"NONE", 
									30)


										
# ========================
# Create the state rasters
# ========================
for i in range(len(states)): 

	# Copy the Mapunit polygon to the current directory for editing
	arcpy.FeatureClassToFeatureClass_conversion(soilsFolder + "/" + "gssurgo_g_" + states[i] + ".gdb/MUPOLYGON", 
													vectorDB, 
													"MUPOLYGON_" + states[i])

	# Add the field that will be taken from the tables
	arcpy.AddField_management("MUPOLYGON_" + states[i], 
								"hydro_grp", 
								"TEXT")


	# Join "component" table to the polygon
	# -------------------------------------
	# Add table to map
	addTable = arcpy.mapping.TableView(soilsFolder + "/" + "gssurgo_g_" + states[i] + ".gdb/component")
		
	#Export tables to new tables so the original tables don't get accidentally altered
	arcpy.TableToTable_conversion(addTable, tableDB, "component_" + states[i])
		
	# Join tables to polygon
	arcpy.AddJoin_management("MUPOLYGON_" + states[i], "mukey", "component" + "_" + states[i], "mukey")

	
	# Generate polygon of desired classifications
	# -------------------------------------------
	# Calculate the texture field in the Mapunit polygon
	arcpy.CalculateField_management ("MUPOLYGON_" + states[i], "hydro_grp", "!hydgrp!", "PYTHON_9.3")	
	
	for j in range(len(grpList)):
	
		# Select out the categories for Hydrologic Group classifications
		statePolyGrp = arcpy.FeatureClassToFeatureClass_conversion (vectorDB + "/MUPOLYGON_" + states[i], 
																		vectorDB, 
																		"hydgrp_" + grpListNames[j] + "_" + states[i], 
																		grp[j])

		# Rasterize the state polygon
		# ---------------------------
		# Calculate the field that determines the raster value
		arcpy.AddField_management(statePolyGrp, "rasterVal", "SHORT")
		arcpy.CalculateField_management (statePolyGrp, "rasterVal", 1, "PYTHON_9.3")		
					
		# Set the extent																			 
		arcpy.env.extent = rasterFolder + "/rangeRaster"																			 

		# Convert to raster
		arcpy.PolygonToRaster_conversion(statePolyGrp, 
											"rasterVal", 
											rasterFolder + "/hydgrp_" + grpListNames[j] + "_" + states[i], 
											"MAXIMUM_COMBINED_AREA", 
											"NONE", 
											30)
											
		# Remove some layers from the map
		# -------------------------------
		arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "hydgrp_" + grpListNames[j] + "_" + states[i], df)[0] )
		arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "MUPOLYGON_"  + states[i], df)[0] )

# End state loop


# ==================										
# Mosaic the rasters
# ==================										

# Loop through each hydrologic group classification
# -------------------------------------------------
for k in range(len(grpList)):

	mosaicList = [rasterFolder + "/rangeRaster"]
		
	for s in range(len(states)): 
		mosaicList.append(rasterFolder + "/hydgrp_" + grpListNames[k] + "_" + states[s])
	del s
		
	# Set processing extent for rasterization
	arcpy.env.extent = rasterFolder + "/rangeRaster"
		
	arcpy.MosaicToNewRaster_management(mosaicList,
										outputFolder, 
										"hydrogroup_" + grpListNames[k],
										rasterFolder + "/rangeRaster",
										"8_BIT_UNSIGNED", 
										30, 
										1, 
										"MAXIMUM",
										"FIRST")
