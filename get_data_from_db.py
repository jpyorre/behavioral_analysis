from pymongo import MongoClient

mongodb_host = 'localhost'
mongodb_port = 27017
dbs_name = 'tcpdumpdns'
collection_name = 'connections'
connection = MongoClient(mongodb_host,mongodb_port)
collection = connection[dbs_name][collection_name]
fields = {'time':True, 'domain':True, '_id':False}

domainslist = [] # Hold the list of domains for counting

projects = collection.find(projection=fields)
for project in projects:
	dateandtime = project['time']
	#dt = datetime.datetime.strptime(dateandtime, "%Y-%m-%d %H:%M:%S")
	domain = project['domain']
	line = ("{0},{1}").format(dateandtime, domain)
        print line
	domainslist.append(line)
