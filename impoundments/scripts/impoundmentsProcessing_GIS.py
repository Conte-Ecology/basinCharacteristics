import arcpy

# ==========================
# Specify the base directory
# ==========================

baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/impoundments"


# =====================
# Read in common inputs
# =====================

# Open file with input parameters
with open (baseDirectory + "/scripts/INPUTS.txt", "r") as myfile:
    lines = myfile.readlines()

states         = lines[0].replace('states', '')        .replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').split(",")
stateNames     = lines[1].replace('stateNames', '')    .replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').replace('_',' ').split(",")
nhdplusRanges  = lines[2].replace('nhdplusRanges', '') .replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').split(",")
wetlandsFolder = lines[3].replace('wetlandsFolder', '').replace('=', '').replace('\n','').replace('"','').replace(' ','')
nhdplusFolder  = lines[4].replace('nhdplusFolder', '') .replace('=', '').replace('\n','').replace('"','').replace(' ','')
state_boundaries = lines[5].replace('state_boundaries', '') .replace('=', '').replace('\n','').replace('"','').replace(' ','')
geodatabase_name = lines[6].replace('outputName', '') .replace('=', '').replace('\n','').replace('"','').replace(' ','')


# ===========
# Folder prep
# ===========

# Set the working directory. Create one if it doesn't exist.
working_directory = baseDirectory + "/gisFiles"
if not arcpy.Exists(working_directory): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Set the output file directory. Create one if it doesn't exist.
output_directory = baseDirectory + "/outputFiles/" + geodatabase_name
if not arcpy.Exists(baseDirectory + "/outputFiles"): arcpy.CreateFolder_management(baseDirectory, "outputFiles")
if not arcpy.Exists(output_directory): arcpy.CreateFolder_management(baseDirectory + "/outputFiles", geodatabase_name)

# Name of database
working_db = working_directory + "/" + geodatabase_name + ".gdb"

# Check if the geodatabase exists. Create one if it doesn't.
if not arcpy.Exists(working_db): arcpy.CreateFileGDB_management (working_directory, geodatabase_name, "CURRENT")


# ===============
# Reproject files
# ===============

# Define the projection to use (that of the wetlands)
projection_definition = wetlandsFolder + "/" + states[0] + "_shapefile_wetlands/CONUS_wet_poly.shp"

# Reproject the flowlines
for NHDRange in nhdplusRanges:
	
	# Define input and output
	nhdplus_file       = nhdplusFolder + "/NHDPlus" + NHDRange + "/NHDPlusSnapshot/Hydrography/NHDFlowline.shp"
	flowlines_prj_file = working_db + "/flowlines_prj_" + NHDRange
	
	# Project
	arcpy.Project_management(nhdplus_file, flowlines_prj_file,  projection_definition)
# end loop (NHDRange)
	
# Reproject the state boundaries
states_prj_file = arcpy.Project_management(state_boundaries, working_db + "/states_prj",  projection_definition)	


# =====================================================
# Loop through states locating waterbodies on flowlines
# =====================================================

for i in range(len(states)):

	# 1. Prep wetlands file for processing
	# ------------------------------------
	
	# Select current wetlands file (looping by state)
	wetlands_file = wetlandsFolder + "/" + states[i] + "_shapefile_wetlands/CONUS_wet_poly.shp"	

	# Create shapefile of groups that are not "Estuarine and Marine Wetland", "Estuarine and Marine Deepwater", or "Riverine"
	select_wetlands = arcpy.FeatureClassToFeatureClass_conversion (wetlands_file, 
																	working_db, 
																	"selected_wetlands_" + states[i], 
																	""" "WETLAND_TY" = 'Freshwater Emergent Wetland' OR 
																		"WETLAND_TY" = 'Freshwater Forested/Shrub Wetland' OR 
																		"WETLAND_TY" = 'Freshwater Pond' OR 
																		"WETLAND_TY" = 'Lake' OR 
																		"WETLAND_TY" = 'Other' """)

	## Dissolve the wetlands
	dissolve_wetlands = arcpy.Dissolve_management(select_wetlands, working_db + "/wetlands_dissolved_" + states[i],"#", "#", "SINGLE_PART", "DISSOLVE_LINES")	
	
	# Calculate new fields so they are available in output
	
	# Area
	arcpy.AddField_management(dissolve_wetlands, "AreaSqKM", "DOUBLE")
	arcpy.CalculateField_management (dissolve_wetlands, "AreaSqKM", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3")

	# Object ID
	arcpy.AddField_management(dissolve_wetlands, "Object_ID", "LONG")
	arcpy.CalculateField_management (dissolve_wetlands, "Object_ID", "!OBJECTID!", "PYTHON_9.3")	
	
	# 2. Select flowlines that intersect the remaining waterbodies
	# ------------------------------------------------------------
	
	# Select the boundary of the current state
	current_state = arcpy.FeatureClassToFeatureClass_conversion (state_boundaries, 
																	working_db, 
																	"boundary_" + states[i], 
																	'"' + "STATE" + '" =' + "'" + stateNames[i] + "'")
	 
	# Use state boundary to select all flowlines within a range of the current state
	NHD_count = range(len(nhdplusRanges))
	for k in NHD_count:

		cur_flow = "flowlines_prj_" + nhdplusRanges[k]

		arcpy.SelectLayerByLocation_management (cur_flow, "WITHIN_A_DISTANCE", current_state, "50.0 KILOMETERS", "NEW_SELECTION")
	# end for (k)
		
	# Join the selected flowlines into one shapefile
	current_flowlines = arcpy.Merge_management(["flowlines_prj_" + ran for ran in nhdplusRanges],working_db +"/flowline_buffer_" + states[i])

	# Select only the flowlines that intersect the waterbodies
	impounded_flowlines = arcpy.SelectLayerByLocation_management ("flowline_buffer_" + states[i], "INTERSECT", "wetlands_dissolved_" + states[i],"", "NEW_SELECTION")	
	
	# 3. Determine the waterbody positions along the flowlines
	# --------------------------------------------------------
	arcpy.LocateFeaturesAlongRoutes_lr("wetlands_dissolved_"+ states[i], 
											impounded_flowlines ,
											"COMID",
											"0 METERS", 
											output_directory + "/impoundments_" + states[i] + ".dbf",
											"RID LINE FMEAS TMEAS",
											"FIRST",
											"DISTANCE",
											"ZERO",
											"FIELDS",
											"M_DIRECTON")
# end loop (i)