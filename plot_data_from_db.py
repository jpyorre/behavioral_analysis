from pymongo import MongoClient
from netaddr import valid_ipv4
from netaddr import valid_ipv6
from collections import Counter
import investigate
import pandas as pd
import plotly.plotly as py
import plotly.offline as py
import plotly.graph_objs as go
from plotly.offline.offline import _plot_html
from plotly.offline import download_plotlyjs, iplot

mongodb_host = 'localhost'
mongodb_port = 27017
dbs_name = 'tcpdumpdns'
collection_name = 'connections'
connection = MongoClient(mongodb_host,mongodb_port)
collection = connection[dbs_name][collection_name]
fields = {'time':True, 'domain':True, '_id':False}

with open('investigate_token.txt') as API_KEY:
    token = API_KEY.read()
    token = token.rstrip()

#############################
# FUNCTIONS
#############################
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

projects = collection.find(projection=fields)
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
    if item == '':
        empty_items += 1
	continue
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
print('\n')
print str(empty_items) + " empty items"
print str(len(unique_domains)) + " unique domains seen"
print str(len(timeanddomain)) + " total domains"
print str(len(ip)) + " total IP addresses"
print('Normal traffic (domains visited over 3 times): {0}').format(len(normal_traffic))
print('Amount of suspicious traffic domains visited under 2 times): {0}').format(len(suspicious_traffic))
print('\nOf the suspicious domains:')
print('Whitelisted domains (OpenDNS): {0}'.format(len(wl_domains)))
print('Blacklisted domains (OpenDNS): {0}'.format(len(bl_domains)))
print('Neutral domains (OpenDNS): {0}'.format(len(not_determined_domains)))

#############################
# Create Pandas dataframes for plotting and stuff
#############################
# timeanddomain_for_df will be used to create a pandas dataframe

#domains_by_count = domain_count(timeanddomain)
#print domains_by_count

dx = [] # Store time values for domains
dy = [] # Store domain values for domains
ix = [] # Store time values for IP addresses
iy = [] # Store IP addresses
domains = [] # temp place to store domains and time as we parse through the timeanddomain list
ips = [] # temp place to store ips and time as we parse through the timeanddomain list

# Parse through time and domain, separate IP's from domains and add to the right lists.
for item in timeanddomain:
	line = item.split(',')
	if line[1] == '':
		continue
	if valid_ipv4(line[1]) == False:
		domains.append(item)
	if valid_ipv6(line[1]) == False:
		domains.append(item)
	
        if valid_ipv4(line[1]) == True:
                ips.append(item)
        if valid_ipv6(line[1]) == True:
                ips.append(item)

# Put IP addresses in 'iy' and the time in 'ix':
for item in ips:
        line = item.split(',')
        ix.append(line[0])
        iy.append(line[1])
	
# Put domains in 'dy' and the time in 'dx':
for item in domains:
	line = item.split(',')
	dx.append(line[0])
	dy.append(line[1])

# Create a Pandas dataframe for the domains and their times:
domain_df = pd.DataFrame(data=dy, index=dx)
domain_df.index = pd.to_datetime(domain_df.index)
#print domain_df.head()


# Create a Pandas dataframe for the IP's and their times:
# IP's in a dataframe:
#ip_df = pd.DataFrame(data=iy, index=ix)
#ip_df.index = pd.to_datetime(ip_df.index)
#print ip_df.head()

# Create a count of domains by day:
count_by_day = domain_df.groupby(domain_df.index.date).count()

total_requests_plot, plotdivid, width, height = _plot_html(count_by_day.iplot(asFigure=True, kind='bar', title='Requests',dimensions=(1200,600)), False, "", True, '100%', 525, False)
