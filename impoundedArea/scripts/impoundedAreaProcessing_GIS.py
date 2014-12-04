import arcpy

# ==============
# Specify inputs
# ==============

baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/impoundedArea"
states = ["MA", "CT", "RI", "ME", "NH", "VT", "NY", "DE", "MD", "NJ", "PA", "VA", "WV"]
stateNames = ["Massachusetts", "Connecticut", "Rhode_Island", "Maine", "New_Hampshire", "VT", "New_York", "Delaware", "Maryland", "New_Jersey", "Pennsylvania", "Virginia", "West_Virginia"]
wetlandsFolder = "C:/KPONEIL/SourceData/fwsWetlands"
flowlinesFile = "F:/KPONEIL/SourceData/topography/Topography_UMASS/datainNortheast.gdb/allstreams"
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
# Set the run sub-folder. Create one if it doesn't exist.
working_directory = main_directory + "/" + outputName
if not arcpy.Exists(working_directory): arcpy.CreateFolder_management(main_directory, outputName)

# Set the run database. Create one if it doesn't exist.
working_db = working_directory + "/vectors.gdb"
if not arcpy.Exists(working_db): arcpy.CreateFileGDB_management (working_directory, "vectors", "CURRENT")

# Set the run raster folder. Create one if it doesn't exist.
working_raster = working_directory + "/rasters"
if not arcpy.Exists(working_raster): arcpy.CreateFolder_management(working_directory, "rasters")

# Set the output folder. Create one if it doesn't exist.
output_folder = working_directory + "/outputFiles"
if not arcpy.Exists(output_folder): arcpy.CreateFolder_management(working_directory, "outputFiles")


# Name the map and dataframe for removing layers
# ----------------------------------------------
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]



# ===================
# Reproject Flowlines
# ===================
# Define the projection to use (that of the wetlands)
projection_definition = wetlandsFolder + "/" + states[0] + "_wetlands.gdb/" + states[0] + "_Wetlands"

# Project
arcpy.Project_management(flowlinesFile, working_db + "/flowlines_prj",  projection_definition)



# ===================
# Create Range Raster
# ===================

# List the states
statePolyList = []

for i in range(len(stateNames)): 
	statePolyList.append(wetlandsFolder + "/" + states[i] + "_wetlands.gdb/" + stateNames[i])

# Merge state boundaries
arcpy.Merge_management(statePolyList, working_db + "/WaterbodyStates")

# Create regional outline
arcpy.Dissolve_management(working_db + "/WaterbodyStates", working_db + "/WaterbodyRange","#", "#", "SINGLE_PART", "DISSOLVE_LINES")	

# Calculate the field that determines the raster value
arcpy.AddField_management("WaterbodyRange", "rasterVal", "SHORT")
arcpy.CalculateField_management ("WaterbodyRange", "rasterVal", 0, "PYTHON_9.3")	

# Create template for the final raster
arcpy.PolygonToRaster_conversion(working_db + "/WaterbodyRange", 
										"rasterVal", 
										working_raster + "/rangeRaster", 
										"MAXIMUM_COMBINED_AREA", 
										"NONE", 
										30)



# Clip flowlines to outline
# -------------------------
arcpy.Clip_analysis(working_db + "/flowlines_prj", working_db + "/WaterbodyRange", working_db + "/flowlinesClip")


# Remove some layers from the map
# -------------------------------
arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "WaterbodyStates", df)[0] )
arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "flowlines_prj", df)[0] )
arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "WaterbodyRange", df)[0] )



