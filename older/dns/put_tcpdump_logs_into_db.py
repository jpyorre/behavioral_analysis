# Process log file and add to mongodb

import time, sys
from tldextract import tldextract
from pymongo import MongoClient
from netaddr import valid_ipv4
from netaddr import valid_ipv6

input_file = sys.argv[1]

def put_data_into_mongodb(db_name,collection_name):
	mongo_db_host = 'localhost'
	connection = MongoClient(mongo_db_host)
	db = connection[db_name][collection_name]
	dnslogline = {}
	for line in timeanddomainslist:            
		time,domain = line.split(',')

		dnslogline = {'time':time, 'domain':domain}
		print dnslogline
	
		db.insert(dnslogline)
 
# Keep a running list of all domains seen in order to count how many time a domain is seen:
timeanddomainslist = []

# Process the input file:
with open(input_file, 'r') as f:
	for line in f:
		line = line.strip()	# get rid of extra blank lines
		linesplit = line.split(' ')	

		try:
			# Assign each column data to a variable:
			datetime = linesplit[0] + ' ' + linesplit[1]
			if len(linesplit) > 11:
				dom = linesplit[9]
				domain = tldextract.extract(dom)
				subd = domain.subdomain
				temp = ("{0}.{1}").format(subd, domain.domain) # Fix an issue where the last octet of IP's were getting removed
				temp = temp.rstrip('.,')
				
				line = ("{0},{1}".format(datetime, temp))
				print line
				timeanddomainslist.append(line)
		except:
			continue

put_data_into_mongodb('tcpdumpdns','connections')