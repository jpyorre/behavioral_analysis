import sys, datetime, os
from collections import Counter
from netaddr import valid_ipv4
from tldextract import tldextract
import datetime, json
infile = sys.argv[1]
html_outfile = 'client_ip_metrics.html'
domains_outfile = 'domains.txt'
metrics_js_outfile = '../assets/js/custom/client_connections_metrics_custom.js'

# This takes a log file that looks like this (originally from some infoblox logs):
# 2017-01-18T11:21:44-05:00 daemon ibprodcache5 named[16648]: info client 10.237.110.21#30429 (affiliates.mgmmirage.com): query: affiliates.mgmmirage.com IN A +EDC (10.208.240.15)
#
# It takes each client IP and maps all the connections, showing the bandwidth over a timeline
#
# It writes the following files:
# json files to ./data/clientip.json
# custom metrics_graphics.js in ../assets/js/custom/client_connections_metrics_custom.js
# client_ip_metrics.html to display results
#
# Run like this:
# python client_connections.py inputfile.log
# When done, open the client_ip_metrics.html
# Warning, with large log files, it may be super slow when opening in a browser
# There are some additional options at the bottom for writing different kinds of json files, but they're commented out at the moment.

resolution_lines = [] # List for all the lines from the log file
clients = [] # Unique client list, which we'll use to assign datetime and domain visited to the individual clients

def write_file(line, filename):
    f = open(filename, 'a')
    f.write(line)
    # f.write('\n')
    f.close()

if os.path.isfile(html_outfile): 
       os.remove(html_outfile)
if os.path.isfile(metrics_js_outfile):
       os.remove(metrics_js_outfile)

metrics_js_text_1 = '''d3.json("data/'''   
metrics_js_text_2 = '''", function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "'''
metrics_js_text_3 ='''",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById("'''
metrics_js_text_4 ='''_client_connection_times"),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });
  '''

html_head = '''
<!DOCTYPE html>
<head>
        <title>Client Bandwidth Metrics</title>
    <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
    <link href="../assets/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href='../assets/css/metricsgraphics.css' rel='stylesheet' type='text/css'>
    <script src="../assets/js/d3.v4.min.js" charset="utf-8"></script>
    <script src='../assets/js/MG.js'></script>
    <script src='../assets/js/misc/utility.js'></script>
    <script src='../assets/js/common/data_graphic.js'></script>
    <script src='../assets/js/common/hooks.js'></script>
    <script src='../assets/js/common/register.js'></script>
    <script src='../assets/js/common/scales.js'></script>
    <script src='../assets/js/common/chart_title.js'></script>
    <script src='../assets/js/common/y_axis.js'></script>
    <script src='../assets/js/common/x_axis.js'></script>
    <script src='../assets/js/common/init.js'></script>
    <script src='../assets/js/common/markers.js'></script>
    <script src='../assets/js/common/rollover.js'></script>
    <script src='../assets/js/common/window_listeners.js'></script>
    <script src='../assets/js/charts/line.js'></script>
    <script src='../assets/js/charts/histogram.js'></script>
    <script src='../assets/js/charts/point.js'></script>
    <script src='../assets/js/charts/bar.js'></script>
    <script src='../assets/js/charts/table.js'></script>
    <script src='../assets/js/charts/missing.js'></script>
    <script src='../assets/js/misc/process.js'></script>
    <script src='../assets/js/misc/smoothers.js'></script>
    <script src='../assets/js/misc/formatters.js'></script>
    <script src='../assets/js/misc/transitions.js'></script>
    <script src='../assets/js/misc/error.js'></script>    
    <script src="../assets/js/custom/client_connections_metrics_custom.js"></script>
<body>'''
html_end = '''
</body>
</html>
'''
write_file(html_head, html_outfile)

def count_stuff(listofitems):
    listofitems_counted = Counter()
    for d in listofitems:
        listofitems_counted[d] += 1
    return(listofitems_counted) 
    
