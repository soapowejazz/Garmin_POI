# Garmin_POI

This script allows you to see the POI created in Ride With GPS (RWGPS) in the POI screen on your Garmin Edge while riding. Normally, if you create a GPX route with POI in RWGPS and then send it to a Garmin Edge, you will only see the POI on the map. However, you will not be able to see the additional screen with the full list of all POI that Garmin creates automatically when POI are detected in the .fit file. The issue is the format in which the POI are reported in the .fit file. This script converts the .fit file to a version where the POI are recognized by Garmin and hence shown into a separate screen while riding.

Process you need to follow for this is the following:
 - Create your route in RWGPS and insert all the needed POI
 - Export the route in .gpx format and select "include POI as waypoints"
 - Export the route in .fit format, using the same name as used for the GPX format
 - Modify the variable FileName at the start of the script
 - Execute the script

Once complete, the script will save a copy of the original file with an additional "_POI" in the name. This contains the POI in the correct format for Garmin to detect them and show them into a separate screen while navigating.

In the file poi_codes there is a list that contains some keywords and the respective code for the POI. This is so that you can also see a descriptive icon next to the POI in the navigation screen. For example, for a restaurant you will see a fork and a knife. However, for this to work, the keywords written in the list in poi_codes have to be present in the name that you gave to the POI (not case sensitive). If no match is found, the default 53 code will be given which corresponds to the i of information.

NOTE: you also need the FitCSVTool from Garmin to convert the fit to a csv and viceversa. This is included in the repository and should be in the same folder as the POI_Garmin script
