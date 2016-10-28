from pymongo import MongoClient
from netaddr import valid_ipv4
from netaddr import valid_ipv6
from collections import Counter
import investigate
import pandas as pd
from bson import json_util
from bson.json_util import dumps
import json

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'tcpdumpdns'
COLLECTION_NAME = 'connections'
fields = {'time':True, 'domain':True, '_id':False}

def test():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=fields)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects
#test()

def process_data():

    with open('investigate_token.txt') as API_KEY:
        token = API_KEY.read()
        token = token.rstrip()

    # Database details:
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=fields)

    # Count the number of times something is seen:
    def domain_count(domain):
        count_of_domains = Counter()
        for d in unique_domains:
            t = d.split(',')[0]
            count_of_domains[d] += 1
        return(count_of_domains) 

    #############################
    # Get data from db and save results to a list
    #############################
    timeanddomain = [] # Hold the list of domains for counting
    for project in projects:
        dateandtime = project['time']
        domain = project['domain']
        line = ("{0},{1}").format(dateandtime, domain)
        timeanddomain.append(line)
    
    #############################
    # Separate IP addresses from Domains
    #############################
    temp1 = [] # Hold the domains that are not IPV4
    unique_domains = []  # Hold the domains that are not IPV4 and IPV6. domain_count(domain) will use this to count the domains
    ip = [] # Hold the IP addresses (IPV4 and IPV6)
    empty_items = 0
    for item in timeanddomain:
        item = item.split(',')[1]
#        if item == '':
#            empty_items += 1
#        continue
        if valid_ipv4(item) == True:
            ip.append(item)   
        if valid_ipv6(item) == True:
            ip.append(item)
        # This next one takes all non-ipv4 items (domains) and adds them to the temp1 list:
        if valid_ipv4(item) == False:
            temp1.append(item)
    # This one reads the temp1 list that contains both domains and ipv6 addresses and takes only the non-ipv6 entries and adds them to the unique_domains list:           
    for item in temp1:
        if valid_ipv6(item) == False:
            unique_domains.append(item)
    
    #############################
    # Count the Domains
    #############################
    count_of_domains = domain_count(unique_domains) # Count the domains and save as count_of_domains

    # Turn the count_of_domains into a dictionary
    # Used to set a threshold and view domains contacted over or under a certain number

    dictlist = []
    temp = []
    for key, value in count_of_domains.iteritems():
        temp = [key,value]
        dictlist.append(temp)

    xdata = []
    ydata = []
    for item in dictlist:
        xdata.append(item[0])
        ydata.append(item[1])

    from nvd3 import discreteBarChart
    chart = discreteBarChart(name='discreteBarChart', height=600, width=1000)

    chart.add_serie(y=ydata, x=xdata)
    chart.buildhtml()

    htmlhead = '''<!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Flask Stock Visualizer</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href={{ url_for('static', filename='./bower_components/bootstrap/dist/css/bootstrap.min.css') }} rel="stylesheet" media="screen">
        <link href={{ url_for('static', filename='main.css') }} rel="stylesheet" media="screen">
      </head>
      </head>
    <body>
        <script src={{ url_for('static', filename='./bower_components/jquery/dist/jquery.min.js') }}></script>
        <script src={{ url_for('static', filename='./bower_components/bootstrap/dist/js/bootstrap.min.js') }}></script>
        <script src={{ url_for('static', filename='./bower_components/d3/d3.min.js') }}></script>
        <script src={{ url_for('static', filename='./bower_components/nvd3/build/nv.d3.js') }}></script>
        <script src={{ url_for('static', filename='main.js') }}></script>'''

    htmltail = '''</body></html>'''

    htmloutput = htmlhead + chart.htmlcontent + htmltail

    writefile = open('templates/index.html','w')
    writefile.write(htmloutput)


    json_projects = json.dumps(count_of_domains, default=json_util.default)
    connection.close()
    # Return data to app.py
    return json_projects

