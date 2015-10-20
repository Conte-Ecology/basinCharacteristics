import arcpy
from arcpy.sa import *
from arcpy import env

# ==============
# Specify inputs
# ==============
baseDirectory  = "C:/KPONEIL/GitHub/projects/basinCharacteristics/topography"
#demFilePath = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/topography/NHDHRDV2/dem"
demFilePath = "F:/KPONEIL/SourceData/topography/NHDHRDV2/dem"
version = "NHDHRDV2"


# ---------------
# Folder creation
# ---------------

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Create version folder
versionDir = gisFilesDir + "/" + version
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, version)

# Create output folder
outputDir = versionDir + "/outputFiles"
if not arcpy.Exists(outputDir): arcpy.CreateFolder_management(versionDir, "outputFiles")


# --------------
# Create rasters
# --------------
# Generate the slope raster
outSlope = Slope(demFilePath, "PERCENT_RISE")
outSlope.save(outputDir + "/slope_pcnt")

# Move the DEM & rename
arcpy.CopyRaster_management(demFilePath,
								outputDir + "/elevation")









# Create regional outline
if not arcpy.Exists(geoDatabase + "/outline"):
	outline = arcpy.Dissolve_management(catchmentsFilePath, 
											geoDatabase + "/outline",
											"#", 
											"#", 
											"SINGLE_PART", 
											"DISSOLVE_LINES")
else: outline = geoDatabase + "/outline"

# Buffer outline
if not arcpy.Exists(geoDatabase + "/boundary"):
	boundary = arcpy.Buffer_analysis(outline, 
										geoDatabase + "/boundary", 
										"1 Kilometers", 
										"#", 
										"#", 
										"ALL")
else: boundary = geoDatabase + "/boundary"

# Reproject the boundary to match the covariate raster
if not arcpy.Exists(geoDatabase + "/boundaryProj"):
	boundaryProj = arcpy.Project_management(boundary, 
											geoDatabase + "/boundaryProj", 
											sourceFolder + "/" + rasterList[0] + ".tif")
else: boundaryProj = geoDatabase + "/boundaryProj"

# -------------------
# Process the rasters
# -------------------

for r in range(len(rasterList)):

	# Trim raster to boundary
	# -----------------------
	# Define the raster file path
	rasterFilePath = sourceFolder + "/" + rasterList[r] + ".tif"

	# Trim the raster to the boundary	
	arcpy.env.extent = rasterFilePath
	extractedRaster  = ExtractByMask(rasterFilePath, boundaryProj)
	
	# Save the trimmed raster
	extractedRaster.save(outputDir + "/" + rasterList[r])