Impoundments
============

This dataset contains information on waterbodies within a specified upstream distance of points in a watershed, currently NHDplus catchments. The values are calculated along the stream network from the the downstream point of each catchment. The catchments to calculate are determined by state. The impoundments layer provides the following values:

1. Distance to waterbody 
2. Surface area  or the waterbody
3. Contributing drainage area to each waterbody (taken from the NHDplus tables for the catchment in which the waterbody lies) 



## Data Sources
| Layer           | Source                                                 | Link                                                                         |
|:-----:          | ------                                                 | ----                                                                         |
| Wetlands Layer  | U.S. Fish & Wildlife National Wetlands Inventory       | http://www.fws.gov/wetlands/Data/Data-Download.html                          |
| Flowlines       | NHDPlus Version 2 Medium Resolution                    | http://www.horizon-systems.com/nhdplus/NHDPlusV2_data.php                    |
| State Boundaries| National Atlas of the United States (State Boundaries) | http://dds.cr.usgs.gov/pub/data/nationalatlas/statesp010g.shp_nt00938.tar.gz |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing structure in the repo should be followed. Raw data should be kept in the same format as it is downloaded.


1. Change the values in the "INPUTS.txt" file in the `scripts` folder. Be sure to keep the formatting the same. Do not add new lines before the existing ones. 
 - The order of states in the "states" and "stateNames" variables should match.
 - The "nhdplusRanges" should include all NHDplus ranges with which the states overlap.
 - "wetlandsFolder" is the source folder of the wetlands datasets by state
 - "nhdplusFolder" is the source folder of the NHDplus datasets by region
 - "state_boundaries" is the path to the state boundary shapefile needed for the arcPy script
 - "outputName" is the name that will be associated with this particular run of the tool (e.g. "NENYstates")
 - "upstreamLimitKM" is the maximum distance upstream from each point to include waterbodies
 
2. Run the script `impoundmentsProcessing_GIS.py` in ArcPython.
 - All that needs to be set in this is the base directory path (to the `impoundments` folder)
 
3. Run the script `impoundmentsProcessing_R.R` 
 - Specify the base directory path (`impoundments` folder)
 - Specify the catchment IDs ("FEATUREID") over which to calculate values. These should match the input range flowlines
 
4. The output .RData file named "impoundmentsByNHDCatchment_[outputName]" will be saved to the `products` folder. 

## Output Format
The output is stored in an RData file as a dataframe with 6 columns:

- The "FEATUREID" column refers to the catchment the data exists for. This will be used to link the data to catchments for prediction.
- The "Object_ID" column is a unique ID for each waterbody. The state abbreviation in this field describes which dataset the waterbody came from, but not necessarily the state which it falls in.
- The "COMID" column tells which catchment the waterbody lies in. All of the COMIDs lie upstream of the associated FEATUREID.
- The "AreaSqKM" column is the area of the waterbody.
- The "TotDASqKM" is the total upstream drainage area contributing to the waterbody (Note: This value is taken from the NHDplus catchment tables and refers to the drainage for the most downstream catchment into which the waterbody falls)
- The "DistKM" column is the distance to the waterbody fom the downstream point of the associated "FEATUREID"

Example: 
> 'data.frame':   312536 obs. of  6 variables:<br>
> $ COMID    : int  5849344 5849456 5849462 5849462 5849462 5849462 5849462 5849462 5849456 5849456 ...<br>
> $ Object_ID: int  139965 135752 135215 135241 135250 135315 135330 135372 135752 139965 ...<br>
> $ AreaSqKM : num  8.64e-04 6.45e-07 2.51e-08 4.59e-08 4.81e-08 ...<br>
> $ TotDASqKM: num  15.3 4.65 8.2 8.2 8.2 ...<br>
> $ DistKM   : num  0 2.48 6.66 5.8 9.74 ...<br>
> $ FEATUREID: int  5849344 5849344 5849344 5849344 5849344 5849344 5849344 5849344 5849456 5849456 ...<br>



## Possible Future Work
- Values from observed stream temperature sites (For now catchments may be used to associate the data with the observed sites)
- TNC dams dataset

