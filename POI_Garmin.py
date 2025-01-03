#%%
import pandas as pd
import math
import numpy as np
from garmin_fit_sdk import Decoder, Stream
import os
from fit_tool.fit_file import FitFile
import subprocess

from functions.haversine import*
from functions.poi_codes import*
from functions.templates import*

#%% USER INPUT
# This is the name of the input file and it should be the same for the .gpx and the .fit files

#FileName = input('Please enter the name of the file, without extension, of the track
# Note that the .gpx and the .fit file MUST have the same name
FileName = 'Ultimate_P1'


#%% READ GPX, TRACK POINTS AND POI
# Define conversion commands for Fit tool
commandIN = ['java', '-jar' ,'FitCSVTool.jar', str(FileName)+'.fit']
commandOUT = ['java', '-jar' ,'FitCSVTool.jar', '-c', str(FileName)+'_POI.csv' , str(FileName) +'_POI.fit']

# Define the directory where the script is as working directory
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

## Read the GPX file and remove the white line at the beginning of the lines
print('Reading the GPX file to get the coordinate of the track points and the POI')
with open(FileName+'.gpx', 'r') as file:
    # Read lines and store them in a list
    gpx = [line.lstrip() for line in file.readlines()]

# create a pandas dataframe that contains all the track points
gpx_track = pd.DataFrame(columns=['Lati','Long','Dist','Cum Dist'])

# read all the track points and store the position in the data frame as latitude and longitude
# In addition, calculate the distance between each pair of points and
# the total cumulative distance of the whole track
counter = 0 # counter for the lines written in the dataframe and the corresponding coordinates
for line in gpx:
    if line.startswith('<trkpt'):
        data = line.split() # the line is split based on empty spaces
        gpx_track.at[counter,'Lati'] = float(data[1].split('"')[1]) # the element 1 from the split line is the latitude, and that is split once again based on "" to extract only the number
        gpx_track.at[counter,'Long'] = float(data[2].split('"')[1]) # the element 1 from the split line is the longitude, and that is split once again based on "" to extract only the number
        if counter == 0: # at the first line don't calculate any distance
            gpx_track.at[counter,'Dist'] = 0.0
            gpx_track.at[counter,'Cum Dist'] = 0.0
        else: # for all other lines calculate the distances between two points and the cumulative distance of the whole track
            lat1 = gpx_track.loc[counter-1,'Lati']
            lon1 = gpx_track.loc[counter-1,'Long']
            lat2 = gpx_track.loc[counter,'Lati']
            lon2 = gpx_track.loc[counter,'Long']
            distance = haversine(lat1,lon1,lat2,lon2)*1000 # the function calculates the distance in Km, hence x1000 to get it in meters
            gpx_track.at[counter,'Dist'] = distance
            gpx_track.at[counter,'Cum Dist'] = gpx_track.loc[counter-1,'Cum Dist']+distance
        counter += 1

# create a pandas dataframe that contains all the POI
gpx_poi = pd.DataFrame(columns=['Lati','Long','Name','Desc'])

# read all the POI and store the respective
# latitude
# longitude
# name
# description, if present

wpt = False
name = False
desc = False
counter = 0 # counter for the lines written in the dataframe and the corresponding coordinates
for line in gpx:
    if line.startswith('<wpt'):
        wpt = True
        data = line.split() # the line is split based on empty spaces
        gpx_poi.at[counter,'Long'] = float(data[1].split('"')[1]) # the element 1 from the split line is the latitude, and that is split once again based on "" to extract only the number
        gpx_poi.at[counter,'Lati'] = float(data[2].split('"')[1]) # the element 1 from the split line is the longitude, and that is split once again based on "" to extract only the number
        current_wpt = counter # save the current counter value to make sure the values of name and description of this POI are saved at the same line in the dataframe

    if wpt == True and line.startswith('<name>'):
        name = True
        gpx_poi.at[current_wpt,'Name'] = line.replace('<name>','').replace('</name>\n','')

    if wpt == True and name == True and line.startswith('<desc>'):
        desc = True
        gpx_poi.at[current_wpt,'Desc'] = line.replace('<desc>','').replace('</desc>\n','')
        
    if line.startswith('</wpt>'):
        wpt = False
    
    counter += 1

