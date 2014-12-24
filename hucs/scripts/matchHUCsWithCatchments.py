# -----------------
# Specify inputs
# -----------------

# Define directories
baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/hucs"
catchmentsFolder = "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/gisFiles/vectors"
hucFilesDir = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/wbd"

# Name of catchments file
catchmentsFileName = "NortheastHRD_AllCatchments.shp"

# List the HUC levels to process
hucs = [4,6,8,10,12]

# Create a version ID for saving
version = "NortheastHRD_2013HUCs"

# Do you want to keep the intermediate GIS files ( "YES" or "NO" ) 
keepFiles = "YES"

#      ***** DO NOT CHANGE SCRIPT BELOW THIS POINT ****

# ---------------
# Folder creation
# ---------------

# Defines the path to the catchments file
catchmentsFilePath = catchmentsFolder + "/" + catchmentsFileName

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Create version folder
versionDir = gisFilesDir + "/" + version
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, version)

# Create version database
geoDatabase = versionDir + "/workingFiles.gdb"
if not arcpy.Exists(geoDatabase): arcpy.CreateFileGDB_management(versionDir, "workingFiles.gdb")

# Create tables folder
tablesDir = versionDir + "/tables"
if not arcpy.Exists(tablesDir): arcpy.CreateFolder_management(versionDir, "tables")


# Name of centroid file (for referencing)
centroidFileName = catchmentsFileName.replace('.shp', '_Centroids')

# Calcuate catchment centroids for mapping to HUCs
if not arcpy.Exists(geoDatabase + "/" + centroidFileName):
	# Get the centroids of the missing catchments
	centroids = arcpy.FeatureToPoint_management(catchmentsFilePath, 
									geoDatabase + "/" + centroidFileName, 
									"INSIDE")



# Define the projection to use (that of the wetlands)
projection_definition = catchmentsFilePath

# Name the spatial reference of the catchment
catchSpatialRef = arcpy.Describe( catchmentsFilePath ).spatialReference.name

# Set directory
arcpy.env.workspace = geoDatabase

# Copy each file with a .csv extension to a dBASE file
for huc in hucs:
		
	# Get spatial reference of raster
	hucSpatialRef = hucFilesDir +  "/WBDHU" + str(huc) + "_June2013.gdb/WBDHU" + str(huc)
	
	# New huc file
	newHUC = geoDatabase + "/HUC" + str(huc)
	
	# Reproject the raster if needed, otherwise copy it to the workspace
	if not arcpy.Exists(newHUC):
		if hucSpatialRef != catchSpatialRef:
			hucFile = arcpy.Project_management  (hucSpatialRef, 
												newHUC,  
												projection_definition)
		else: hucFile = arcpy.CopyFeatures_management (hucSpatialRef, 
											newHUC)
	else: hucFile = newHUC

	# Name of spatial join file (for referencing)
	spatialJoinName = catchmentsFileName.replace('.shp', '_HUC' + str(huc))
	
	# Map the HUCs to catchment centroids
	spatialJoin = arcpy.SpatialJoin_analysis(centroids, 
												hucFile, 
												geoDatabase + "/" + spatialJoinName)
	
	# Save the results as a table
	outputTable = arcpy.TableToTable_conversion(spatialJoin,
													tablesDir, 
													spatialJoinName + ".dbf",
													"HUC" + str(huc) + " <> ''")	


	# ------------------------------
	# Account for missing catchments
	# ------------------------------
	# Some catchment centroids fall outside of the HUC shapefile boundaries. These features area separated and spatially joined
	#	using the "CLOSEST" match option, which takes far too long to run over all features to begin with.
	
	# Join the spatial join result to the original centroid file
	attributeJoin = arcpy.AddJoin_management (centroidFileName,
													"FEATUREID", 
													spatialJoinName, 
													"FEATUREID")
	
	# Select points without assigned HUCs
	arcpy.SelectLayerByAttribute_management (attributeJoin, 
												"NEW_SELECTION", 
												"HUC" + str(huc) + " IS NULL")
	
	# Remove the join
	arcpy.RemoveJoin_management(attributeJoin, spatialJoinName)
	
	# Export the file
	missingCentroids = arcpy.CopyFeatures_management(attributeJoin, geoDatabase + "/Missing_HUC" + str(huc))

	# If there are missing catchments, assign HUCs
	if arcpy.GetCount_management(missingCentroids) > 0:
	
		# Map the HUCs to the missing centroids
		missingJoin = arcpy.SpatialJoin_analysis(missingCentroids, 
													hucFile, 
													geoDatabase + "/" + catchmentsFileName.replace('.shp', 'Missing_HUC' + str(huc)), 
													"#", "#", "#", "CLOSEST")

		# Export the results as a table
		missingTable = 	arcpy.TableToTable_conversion(missingJoin,
														tablesDir, 
														"Missing_HUC" + str(huc) + ".dbf")
													
													
		# Append the missing values to the existing table
		arcpy.Append_management(missingTable, 
									outputTable, 
									"NO_TEST")

		# Delete the intermediate shapefiles	
		if keepFiles == "NO": 
			arcpy.Delete_management(missingJoin)
			arcpy.Delete_management(missingTable)
		# End if
	# End if 
	
	if keepFiles == "NO": 
			arcpy.Delete_management(spatialJoin)
			arcpy.Delete_management(missingCentroids)
	# End if
# End for

# Delete the intermediate shapefiles	
if keepFiles == "NO": arcpy.Delete_management(centroids)		