# ===========================
# Polygon Processing by State
# ===========================
for j in range(len(states)): 

	# Select the Riverine classification. This will be used for selecting other water bodies.
	arcpy.FeatureClassToFeatureClass_conversion (wetlandsFolder + "/" + states[j] + "_wetlands.gdb/" + states[j] + "_Wetlands", 
																		working_db, 
																		"riverine_" + states[j], 
																		""" "WETLAND_TYPE" = 'Riverine' """)	

	
	# Open Water Classification Processing
	# ------------------------------------
	# Select the "open water" classification
	arcpy.FeatureClassToFeatureClass_conversion (wetlandsFolder + "/" + states[j] + "_wetlands.gdb/" + states[j] + "_Wetlands", 
																		working_db, 
																		"openWater_" + states[j], 
																		""" "WETLAND_TYPE" = 'Freshwater Pond' OR 
																			"WETLAND_TYPE" = 'Lake' """)
	# Dissolve the "open water" classification																
	arcpy.Dissolve_management(working_db + "/openWater_" + states[j], working_db + "/openDissolve_" + states[j],"#", "#", "SINGLE_PART", "DISSOLVE_LINES")	

	# Select only the waterbodies that intersect the flowlines
	arcpy.SelectLayerByLocation_management ("openDissolve_" + states[j], "INTERSECT", "flowlinesClip","", "NEW_SELECTION")		

	# Add to the previous selection the waterbodies that intersect the "riverine" class 
	arcpy.SelectLayerByLocation_management ("openDissolve_" + states[j], "INTERSECT", "riverine_" + states[j],"", "ADD_TO_SELECTION")		

	# Export the selection as a new file (On network)
	arcpy.FeatureClassToFeatureClass_conversion ("openDissolve_" + states[j], working_db, "openOnNetwork_" + states[j])

	# Switch the selection to grab the waterbodies that are off of the network
	arcpy.SelectLayerByAttribute_management("openDissolve_" + states[j], "SWITCH_SELECTION")		

	# Export the selection as a new file (Off network)
	arcpy.FeatureClassToFeatureClass_conversion ("openDissolve_" + states[j], working_db, "openOffNetwork_" + states[j])	
	
	
	# Rasterize the "Open Water" polygons
	# -----------------------------------
	# Calculate the fields for rasterization
	arcpy.AddField_management(working_db + "/openOnNetwork_" + states[j], "rasterVal", "SHORT")
	arcpy.CalculateField_management (working_db + "/openOnNetwork_" + states[j], "rasterVal", 1, "PYTHON_9.3")	
	arcpy.AddField_management(working_db + "/openOffNetwork_" + states[j], "rasterVal", "SHORT")
	arcpy.CalculateField_management (working_db + "/openOffNetwork_" + states[j], "rasterVal", 1, "PYTHON_9.3")	
	
	# Set processing extent for rasterization
	arcpy.env.extent = working_raster + "/rangeRaster"

	arcpy.PolygonToRaster_conversion("openOnNetwork_" + states[j], 
										"rasterVal", 
										working_raster + "/openOn_" + states[j],
										"MAXIMUM_COMBINED_AREA", 
										"NONE", 
										30)
	
	arcpy.PolygonToRaster_conversion("openOffNetwork_" + states[j], 
										"rasterVal", 
										working_raster + "/openOff_" + states[j],
										"MAXIMUM_COMBINED_AREA", 
										"NONE", 
										30)	

	
	
	# All Waterbodies Classification Processing
	# ------------------------------------------
	# Select the "all wetlands" classification
	arcpy.FeatureClassToFeatureClass_conversion (wetlandsFolder + "/" + states[j] + "_wetlands.gdb/" + states[j] + "_Wetlands", 
																		working_db, 
																		"allWaterbodies_" + states[j], 
																		""" "WETLAND_TYPE" = 'Freshwater Emergent Wetland' OR 
																			"WETLAND_TYPE" = 'Freshwater Forested/Shrub Wetland' OR 
																			"WETLAND_TYPE" = 'Freshwater Pond' OR 
																			"WETLAND_TYPE" = 'Lake' OR 
																			"WETLAND_TYPE" = 'Other' """)

	# Dissolve the "open water" classification																
	arcpy.Dissolve_management(working_db + "/allWaterbodies_" + states[j], working_db + "/allDissolve_" + states[j],"#", "#", "SINGLE_PART", "DISSOLVE_LINES")	

	# Select only the waterbodies that intersect the flowlines
	arcpy.SelectLayerByLocation_management ("allDissolve_" + states[j], "INTERSECT", "flowlinesClip","", "NEW_SELECTION")		

	# Add the waterbodies that intersect the "riverine" class to the previous selection
	arcpy.SelectLayerByLocation_management ("allDissolve_" + states[j], "INTERSECT", "riverine_" + states[j],"", "ADD_TO_SELECTION")		

	# Export the selection as a new file
	arcpy.FeatureClassToFeatureClass_conversion ("allDissolve_" + states[j], working_db, "allOnNetwork_" + states[j])

	# Switch the selection to grab the waterbodies that are off of the network
	arcpy.SelectLayerByAttribute_management("allDissolve_" + states[j], "SWITCH_SELECTION")
	
	# Export the selection as a new file (Off network)
	arcpy.FeatureClassToFeatureClass_conversion ("allDissolve_" + states[j], working_db, "allOffNetwork_" + states[j])
	
	# Calculate the fields for rasterization
	arcpy.AddField_management(working_db + "/allOnNetwork_" + states[j], "rasterVal", "SHORT")
	arcpy.CalculateField_management (working_db + "/allOnNetwork_" + states[j], "rasterVal", 1, "PYTHON_9.3")	
	arcpy.AddField_management(working_db + "/allOffNetwork_" + states[j], "rasterVal", "SHORT")
	arcpy.CalculateField_management (working_db + "/allOffNetwork_" + states[j], "rasterVal", 1, "PYTHON_9.3")	

	# Set processing extent for rasterization
	arcpy.env.extent = working_raster + "/rangeRaster"

	# Rasterize the polygon
	arcpy.PolygonToRaster_conversion("allOnNetwork_" + states[j], 
										"rasterVal", 
										working_raster + "/allOn_" + states[j],
										"MAXIMUM_COMBINED_AREA", 
										"NONE", 
										30)
	
	# Rasterize the polygon
	arcpy.PolygonToRaster_conversion("allOffNetwork_" + states[j], 
										"rasterVal", 
										working_raster + "/allOff_" + states[j],
										"MAXIMUM_COMBINED_AREA", 
										"NONE", 
										30)	

	# Remove intermediate layers from map
	# -----------------------------------
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "openWater_" + states[j], df)[0] )
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "openDissolve_" + states[j], df)[0] )
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "allWaterbodies_" + states[j], df)[0] )
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "allDissolve_" + states[j], df)[0] )
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "riverine_" + states[j], df)[0] )
# End polygon processing loop



# ==================
# Mosaicking Rasters
# ==================

# Open Water
# ----------

# List 4 categories
categories = ["openOn", "openOff", "allOn", "allOff"]

for k in range(len(categories)): 

	mosaicList = [working_raster + "/rangeRaster"]
	
	for s in range(len(stateNames)): 
		mosaicList.append(working_raster + "/" + categories[k] + "_" + states[s])
	del s
	
	# Set processing extent for rasterization
	arcpy.env.extent = working_raster + "/rangeRaster"
		
	arcpy.MosaicToNewRaster_management(mosaicList,
										output_folder, 
										categories[k] + "Net",
										working_raster + "/rangeRaster",
										"8_BIT_UNSIGNED", 
										30, 
										1, 
										"MAXIMUM",
										"FIRST")
	del mosaicList
