# Process log file and add to mongodb

import datetime, sys, dpkt
from tldextract import tldextract
from pymongo import MongoClient
from netaddr import valid_ipv4
from netaddr import valid_ipv6
import socket

input_file = sys.argv[1]

f = open(input_file)
pcap = dpkt.pcap.Reader(f)

def put_data_into_mongodb(db_name,collection_name,data):
	mongo_db_host = 'localhost'
	connection = MongoClient(mongo_db_host)
	db = connection[db_name][collection_name]

	pcaplogline = {}
	for line in data:       
		time,src_ip,useragent,dest_host,dest_ip,request_method,request = line.split(',')
		pcaplogline = {'time':time, 'src_ip':src_ip, 'useragent':useragent, 'dest_host':dest_host, 'dest_ip':dest_ip, 'request_method':request_method, 'request':request}
		print pcaplogline
		db.insert(pcaplogline)
 
# Keep a running list of all domains seen in order to count how many time a domain is seen:
timeanddomainslist = []

# Process the input file:

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
			timeanddomainslist.append(data)

	except:
		continue

put_data_into_mongodb('pcap','http',timeanddomainslist)
