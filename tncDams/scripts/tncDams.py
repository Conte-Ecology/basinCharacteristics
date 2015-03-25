# -----------------
# Specify inputs
# -----------------

# Define directories
baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/tncDams"
polygonsFile = "F:/KPONEIL/SourceData/streamStructure/northeastHRD/delin_basins_deerfield_2_17_2015.shp"
damsFile = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/connectivity/tnc/dams_on_med_rez.shp"

version = "pointDelineation"
# ---------------
# Folder creation
# ---------------

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Create version folder
versionDir = gisFilesDir + "/" + version
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, version)

# Create version database
geoDatabase = versionDir + "/processingFiles.gdb"
if not arcpy.Exists(geoDatabase): arcpy.CreateFileGDB_management(versionDir, "processingFiles.gdb")

# Create tables folder
tablesDir = versionDir + "/tables"
if not arcpy.Exists(tablesDir): arcpy.CreateFolder_management(versionDir, "tables")

# ----------------
# Define Functions
# ----------------

# Unique Values function	
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

# -------------
# Process Files
# -------------

# Spatial join the polygons and dams file
arcpy.SpatialJoin_analysis(polygonsFile,
							damsFile,
							geoDatabase + "/spatialJoin",
							"JOIN_ONE_TO_MANY",
							"KEEP_ALL",
							"#",
							"CONTAINS")
							

							
							
# Convert
rawTable = arcpy.TableToTable_conversion(geoDatabase + "/spatialJoin", 
											tablesDir, 
											"rawSpatialJoin")




											
fieldList  = arcpy.ListFields(rawTable)
fieldsToDelete = []

for f in range(len(fieldList)):

	field = fieldList[f]
		
	curName = str(field.name)
	
	if not curName in ["OID", "DelinID", "deg_barr"]: fieldsToDelete.append(curName)


arcpy.DeleteField_management(rawTable, 
                             fieldsToDelete)							



		# Get unique values
barriers = unique_values(damsFile, "deg_barr")


barrierFields = []

for bar in barriers:
	arcpy.AddField_management(rawTable, 
								"deg_barr_" + str(bar), 
								"LONG")		

	barrierFields.append("deg_barr_" + str(bar))


arcpy.MakeTableView_management(rawTable, "rawTable_View")								
								
								
for bar in barriers:
	arcpy.SelectLayerByAttribute_management("rawTable_View", 
												"NEW_SELECTION",
												""" "deg_barr" =  """ + str(bar) )
												
	arcpy.CalculateField_management ("rawTable_View", 
										"deg_barr_" + str(bar), 
										1, 
										"PYTHON_9.3")											

arcpy.SelectLayerByAttribute_management("rawTable_View", "CLEAR_SELECTION")
								
test = [ ["deg_barr_1", "SUM"], ["deg_barr_2", "SUM"] ]										
										
arcpy.Statistics_analysis("rawTable_View", 
							geoDatabase + "/damStats3", 
							test, 
							"DelinID")												