#Import System Modules:
import arcpy
from arcpy import env
from arcpy.sa import *

# -------------------------------------------------------------------------
# Enter user inputs
# -------------------------------------------------------------------------
# Directories
rasterFolder = "C:/KPONEIL/massDOTCulvertProject/rasters"
tableFolder  = "C:/KPONEIL/massDOTCulvertProject/tables"
workspace    = "C:/KPONEIL/massDOTCulvertProject/workspace"
vectorFolder = "C:/KPONEIL/massDOTCulvertProject/shapefiles"

# Catchments file name
catchmentsFileName = "culverts_flowacc_11_25_Watersheds.shp"

# Raster names
rasterList = ["forest", "surfcoarse", "fwswetlands"] 

# Stat to calculate
statType = "MEAN"
# -------------------------------------------------------------------------

# Get catchments file path
catchmentsFilePath = vectorFolder + "/" + catchmentsFileName

# Import the supplemental tools (downloaded from here: http://blogs.esri.com/esri/arcgis/2013/11/26/new-spatial-analyst-supplemental-tools-v1-3/#comment-7007)
arcpy.ImportToolbox("C:/KPONEIL/tools/ArcGIS/SpatialAnalystSupplementalTools/Spatial Analyst Supplemental Tools.pyt")


# Add layers
# ----------
# Define map
mxd = arcpy.mapping.MapDocument("CURRENT")
# Define dataframe
df = arcpy.mapping.ListDataFrames(mxd)[0]

# Add the catchments layer to the map
addLayer = arcpy.mapping.Layer(catchmentsFilePath)
arcpy.mapping.AddLayer(df, addLayer, "AUTO_ARRANGE")


# Add fields
# ----------
# Define function to check for the existence of the field
def fieldExists(inFeatureClass, inFieldName):
   fieldList = arcpy.ListFields(inFeatureClass)
   for iField in fieldList:
      if iField.name.lower() == inFieldName.lower():
         return True
   return False


# Zone field
if not fieldExists(catchmentsFilePath, "FEATUREID"): 
	# Add the field that will be used for zonal statistics (Long integer format seems to work better than strings)
	arcpy.AddField_management(catchmentsFilePath, "FEATUREID", "LONG")
	arcpy.CalculateField_management(catchmentsFilePath, "FEATUREID", "!Name!", "PYTHON_9.3")

	# Add index to zone field to speed up zonal stats tool
	arcpy.AddIndex_management(catchmentsFileName, "FEATUREID")

# Area field
if not fieldExists(catchmentsFilePath, "AreaSqKM"): 	
	# Calculate the catchment area
	arcpy.AddField_management(catchmentsFileName, "AreaSqKM", "DOUBLE")
	arcpy.CalculateField_management (catchmentsFileName, "AreaSqKM", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3")	


# ====================
# Run Zonal Statistics
# ====================
for raster in rasterList:
		
	# Name of output table
	outTable = tableFolder + "/" + raster + ".dbf"
		
	arcpy.ZonalStatisticsAsTable02_sas(catchmentsFileName,
											"FEATUREID",
											rasterFolder + "/" + raster,
											outTable,
											statType,
											"DATA")	
											
	# Check for missing catchments. If some catchments are missing from the output table, then run the script to fill these in.
	cat = arcpy.GetCount_management(catchmentsFilePath) 
	catRows = int(cat.getOutput(0))
	tab = arcpy.GetCount_management(outTable)
	tabRows = int(tab.getOutput(0))

	# Might want to write this as a function
	if tabRows < catRows:
						
		# --------------------
		# Fill in missing data 
		# --------------------
		# Calculate raster values at centroid of catchment.
			
		# Join the output table to the catchments shapefile								
		attributeJoin = arcpy.AddJoin_management (catchmentsFileName, 
													"FEATUREID", 
													outTable, 
													"FEATUREID")

		# Define the query
		qry = raster + "."  + "FEATUREID" + ' IS NULL'
				
		qry = raster + ".FEATUREID IS NULL"
				
		# Select catchments					
		arcpy.FeatureClassToFeatureClass_conversion(attributeJoin, 
														workspace, 
														raster + "MissingCatchments.shp", 
														qry)

		# Remove the join
		arcpy.RemoveJoin_management(catchmentsFileName)
			
		del attributeJoin
			
		# Get the centroids of the missing catchments
		arcpy.FeatureToPoint_management(workspace + "/" + raster + "MissingCatchments.shp", 
											workspace + "/" + raster + "MissingCentroids", 
											"INSIDE")
						
		# Extract the raster values at centroids (need Spatial Analyst enabled)
		ExtractValuesToPoints (workspace + "/" + raster + "MissingCentroids.shp", 
										rasterFolder + "/" + raster, 
										workspace + "/" + raster + "MissingValues.shp", 
										"INTERPOLATE",
										"VALUE_ONLY")

		# Add a new field for the raster value to match the zonal statistics output table
		arcpy.AddField_management(workspace + "/" + raster + "MissingValues.shp", statType, "DOUBLE")
		arcpy.CalculateField_management (workspace + "/" + raster + "MissingValues.shp", statType, "!RASTERVALU!", "PYTHON_9.3")				
										
		# Export the missing values table
		arcpy.TableToTable_conversion(workspace + "/" + raster + "MissingValues.shp",
										workspace,
										raster + "_" + statType + "_" + "MissingValues.dbf")

		# Append the missing values to the existing table
		arcpy.Append_management(workspace + "/" + raster + "_" + statType + "_" + "MissingValues.dbf", 
									outTable, 
									"NO_TEST")
			
		# Delete the intermediate shapefiles
		arcpy.Delete_management(workspace + "/" + raster + "MissingCatchments.shp")						
		arcpy.Delete_management(workspace + "/" + raster + "MissingCentroids")						
		arcpy.Delete_management(workspace + "/" + raster + "MissingValues.shp")												