process_data()
'''    
    #############################
    # Determine normal in a loose manner:
    #############################

    normal_traffic = []
    suspicious_traffic = []

    # Print domains with a certain number of visits
    for item in dictlist:
    	domain = item[0]
    	count = item[1]

    # if count is greater than or equal to a number: 
    	if count >= 2:
    		#print("{0}, {1}".format(domain,count))
    		normal_traffic.append(domain)
    		
    # if count is equal to a number: 
    	if count < 2:
    		#print("{0}, {1}".format(domain,count))
    		suspicious_traffic.append(domain)

    # if count is less than or equal to a number: 
    #	if count <= 10:
    #		print("{0}, {1}".format(domain,count))


    #################################
    # Check the suspicious traffic in
    # OpenDNS Investigate:

    wl_domains = []
    bl_domains = []
    not_determined_domains = []
    for domain in suspicious_traffic:
    	inv = investigate.Investigate(token)
    	res = inv.categorization(domain, labels=True)
    	status = res[domain]['status']
    	#print("{0}: {1}".format(domain,status))
    	if status == 0:
    		not_determined_domains.append(domain)
    	if status == 1:
    		wl_domains.append(domain)
    	if status == -1:
    		security_category = res[domain]['security_categories']
    		#domain_and_cat = str(domain) + ":" + str(security_category)
    		bl_domains.append(domain)
    		#print (domain, security_category)
    #print("\n\nWhitelisted domains:\n{0}\n".format(wl_domains))
    #print("Not determined:\n{0}\n".format(not_determined_domains))
    #if bl_domains == 0:
    #	print("No blacklisted domains")
    #else:
    #for item in bl_domains:
    #	print item
    #print("Blacklisted domains:\n{0}\n".format(bl_domains))

    #################################
    stats_emptyitems = str(empty_items) + " empty items\n"
    stats_number_of_u_domains =  str(len(unique_domains)) + " unique domains seen\n"
    stats_number_of_t_domains =  str(len(timeanddomain)) + " total domains\n"
    stats_number_of_ips =  str(len(ip)) + " total IP addresses\n"
    stats_normaltraffic = ('Normal traffic (domains visited over 3 times): {0}\n').format(len(normal_traffic))
    stats_suspicioustraffic = ('Amount of suspicious traffic domains visited under 2 times): {0}\n').format(len(suspicious_traffic))
    stats_wl = ('\nOf the suspicious domains:\nWhitelisted domains (OpenDNS): {0}\n'.format(len(wl_domains)))
    stats_bl = ('Blacklisted domains (OpenDNS): {0}\n'.format(len(bl_domains)))
    stats_neutral = ('Neutral domains (OpenDNS): {0}'.format(len(not_determined_domains)))

    stats = stats_emptyitems + stats_number_of_u_domains + stats_number_of_t_domains + stats_number_of_ips + stats_normaltraffic + stats_normaltraffic + stats_suspicioustraffic + stats_wl + stats_bl + stats_neutral


    

    #############################
    # Create Pandas dataframes for plotting and stuff
    #############################
    # timeanddomain_for_df will be used to create a pandas dataframe

    timeanddomain_for_df_temp = []
    timeanddomain_for_df = [] # This holds all domains (no IPv4 or IPv6 along with the datetime)

    for item in timeanddomain:
        item = item.split(',')
        dt = item[0]
        domain = item[1]
        line = ("{0},{1}".format(dt,domain))
        
        if domain == '':
            continue
        if valid_ipv4(domain) == False:
            timeanddomain_for_df_temp.append(line)
        
    for item in timeanddomain_for_df_temp:
        item = item.split(',')
        dt = item[0]
        domain = item[1]
        line = ("{0},{1}".format(dt,domain))
        if valid_ipv6(domain) == False:
            timeanddomain_for_df.append(line)

    x = []
    y = []
    for item in timeanddomain_for_df:
        item = item.split(',')
        x.append(item[0])
        y.append(item[1])

    # One dataframe, used for some plots:
    d = {'date':x,'domain':y}
    dftest = pd.DataFrame(data=d)
    #print dftest.head()

    # Another dataframe, used for some plots:
    df = pd.DataFrame(data=y,index=x)
    df.index = pd.to_datetime(df.index)

    #print df.head()
'''