# reset the index of the POI dataframe to start at zero
gpx_poi.reset_index(drop=True, inplace=True)

#%% CREATE NEX GPX WITH TRACK POINTS AND ORDERED

print('Create a new temporary GPX file where the POI are placed at the correct position among the track points')
# create a pandas dataframe that contains all the track points plus the POI
gpx_all = pd.DataFrame(columns=['Lati','Long','Dist','Cum Dist','Name','Desc'])

# the first line of this dataframe can be just equal to the first line of the gpx track
gpx_all.at[0,'Lati'] = gpx_track.loc[0,'Lati']
gpx_all.at[0,'Long'] = gpx_track.loc[0,'Long']
gpx_all.at[0,'Dist'] = 0.0
gpx_all.at[0,'Cum Dist'] = 0.0
gpx_all.at[0,'Name'] = 'NA'
gpx_all.at[0,'Desc'] = 'NA'
poi_num = 0 # index that keeps track of the POI number, intially set at 0
gpx_num = 1 # index that keeps track of the number of GPX track point, starting at 1 because first line is already filled
counter = 1 # index that keep track of the current line in the full GPX track+POI, starting at 1 because first line is already filled
poi_found = False # boolean to track if a POI has been found or not
while gpx_num < len(gpx_track): # iterate until the whole length of the GPX track file is covered
    lat1 = gpx_all.loc[counter-1,'Lati'] # get the latitude of the previous point
    lon1 = gpx_all.loc[counter-1,'Long'] # get the longitude of the previous point
    lat_gpx = gpx_track.loc[gpx_num,'Lati'] # get the latitude of the current point on the gpx track
    lon_gpx = gpx_track.loc[gpx_num,'Long'] # get the longitude of the current point on the gpx track
    dist_gpx = haversine(lat1,lon1,lat_gpx,lon_gpx)*1000 # calculate the distance between the new point on the GPX track and the previous
    if len(gpx_poi)>0: # if there are still POI to be included. This can be checked with the length of the POI list
        # now it is not known if the POI are ordered by distance or not, hence it is assumed that the order is random
        # this means that it has to be iterated through all the available POI in the list to find the one that is closer
        for poi_index in range(0,len(gpx_poi)):
            lat_poi = gpx_poi.loc[poi_index,'Lati'] # get the latitude of the current point on the POI list
            lon_poi = gpx_poi.loc[poi_index,'Long'] # get the longitude of the current point on the POI list
            dist_poi = haversine(lat1,lon1,lat_poi,lon_poi)*1000 # calculate the distance between the new POI track and the previous point on the GPX track
            if dist_poi < dist_gpx: # if the distance is less than the GPX distance
                print(f'Found POI, {gpx_poi.loc[poi_index,"Name"]}') # print the name of the POI found
                poi_insert = poi_index # save the index of the POI to be inserted in the track
                lat_poi_insert = lat_poi # save the latitude of the POI to insert
                lon_poi_insert = lon_poi # save the longitude of the POI to insert
                dist_poi_insert = dist_poi # save the distance of the POI to insert
                poi_found = True # change this boolean to later on insert the POI
    if poi_found == True:
        gpx_all.at[counter,'Lati'] = lat_poi_insert # insert the latitude of the POI
        gpx_all.at[counter,'Long'] = lon_poi_insert # insert the longitude of the POI
        gpx_all.at[counter,'Dist'] = dist_poi_insert # insert the distance of the POI
        gpx_all.at[counter,'Cum Dist'] = dist_poi_insert + gpx_all.loc[counter-1,'Cum Dist'] # calculate the cumulative distance
        gpx_all.at[counter,'Name'] = gpx_poi.loc[poi_insert,'Name'] # insert the name of the POI
        gpx_all.at[counter,'Desc'] = gpx_poi.loc[poi_insert,'Desc'] # insert the description, if available, of the POI
        poi_num = poi_num + 1 # increase the POI conuter but not the GPX track counter
        gpx_poi.drop(poi_insert,inplace=True) # remove the POI from the list of POI
        gpx_poi.reset_index(drop=True,inplace=True)
        poi_found = False # change this boolean back to false until another POI is found
    else:
        gpx_all.at[counter,'Lati'] = lat_gpx # insert the latitude of the GPX point
        gpx_all.at[counter,'Long'] = lon_gpx # insert the longitude of the GPX point
        gpx_all.at[counter,'Dist'] = dist_gpx # insert the distance of the GPX point
        gpx_all.at[counter,'Cum Dist'] = dist_gpx + gpx_all.at[counter-1,'Cum Dist'] # calculate the cumulative distance
        gpx_all.at[counter,'Name'] = 'NA'
        gpx_all.at[counter,'Desc'] = 'NA'
        gpx_num = gpx_num + 1 # increase the GPX track counter but not the POI counter
    counter = counter + 1 # increase the line counter for the full GPX file

