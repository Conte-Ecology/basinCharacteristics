# -----------------
# Enter user inputs
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


# Get the centroids of the missing catchments
centroids = arcpy.FeatureToPoint_management(catchmentsFilePath, 
								geoDatabase + "/" + catchmentsFileName.replace('.shp', '_Centroids'), 
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

	# Map the HUCs to catchment centroids
	spatialJoin = arcpy.SpatialJoin_analysis(centroids, 
												hucFile, 
												geoDatabase + "/" + catchmentsFileName.replace('.shp', '_HUC' + str(huc)), 
												"#", "#", "#", "CLOSEST")
												

	# Save the output table
	arcpy.TableToTable_conversion(spatialJoin,
									tablesDir, 
									catchmentsFileName.replace('.shp', '_HUC' + str(huc)) + ".dbf")
	
	# Delete the intermediate shapefiles	
	if keepFiles == "NO": arcpy.Delete_management(spatialJoin)	

# Delete the intermediate shapefiles	
if keepFiles == "NO": arcpy.Delete_management(centroids)		




qry = "HUC" + str(huc) + " = ''"
				
# Select catchments					
missingCentroids = arcpy.FeatureClassToFeatureClass_conversion(spatialJoin, 
																geoDatabase, 
																"Missing_HUC" + str(huc), 
																qry)

# Map the HUCs to catchment centroids
MissingJoin = arcpy.SpatialJoin_analysis(missingCentroids, 
											hucFile, 
											geoDatabase + "/" + catchmentsFileName.replace('.shp', 'Missing_HUC' + str(huc)), 
											"#", "#", "#", "CLOSEST")


# Append the missing values to the existing table
arcpy.Append_management(MissingJoin, 
							spatialJoin, 
							"NO_TEST")

arcpy.TableToTable_conversion(spatialJoin,
									tablesDir, 
									catchmentsFileName.replace('.shp', '_HUC' + str(huc)) + ".dbf")
											
											
											
											
											
											
											
											
											
											


arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings)

# Dealing with catchments without HUCs
HUC4 = ''


# Time to run?
arcpy.SpatialJoin_analysis(geoDatabase + "/test", 
							geoDatabase + "/HUC4", 
							geoDatabase + "/" + catchmentsFileName.replace('.shp', '_test4HUC' + str(4)), 
							"#", "#", "#", "CLOSEST")



