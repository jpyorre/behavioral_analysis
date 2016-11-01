# Process log file and add to mongodb

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

# Plotly:
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from plotly.offline.offline import _plot_html
import cufflinks as cf
import plotly.graph_objs as go

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'pcap'
COLLECTION_NAME = 'http'
fields = {'time': True, 'src_ip': True, 'useragent': True, 'dest_host': True, 'dest_ip':True, 'request_method': True, 'request': True, '_id':False}

# Count the number of times a something is seen:
def count_stuff(listofitems):
    listofitems_counted = Counter()
    for d in listofitems:
        t = d.split(',')[0]
        listofitems_counted[d] += 1
    return(listofitems_counted) 

def process_data():
    # Database details:
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=fields)
    #projects = collection.find()

   	# Get data from db and save results to a list
    #############################
    gets = [] # Hold the get requests
    posts = [] # Hold the posts
    gets_and_posts = []
    gets_full_entry = []
    gets_with_a_request = []
    posts_full_entry = []
    total_entries = []
    gets_and_posts_no_head = []

    for data in projects:
    	time = data['time']
    	useragent = data['useragent']
    	request_method = data['request_method']
    	request = data['request']
        src_ip = data['src_ip']
        dest_ip = data['dest_ip']
        dest_host = data['dest_host']


        if request_method == 'GET':
            if len(request) > 2: # Dirty way to negate the requests with no data
                line = "{0},{1},{2},{3},{4},{5},{6}".format(time,src_ip,useragent,dest_ip,dest_host,request_method,request)
                gets_with_a_request.append(line)

    	if len(request) > 2: # Dirty way to negate the requests with no data
            line = "{0},{1},{2},{3},{4},{5},{6}".format(time,src_ip,useragent,dest_ip,dest_host,request_method,request)
    	else:
    		line = "{0},{1},{2},{3},{4},{5},No request".format(time,src_ip,useragent,dest_ip,dest_host,request_method)

    	total_entries.append(line)

        # Used for counting the GETs and POSTs, for making the pie chart
        if request_method == 'GET':
            gets_and_posts.append('GET Requests')
            gets_and_posts_no_head.append(line)

        if request_method == 'POST':
            gets_and_posts.append('POSTs')
            gets_and_posts_no_head.append(line)
        ###################################

        # Get all the GETs (full line) and save to gets_full_entry
    	if request_method == 'GET':
    		gets.append(request_method)
    		gets_full_entry.append(line)
        # Get all the POSTs (full line) and save to posts_full_entry
    	if request_method == 'POST':
    		posts.append(request_method)
    		posts_full_entry.append(line)


    html_start = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/nvd3/1.7.0/nv.d3.min.css" rel="stylesheet" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/nvd3/1.7.0/nv.d3.min.js"></script>
        <script src="../../static/plotly-latest.min.js"></script>
    </head>
    <body>"""
    html_end = """
    </body>
    </html>"""
    ###################################
    # For a Pie Chart of GETS and POSTS: 
    count_request_method = count_stuff(gets_and_posts)
    count_of_request_methods = []
    temp = []
    for key, value in count_request_method.iteritems():
        temp = [key,value]
        count_of_request_methods.append(temp)

    xcategorylist = []
    ycategorylist = []
    for item in count_of_request_methods:
        xcategorylist.append(item[0])
        ycategorylist.append(item[1]) 

    type = 'pieChart'
    categorypiechart = pieChart(name=type, color_category='category20c', height=400, width=400)
    extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
    categorypiechart.add_serie(y=ycategorylist, x=xcategorylist, extra=extra_serie)
    categorypiechart.buildcontent()
    writefile = open('../flask/templates/pcap/pcap_category_piechart.html','w')
    writefile.write(html_start + categorypiechart.htmlcontent)

    writefile = open('../flask/templates/pcap/pcap_category_piechart.html','a')  # Re-open for appending
    header = "<b>Time, Source IP, Destination Host, Destination IP, Request Method, Request</b><br>"
    writefile.write(header)
    for line in gets_with_a_request:
        line = line.split(',')
        time, src_ip, dest_host, dest_ip, method, request = line[0],line[1],line[4],line[3],line[5],line[6]
        line = ("{0}, {1}, {2}, {3}, {4}<br>".format(time, src_ip, dest_host, dest_ip, method, request))
        writefile.write(line)
    for line in posts_full_entry:
        line = line.split(',')
        time, src_ip, dest_host, dest_ip, method, request = line[0],line[1],line[4],line[3],line[5],line[6]
        line = ("{0}, {1}, {2}, {3}, {4}, {5}<br>".format(time, src_ip, dest_host, dest_ip, method, request))
        writefile.write(line)
    writefile.write(html_end)

    # Timeseries of GETs vs POSTs with plotly
    xtime = []
    ytime = []
    for item in gets_and_posts_no_head:
        item = item.split(',')
        xtime.append(item[0])
        ytime.append(item[5])
    # Time Series
    df_timeseries = pd.DataFrame(ytime,xtime)
    plot_html, plotdivid, width, height =  _plot_html(df_timeseries.iplot(asFigure=True, kind ='bar', subplots=False, shared_xaxes=True, fill=True, title='Time Series',dimensions=(800,450)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('../flask/templates/pcap/pcap_timeseries.html', 'w')
    f.write(html_bar_chart)
    f.close()

# Check out domains with investigate
    #######################
    # STATS:

    number_of_gets = str(len(gets)) + " GET requests seen<br>"
    number_of_posts = str(len(posts)) + " POSTS seen<br>"

    #print number_of_gets
    #print number_of_posts
    		
process_data()