#%% READ ORIGINAL FIT FILE
# First of all the fit file needs to be converted to a csv file
print('Converting the FIT file to CSV')
process = subprocess.Popen(commandIN, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

# Read the FIT file into a Pandas Dataframe.
# this is read ALL as string, so that it's easier to modify the data in the next steps
print('Reading the CSV file')
fit = pd.read_csv(FileName+'.csv',dtype='str').fillna('')

# convert the columns with the altitudes to decimals with only one comma
# for doing this, the strings containing the altitudes are split using the decimal point, if available
# and the decimal part is shortened
for i in range(0,len(fit['Value 5'])):
    text = str(fit.loc[i,'Value 5'])
    try:
        number = text.split('.')
        height = number[0] + '.' + number[1][0]
        fit.at[i,'Value 5'] = height
    except:
        pass
    
for i in range(0,len(fit['Value 6'])):
    text = str(fit.loc[i,'Value 6'])
    try:
        number = text.split('.')
        height = number[0] + '.' + number[1][0]
        fit.at[i,'Value 6'] = height
    except:
        pass

# the part of the csv file that contains the route point has the "message" type as record
# filter the dataframe to only extract the record data
# To do this, first find the first and last row where this entry occurs
first_record = fit.index[fit['Message'] == 'record'].min()
last_record = fit.index[fit['Message'] == 'record'].max()

# and then extract the part of the dataframe that is needed
record = fit.iloc[first_record:last_record+1]

# make a copy of the data frame
record_original = record

# finally, reset the index of the record dataframe
record.reset_index(drop=True,inplace=True)

# also the part of the csv that contains course points has to be extracted
first_course = fit.index[fit['Message'] == 'course_point'].min()
last_course = fit.index[fit['Message'] == 'course_point'].max()

# and then extract the part of the dataframe that is needed
course = fit.iloc[first_record:last_record+1]

# now save all the rest of the csv into two separate dataframes, since those parts will not be modified
if np.isnan(first_course):
    before = fit.iloc[:first_record]
else:
    before = fit.iloc[:first_course]
after = fit.iloc[last_record+1:]

#record = fit[fit['Message'] == 'record']

# Now from the gpx_all dataframe that contains all the POI, extract the position of the POI
poi_index = gpx_all[gpx_all['Name'] != 'NA'].index.to_list()

#%% ADD POI TO FIT FILE
print('Adding the POI to the FIT file')

# create an empty dataframe that will contain all the defined POI
course_points = pd.DataFrame()

# iterate through the whole list of gpx points in order to find the appropriate time stamp 
# and the appropriate distance for all the POI
for i in range(0,len(poi_index)):
    split = poi_index[i] # get the position of the POI in the full gpx
    upper = record.iloc[:split] # split the dataframe in the upper
    lower = record.iloc[split:] # and lower part
    time = record.loc[split-1,'Value 1'] # get the time stamp value of the last point before the POI
    poi_Template['Value 1'] = str(int(time) + 10) # assign the time point stamp as 10 + the one from the previous point
    poi_Template['Value 2'] = str(int(gpx_all.loc[split,'Lati'] * ((2**32)/360))) # get the latitude of the POI and convert to integer
    poi_Template['Value 3'] = str(int(gpx_all.loc[split,'Long'] * ((2**32)/360))) # get the longitude of the POI and convert to integer
    lat1 = int(record.loc[split-1,'Value 2']) / ((2**32)/360) # get the latitude of the last point before the POI
    lon1 = int(record.loc[split-1,'Value 3']) / ((2**32)/360) # get the longitude of the last point before the POI
    lat2 = int(poi_Template['Value 2']) / ((2**32)/360)
    lon2 = int(poi_Template['Value 3']) / ((2**32)/360)
    distance = haversine(lat1,lon1,lat2,lon2)*1000 # calculate the distance between the last point and the POI
    poi_Template['Value 4'] = round(distance + float(record.loc[split-1,'Value 4']),1) # copy the distance for the new line of the POI
    poi_Template['Value 5'] = gpx_all.loc[split,'Name'] # pick up the name of the POI
    # based on the POI name, try to associate a code with it.
    # if nothing can be found, the POI will receive the coding of a generic information
    code_found = 0
    for j in range(0, len(codes)):
        keywords = codes[j][0]
        for keyword in keywords:
            if keyword == poi_Template['Value 5'].lower() or keyword in poi_Template['Value 5'].lower(): # when checking the equality with the poi name, put the POI name all in lower case
                poi_code = codes[j][1]
                code_found = 1
                print(f'Found code {poi_code[0]} for {poi_Template["Value 5"]}')
    if code_found == 1:
        poi_Template['Value 6'] = poi_code[0] # give the appropriate code to the POI
    else:
        poi_Template['Value 6'] = '53' # if no coding is found, the general info numbering is associated
    newrow = pd.DataFrame.from_dict(poi_Template)
    course_points = pd.concat([course_points,newrow],ignore_index=True)
    record = pd.concat([upper,newrow,lower],ignore_index=True)


    # at this point the new POI is in, by the time stamps of all the following points 
    # have to be updated by the number 10 that has been added above
    for j in range(split+1,len(record)):
        record.at[j,'Value 1'] = str(int(record.loc[j,'Value 1']) + 10)

        
# Next step is to re-number the course points and all the gpx points
# convert the number to numeric
record['Local Number'] = pd.to_numeric(record['Local Number'])
# define a condition
condition = record['Message'] == 'record'
# reduce the "record" points by 1 and increase the "course_points" by 1
# record.loc[condition,'Local Number'] -= 1
record.loc[~condition,'Local Number'] += 1

# The definition for the "course_point" has to be now added, just before the first occurrence of the course_points
# find the position of the first occurrence of course_point
split = (record['Message'] == 'course_point').idxmax()
upper = record.iloc[:split] # split the dataframe in the upper
lower = record.iloc[split:] # and lower part
definition = pd.DataFrame.from_dict(poi_Template_Def) # definition of course_point
record = pd.concat([upper,definition,lower],ignore_index=True)

# newfit = pd.concat([before,course_points,record,after],ignore_index=True)
newfit = pd.concat([before,record,after],ignore_index=True)

# and also need to remove the last column which has been taken over from the previous fit file
newfit.drop('Unnamed: 30', inplace=True, axis=1)


float_format_dict = {'Value 1': '%.3f','Value 2': '%.0f','Value 3': '%.0f', 'Value 4': '%.1f'}

# newfit['Value 1'].astype(int)
print('Saving the modified CSV file with all POI')
newfit.to_csv(FileName + '_POI.csv', index=False,float_format='%.0f')

# Finally re convert the .csv file to a .fit file
print('Converting the CSV file with all POI back to FIT')
process = subprocess.Popen(commandOUT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()