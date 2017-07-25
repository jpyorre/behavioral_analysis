import datetime, sys
from pymongo import MongoClient

all_data = 'processed/all_domains.txt'
domains_in_top_1m = 'processed/domains_in_top_1m.txt'
domains_not_in_top_1m = 'processed/domains_not_in_top_1m.txt'
vt_data = 'processed/vt_inv_results.txt'

def insert_into_mongo(logline, collection):
    mongo_db_host = 'localhost'
    connection = MongoClient(mongo_db_host)
    db = connection['dns'][collection]
    db.insert(logline, collection)

def insert_all_data():
    with open(all_data,'r') as data: # Process the input file
        for line in data:
            ls = line.split('|')
            dt = datetime.datetime.strptime(ls[0], '%Y-%m-%d %H:%M:%S')
            domain,ip,asn,lat,lon,inv,category = ls[1],ls[2],ls[3],ls[4],ls[5],ls[6],ls[7]
            logline = {'time':dt, 'domain':domain, 'ip':ip, 'asn':asn, 'lat':lat, 'lon':lon, 'inv':inv,'category':category}
            print "Inserting into all_data: {}".format(domain)
            insert_into_mongo(logline, 'all_data')

def insert_domains_in_top_1m():
    with open(domains_in_top_1m,'r') as data: # Process the input file
        for line in data:
            ls = line.split('|')
            dt = datetime.datetime.strptime(ls[0], '%Y-%m-%d %H:%M:%S')
            domain,ip,asn,lat,lon,inv,category = ls[1],ls[2],ls[3],ls[4],ls[5],ls[6],ls[7]
            logline = {'time':dt, 'domain':domain, 'ip':ip, 'asn':asn, 'lat':lat, 'lon':lon, 'inv':inv,'category':category}
            print "Inserting into domains_in_top_1m: {}".format(domain)
            insert_into_mongo(logline, 'domains_in_top_1m')

def insert_domains_not_in_top_1m():
    with open(domains_not_in_top_1m,'r') as data: # Process the input file
        for line in data:
            ls = line.split('|')
            dt = datetime.datetime.strptime(ls[0], '%Y-%m-%d %H:%M:%S')
            domain,ip,asn,lat,lon,inv,category = ls[1],ls[2],ls[3],ls[4],ls[5],ls[6],ls[7]
            logline = {'time':dt, 'domain':domain, 'ip':ip, 'asn':asn, 'lat':lat, 'lon':lon, 'inv':inv,'category':category}
            print "Inserting into domains_not_in_top_1m: {}".format(domain)
            insert_into_mongo(logline, 'domains_not_in_top_1m')

def insert_vt_data():
    with open(vt_data,'r') as data: # Process the input file
        for line in data:
            ls = line.split('|')

            dt = datetime.datetime.strptime(ls[0], '%Y-%m-%d %H:%M:%S')
            domain,ip,asn,lat,lon,inv,category,reputation,urls,subs = ls[1],ls[2],ls[3],ls[4],ls[5],ls[6],ls[7],ls[8],ls[9],ls[10].rstrip('\n')
            logline = {'time':dt, 'domain':domain, 'ip':ip, 'asn':asn, 'lat':lat, 'lon':lon, 'inv':inv,'category':category,'reputation':reputation,'urls':urls,'subdomains':subs}
            print "Inserting into vt_data: {}".format(domain)
            insert_into_mongo(logline, 'vt_data')


def insert_test_data():
    with open('t.txt','r') as data: # Process the input file
        for line in data:
            ls = line.split('|')
            dt = datetime.datetime.strptime(ls[0], '%Y-%m-%d %H:%M:%S')
            domain,ip,asn,lat,lon,inv,category = ls[1],ls[2],ls[3],ls[4],ls[5],ls[6],ls[7]
            logline = {'time':dt, 'domain':domain, 'ip':ip, 'asn':asn, 'lat':lat, 'lon':lon, 'inv':inv,'category':category}
            print "Inserting into testdata: {}".format(domain)
            insert_into_mongo(logline, 'testdata')

# insert_test_data()        
insert_all_data()
insert_domains_in_top_1m()
insert_domains_not_in_top_1m()
insert_vt_data()