with open(infile, 'r') as f:
    for line in f:
        line = line.strip()	# Make sure each line is a newline
        s = line.split(' ')	# Split items by space character, creating a list (see next 3 lines for list items)
        try:
            _dateandtime = s[0] # dateandtime, currently a string. Will convert to datetime object later
            _dateandtime = _dateandtime.rstrip('05:00').rstrip('-')
            dateandtime = datetime.datetime.strptime(_dateandtime, "%Y-%m-%dT%H:%M:%S")
            client = s[6].split('#')[0]	# The client portion from these logs is like this:  10.237.110.21#3856. Split by the # character and then grab the first item in the new list, the client IP
            domain = s[7].strip('(').rstrip(':').rstrip(')') # The domain called out to from these logs is like this: (pages.returnpath.com). Strip the '(' and the ')' as well as the ':'
            if valid_ipv4(client):	#make sure we have a valid IP version 4 IP address (removes garbage text)
        		resolution_line = "{},{},{}".format(dateandtime, client, domain)	# Save it all as a line to work with further on
        		resolution_lines.append(resolution_line)	# add each line to the resolution_lines list to work with further on
        		if client not in clients:	# Make a unique client list, which we'll use to assign datetime and domain visited to the individual clients
        			clients.append(client)
        except:
        	continue
       
temp_array = []
list_items = []
html_mids = []
all_domains = []

for client_ip in clients:
    all_times = []
    item = {'client':client_ip,'date_and_domain':[], 'domain_count':''}    # Create dict with list to hold the date and time of domain visit together
    temp_array.append(item) # Add list item for each client IP

for i in temp_array:    # for each client IP in list
    domain_count = 0    # Count number of domains in list
    times = []
    l = []
    for r in resolution_lines:  # for each line in resolution_lines
        # test = []
        r = r.split(',')    # Split each line in resolution_lines to make a list (see next line)
        rdate,rclient,rdomain = r[0],r[1],r[2]

        # get unique domains:
        tld_domain = tldextract.extract(rdomain)
        topleveldomain ="{0}.{1}".format(tld_domain.domain, tld_domain.suffix)
        if topleveldomain not in all_domains:
            all_domains.append(topleveldomain)

        if i['client'] == rclient:  # if the client we're looking at is equal to the client in the line from the resolution_lines list
            times.append(rdate)
            domain_count += 1 # Count number of domains in list
            rdate_rdomain = {'date':rdate,'domain':rdomain}  # Create a dict to tie the date and domain from resolution_line together for analysis
            i['date_and_domain'].append(rdate_rdomain)   # Append rdate_rdomain to each individual client line in the date_and_domain list in: item = {'client':client_ip,'date_and_domain':[]}
        i['domain_count'] = domain_count
    count_of_times = count_stuff(times)
    print "Finished working on: " + i['client']#, count_of_times

    for key, value in count_of_times.iteritems():
        z = {'value':value,'date':str(key)} # Create Dataframe
        all_times.append(z)
    
    list_items.append(i)
    # print i['client'], all_times
    json.dump(all_times, open('data/' + i['client'] +'.json','w'))

    metrics_js_text = metrics_js_text_1 + i['client'] + '.json' + metrics_js_text_2 + i['client'] + metrics_js_text_3 + i['client'] + metrics_js_text_4
    write_file(metrics_js_text,metrics_js_outfile)

    html_div = "<div id=\"" + i['client'] + '_client_connection_times' +"\"></div>"
    write_file(html_div, html_outfile)

write_file(html_end, html_outfile)

if os.path.isfile(domains_outfile): 
       os.remove(domains_outfile)

for i in all_domains:
    write_file(i+'\n',domains_outfile)
# Write everything to one json file:
# json.dump(temp_array, open('../assets/data/client_connections.json','w'))
    
# Write to files named after each client IP address:
# for i in list_items:
#     filename = i['client'] + '.json'
#     if os.path.isfile(filename):    # Remove files so new stuff isn't appended to old files during testing or whatever (this doesn't have to be done with the json.dump above because that creates a new file each time)
#        os.remove(filename)
#     write_file(str(i), filename)