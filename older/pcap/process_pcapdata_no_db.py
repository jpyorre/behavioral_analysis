from netaddr import valid_ipv4
from netaddr import valid_ipv6
from collections import Counter
import investigate
import pandas as pd
from tldextract import tldextract
from bson import json_util
from bson.json_util import dumps
import json, sys, dpkt, datetime, socket
from nvd3 import discreteBarChart, pieChart
import quickmap

# Plotly:
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from plotly.offline.offline import _plot_html
import cufflinks as cf
import plotly.graph_objs as go

input_file = sys.argv[1]

f = open(input_file)
pcap = dpkt.pcap.Reader(f)

# Count the number of times a something is seen:
def count_stuff(listofitems):
    listofitems_counted = Counter()
    for d in listofitems:
        t = d.split(',')[0]
        listofitems_counted[d] += 1
    return(listofitems_counted) 

def process_data():

    pcapdata = []

    for ts, buf in pcap:
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data
        tcp = ip.data

        dtstring=datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S:%f') # Convert time to string
        #dt=datetime.datetime.strptime(dtstring,'%d-%m-%Y %H:%M:%S:%f') # Convert string time to datetime
        
        try:
            if len(tcp.data) > 0:
                http = dpkt.http.Request(tcp.data)
                headers = http.headers
                dest_ip = socket.inet_ntoa(ip.dst)
                src_ip = socket.inet_ntoa(ip.src)
                dest_host = headers['host']
                uri = http.uri
                useragent = headers['user-agent']
                request = repr(http['body'])
                #data = (dtstring, http.method)
                data = ("{0},{1},{2},{3},{4},{5},{6}".format(dtstring, src_ip, useragent, dest_host, dest_ip, http.method, request))
                pcapdata.append(data)

        except:
            continue

        
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
    alltimes = []

    for data in pcapdata:
        data = data.split(',')
        
    	time = data[0]
    	useragent = data[2]
    	request_method = data[5]
    	request = data[6]
        src_ip = data[1]
        dest_ip = data[4]
        dest_host = data[3]

        

        if request_method == 'GET':
            if len(request) > 2: # Dirty way to negate the requests with no data
                line = "{0},{1},{2},{3},{4},{5},{6}".format(time,src_ip,useragent,dest_ip,dest_host,request_method,request)
                gets_with_a_request.append(line)

    	if len(request) > 2: # Dirty way to negate the requests with no data
            line = "{0},{1},{2},{3},{4},{5},{6}".format(time,src_ip,useragent,dest_ip,dest_host,request_method,request)
    	else:
    		line = "{0},{1},{2},{3},{4},{5},No request".format(time,src_ip,useragent,dest_ip,dest_host,request_method)

        alltimes.append(time)
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
        <link href="../../flask/static/bower_components/nvd3/build/nv.d3.min.css" rel="stylesheet" />
        <script src="../../flask/static/bower_components/d3/d3.min.js"></script>
        <script src="../../flask/static/bower_components/nvd3/build/nv.d3.min.js"></script>
        <script src="../../flask/static/plotly-latest.min.js"></script>
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
    writefile = open('pcapstatic/pcap_category_piechart.html','w')
    writefile.write(html_start + categorypiechart.htmlcontent)

    writefile = open('pcapstatic/pcap_category_piechart.html','a')  # Re-open for appending
    header = "<b>Time, Source IP, Destination Host, Destination IP, Request Method, Request</b><br>"
    writefile.write(header)
    #for line in gets_with_a_request:
    for line in total_entries:
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
    plot_html, plotdivid, width, height =  _plot_html(df_timeseries.iplot(asFigure=True, kind ='bar', subplots=False, shared_xaxes=True, fill=True, title='Time Series of HTTP Requests',dimensions=(800,450)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('pcapstatic/pcap_timeseries.html', 'w')
    f.write(html_bar_chart)
    f.close()

    # Gets and Posts on a timeseries:

    xtime = []
    yrequest = []
    posts_to_dst_ips = []
    gets_to_dst_ips = []
    total_dst_ips = []
    total_src_ips = []
    total_dst_hosts = []
    for item in total_entries:
        item = item.split(',')
        time = item[0]
        src_ip = item[2]
        dst_ip = item[3]
        dst_host = item[4]
        request = item[5]

        if src_ip not in total_src_ips:
            total_src_ips.append(src_ip)

        if dst_ip not in total_dst_ips:
            total_dst_ips.append(dst_ip)

        if dst_host not in total_dst_hosts:
            total_dst_hosts.append(dst_host)

        # Separate the dst_ip's based on GETS and POSTS (for a map)
        if request == 'POST':
            posts_to_dst_ips.append(dst_ip)

        if request == 'GET':
            gets_to_dst_ips.append(dst_ip)

        # Get the count of POSTS for a timeseries
        if request == 'POST':
            xtime.append(time)
            yrequest.append(1)
        else:
            xtime.append(time)
            yrequest.append(0)
        

    # Create maps of the POSTS vs GETS:
    quickmap.ip_map_world('miller-2048x1502-color.jpg',posts_to_dst_ips,'pcapstatic/posts_to_dst_ips.svg')
    quickmap.ip_map_world('miller-2048x1502-color.jpg',gets_to_dst_ips,'pcapstatic/gets_to_dst_ips.svg')


    df_timeseries = pd.DataFrame(yrequest,xtime)
    
    plot_html, plotdivid, width, height =  _plot_html(df_timeseries.iplot(asFigure=True, kind ='bar', subplots=False, shared_xaxes=True, fill=True, title='All Requests by time, showing the POSTs',dimensions=(800,450)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('pcapstatic/getsandposts_timeseries.html', 'w')
    f.write(html_bar_chart)
    f.close()

# TO DO: Check out domains with investigate
    #######################
    # STATS:

    number_of_gets = str(len(gets)) + " GET requests seen<br>"
    number_of_posts = str(len(posts)) + " POSTS seen<br>"
    stats_number_of_src_ips =  str(len(total_src_ips)) + " total Source IP addresses<br>"
    stats_number_of_dst_ips =  str(len(total_dst_ips)) + " total Destination IP addresses<br>"
    stats_number_of_dst_hosts =  str(len(total_dst_hosts)) + " total Destination Hosts<br>"


    stats = number_of_gets + number_of_posts + stats_number_of_src_ips + stats_number_of_dst_ips + stats_number_of_dst_hosts

    writefile = open('pcapstatic/stats.html','w')
    writefile.write(stats)
#    '''		
process_data()