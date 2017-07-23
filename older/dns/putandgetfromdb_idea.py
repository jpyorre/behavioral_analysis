from pymongo import MongoClient
from netaddr import valid_ipv4
from netaddr import valid_ipv6
from collections import Counter
import investigate
import pandas as pd
from tldextract import tldextract
from bson import json_util
from bson.json_util import dumps
import json
from nvd3 import discreteBarChart, pieChart

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'tcpdumpdns'
#COLLECTION_NAME = 'connections'
COLLECTION_NAME = '2000'
fields = {'time':True, 'domain':True, '_id':False}

# Put categories into db (db is called tcpdumpdns, collection is called content_cat_counts)
    connection = MongoClient(MONGODB_HOST)
    db = connection[DBS_NAME]['content_cat_counts']
    for line in category_list: 
        category =line[0]
        count =line[1]
        db.insert({'content_category':category, 'content_cat_counts':count})


# Get data for piechart from db        
xcategorylist = []  # Array to hold the category names
ycategorylist = []  # Array to hold the category counts
temp = [] # Array to hold category names and category names as a string (to turn this dict into an array of its own)
collection = connection[DBS_NAME]['content_cat_counts']
categorycounts_fromdb = collection.find(projection={'content_category':True, 'content_cat_counts':True, '_id':False})
for value in categorycounts_fromdb:
    cat = value['content_category']
    cat_count = value['content_cat_counts']
    line = ("{0},{1}".format(cat, cat_count))   # Save the category name and count from the dict as a string called 'line'
    temp.append(line)   # add 'line' into a list

# Read each line of temp, separating the 'line' into two values:
for item in temp:
    item = item.split(',')
    xcategorylist.append(item[0])   # Append the category name to it's own list (for piechart)
    ycategorylist.append(item[1])   # Append the category count to it's own list (for piechart)

### generate the category piechart:
type = 'pieChart'
categorypiechart = pieChart(name=type, color_category='category20c', height=1000, width=1000)
extra_serie = {"tooltip": {"y_start": "", "y_end": ""}}
categorypiechart.add_serie(x=xcategorylist, y=ycategorylist, extra=extra_serie)
categorypiechart.buildhtml()
writefile = open('templates/category_piechart.html','w')
writefile.write(categorypiechart.htmlcontent)