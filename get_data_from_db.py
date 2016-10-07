from pymongo import MongoClient
from netaddr import valid_ipv4
from netaddr import valid_ipv6
from collections import Counter
import pandas as pd

mongodb_host = 'localhost'
mongodb_port = 27017
dbs_name = 'tcpdumpdns'
collection_name = 'connections'
connection = MongoClient(mongodb_host,mongodb_port)
collection = connection[dbs_name][collection_name]
fields = {'time':True, 'domain':True, '_id':False}

#############################
# FUNCTIONS
#############################
# Count the number of times something is seen:
def domain_count(domain):
    count_of_domains = Counter()
    for d in temp2:
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
	#dt = datetime.datetime.strptime(dateandtime, "%Y-%m-%d %H:%M:%S")
	domain = project['domain']
	line = ("{0},{1}").format(dateandtime, domain)
        #print line
	timeanddomain.append(line)

#############################
# Separate IP addresses from Domains
#############################
temp1 = [] # Hold the domains that are not IPV4
temp2 = []  # Hold the domains that are not IPV4 and IPV6. domain_count(domain) will use this to count the domains
ip = []
for item in timeanddomain:
    item = item.split(',')[1]
    if item == '':
        continue
    if valid_ipv4(item) == True:
        ip.append(item)   
    if valid_ipv6(item) == True:
        ip.append(item)
    if valid_ipv4(item) == False:
        temp1.append(item)
           
for item in temp1:
    if valid_ipv6(item) == False:
        temp2.append(item)

#############################
# Count the Domains
#############################
count_of_domains = domain_count(temp2) # Count the domains and save as count_of_domains

# Turn the count_of_domains into a dictionary
# Used to set a threshold and view domains contacted over or under a certain number

dictlist = []
temp = []
for key, value in count_of_domains.iteritems():
    temp = [key,value]
    dictlist.append(temp)

#############################
# More data work to create a pandas dataframe
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

print df.head()
















