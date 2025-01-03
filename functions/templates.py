# Here below are listed all the default and fixed values that have to be inserted in the same row as the POI
# these values are stored in a dictionary which is then every time converted to a pandas dataframe and
# inserted at the right point in the record dataframe
# before the insertion the commented line have to be modified
poi_Template = {
'Type' : ['Data'],
'Local Number' : ['4'],
'Message' : ['course_point'],
# TIME STAMP
'Field 1' : ['timestamp'],
'Value 1' : [''], #this is the time stamp value,
'Units 1' : ['s'],
# LATITUDE
'Field 2' : ['position_lat'],
'Value 2' : [''], # latitude
'Units 2' : ['semicircles'],
# LONGITUDE
'Field 3' : ['position_long'],
'Value 3' : [''], #longitude
'Units 3' : ['semicircles'],
# DISTANCE
'Field 4' : ['distance'],
'Value 4' : [''], #distance
'Units 4' : ['m'],
# POI NAME
'Field 5' : ['name'],
'Value 5' : [''], # name of the POI,
'Units 5' : [''],
# POI TYPE
'Field 6' : ['type'],
'Value 6' : [''],# code type of POI
'Units 6' : [''],
'Field 7' : [''],
'Value 7' : [''],
'Units 7' : [''],
'Field 8' : [''],
'Value 8' : [''],
'Units 8' : [''],
'Field 9' : [''],
'Value 9' : [''],
'Units 9' : [''],
# 'Unnamed: 30' : [''],
}

# create another template for the definition of the POI
poi_Template_Def = {
'Type' : ['Definition'],
'Local Number' : ['5'],
'Message' : ['course_point'],
# TIME STAMP
'Field 1' : ['timestamp'],
'Value 1' : ['1'], #this is the time stamp value,
'Units 1' : [''],
# LATITUDE
'Field 2' : ['position_lat'],
'Value 2' : ['1'], # latitude
'Units 2' : [''],
# LONGITUDE
'Field 3' : ['position_long'],
'Value 3' : ['1'], #longitude
'Units 3' : [''],
# DISTANCE
'Field 4' : ['distance'],
'Value 4' : ['1'], #distance
'Units 4' : [''],
# POI NAME
'Field 5' : ['name'],
'Value 5' : ['11'], # name of the POI,
'Units 5' : [''],
# POI TYPE
'Field 6' : ['type'],
'Value 6' : ['1'],# code type of POI
'Units 6' : [''],
'Field 7' : [''],
'Value 7' : [''],
'Units 7' : [''],
'Field 8' : [''],
'Value 8' : [''],
'Units 8' : [''],
'Field 9' : [''],
'Value 9' : [''],
'Units 9' : [''],
# 'Unnamed: 30' : [''],
}