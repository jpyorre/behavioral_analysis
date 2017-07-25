# This script is used for testing pulling from the mongodb and creating files. I use it to get things right for the Flask app

import datetime, sys, time, json
from collections import Counter
from pymongo import MongoClient
import pandas as pd
import whois, dns.resolver, pyasn, json, requests, itertools
import networkx as nx
from networkx.readwrite import json_graph
from pprint import pprint as pp
from nvd3 import cumulativeLineChart, pieChart, lineChart, discreteBarChart, scatterChart, multiBarChart
from netaddr import valid_ipv4

from influxdb import InfluxDBClient # probably won't use
from influxdb import DataFrameClient # probably won't use

# Plotly:
from plotly.offline import download_plotlyjs, iplot
from plotly.offline.offline import _plot_html
import cufflinks as cf
import plotly.graph_objs as go

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'dns'
#COLLECTION_NAME = 'subdomains_not_in_top_1m'
FIELDS = {'time':True, 'domain':True, 'ip':True, 'inv':True, 'asn':True, 'lat':True,'lon':True, 'category':True,'reputation':True,'urls':True,'subdomains':True,'_id':False}
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
#collection = connection[DBS_NAME][COLLECTION_NAME]
#data = collection.find(projection=FIELDS)

times,domains,ips,labels,values,categories,security_categories, timeandcategory, domains_times, domains_cats, timeandsecuritycategory, domains_securitycategory, domains_ip_asn, cats_domains, domain_locations, domain_locations_inv_status = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]

def send_to_influx(df,database):
    host='localhost'
    port=8086
    user = 'root'
    password = 'root'
    dbname = database
    showdbs = 'show series'
    #client = InfluxDBClient(host, port, user, password, dbname)
    client = DataFrameClient(host, port, user, password, dbname)
    # Create DB's
    # client.create_database('all_data')
    # client.create_database('domains_in_top_1m')
    # client.create_database('domains_not_in_top_1m')
    client.write_points(df, 'dns') # Write dataframe
    #client.query("use march1; select * from demo") # Read dataframe

# Count the number of times something is seen:
def count_items(listofitems):
    listofitems_counted = Counter()
    for d in listofitems:
        listofitems_counted[d] += 1
    return(listofitems_counted)

def make_df(workinglist):
    x = []
    y = []
    count_of_stuff = count_items(workinglist) #Count the number items from list sent to function
    for key, value in count_of_stuff.iteritems():
        x.append(key)
        y.append(value)
    df = pd.DataFrame({'count':y,'time':x}) # Create Dataframe
    df = df.set_index('time')
    return df

def process_data_mongo(collectionname):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][collectionname]
    data = collection.find(projection=FIELDS)
    names = []
    for line in data:
        dt,domain,ip,inv_security_category,category,lat,lon,asn = line['time'], line['domain'], line['ip'], line['inv'], line['category'], line['lat'], line['lon'], line['asn']
        times.append(dt)
        domains.append(domain)
        ips.append(ip)
        categories.append(category)
        security_categories.append(inv_security_category)
        time_cat = "{},{}".format(dt,category)#,domain)
        domain_cat = "{},{}".format(domain,category)
        cat_domain = "{},{}".format(category,domain)
        time_sec_cat = "{},{}".format(dt,inv_security_category)
        domain_time = "{},{}".format(dt,domain)
        domain_ip_asn = "{},{},{}".format(domain, ip, asn)
        domain_securitycategory = "{},{}".format(domain,inv_security_category)
        domain_location = "{},{},{}".format(domain, lat, lon)
        domain_location_inv = "{},{},{},{}".format(domain, lat, lon, inv_security_category)
        timeandsecuritycategory.append(time_sec_cat)
        timeandcategory.append(time_cat)
        domains_cats.append(domain_cat)
        cats_domains.append(cat_domain)
        domains_times.append(domain_time)
        domains_ip_asn.append(domain_ip_asn)
        domains_securitycategory.append(domain_securitycategory)
        domain_locations.append(domain_location)
        domain_locations_inv_status.append(domain_location_inv)


        #print dt,domain,ip,inv_security_category,category,lat,lon,asn

    #     #################
    #     # Separate data into day chunks:
    #     #################
    #     day = str(dt.day)
    #     month = str(dt.month)
    #     monthcount = 1
    #     while monthcount <= 12:      
    #         if month == str(monthcount):
    #             # This will write files by month:
    #             # filename = ("{}.txt".format(month))
    #             # l = "{}{}".format(dt,domain)
    #             # write(filename,l)
                
    #             daycount = 1
    #             while daycount <= 31:
    #                 tc =[]
    #                 if day == str(daycount):
    #                     name = ("{}-{}".format(month, day))
    #                     filename = ("{}.txt".format(name))
    #                     #print time_cat
    #                     write(filename,time_cat)
    #                     names.append(filename)
    #                 daycount +=1
    #         monthcount +=1
    # # Go through each day and creat plots
    # count = 0
    # while count < len(names):   

    #     with open('test/'+ names[count],'r') as data:
    #         listofthings = []
    #         for eachline in data:
    #             eachline = eachline.strip()
    #             listofthings.append(eachline)                
    #             count +=1

    #         # instead of printing it, send the list to make a plotly plot
    #         filename = listofthings[0].split(',')[0].split(' ')[0]
    #         df = df_count_domains_with_time(listofthings)
    #         plotly_ts(df,filename,filename +'.html')
#################

def write(filename, line):
    writefile = open('test/' + filename,'a')
    writefile.write(line)
    writefile.write('\n')
    writefile.close()

def plotly_ts(df, title, filename):
    _htmlhead = open('plotly_ts_head.html','r')
    htmlhead = _htmlhead.read()

    _htmltail = open('plotly_ts_tail.html','r')
    htmltail = _htmltail.read()

    plot_html, plotdivid, width, height =  _plot_html(df.iplot(asFigure=True, kind ='bar', subplots=False, shared_xaxes=True, fill=True, title=title,dimensions=(800,450)), False, "", True, '100%', 525, False)
    html_bar_chart = htmlhead + plot_html + htmltail
    f = open('plotly/' + filename, 'w')
    f.write(html_bar_chart)
    f.close()

def chop(date):
    return date.split(".")[0] # lookup per second
    #return date[:-6] #lookup for every hour
    #return date[:-9] #lookup for every day
    #return date[:-12] #lookup for every month

def chop_seconds(workinglist):
    date_dom = map(lambda x: x.split(","), workinglist)
    date_dom = map(lambda (dat,dom): (chop(dat), dom), date_dom)
    return map(lambda x: ",".join(x), date_dom)

def df_count_domains_with_time(workinglist):
    date_dom = chop_seconds(workinglist) #chops off the seconds
    count_of_stuff = count_items(date_dom) #count the number of item pairs

    datedom_cnt = count_of_stuff.iteritems() #counts: date:domain => count 
    date_dom_cnt = map(lambda (key, cnt): # Splitting into (date, domain, count)
        (key.split(",")[0],
         key.split(",")[1], 
         cnt), 
        datedom_cnt)
    lookup = {} #create a lookup table: {date : {domains: cnt}}
    for dat, dom, cnt in date_dom_cnt:
        if dat in lookup:
            lookup[dat][dom] = cnt
        else:
            lookup[dat] = {dom: cnt}
    dates = list(set(map(lambda (dat, dom, cnt): dat, date_dom_cnt))) #just get the unique dates
    domains = list(set(map(lambda (dat, dom, cnt): dom, date_dom_cnt))) #just get the unique domains

    payload = [0]*len(domains) #iterate and construct a matrix
    for i, date in enumerate(dates):
        for j, domain in enumerate(domains):
            if i == 0:
                if domain in lookup[date]:
                    payload[j] = [lookup[date][domain]]
                else:
                    payload[j] = [0]
            else:
                if domain in lookup[date]:
                    #print "here", domain, date, lookup[date][domain], payload[j]
                    payload[j].append(lookup[date][domain])
                else:
                    payload[j].extend([0])
    payload = dict(zip(domains, payload))
    df = pd.DataFrame(payload, index=dates)
    return df

def c3_pie_chart(filename,chartname,scoring_list):
    _htmlhead = open('flask/ba/ba/static/build/c3_piechart_head.html','r')
    htmlhead = _htmlhead.read()
    _htmlmid = open('flask/ba/ba/static/build/c3_piechart_middle.html','r')
    htmlmid = _htmlmid.read()
    _htmltail = open('flask/ba/ba/static/build/c3_piechart_tail.html','r')
    htmltail = _htmltail.read()
    out_filename = str(filename) + "_piechart.html"
    htmlout = "{0}{1}{2}{3}{4}".format(htmlhead,chartname,htmlmid,scoring_list,htmltail)
    writefile = open(out_filename,'w')
    writefile.write(htmlout)

def category_piecharts(collection): 
    count_of_categories = count_items(categories) # A count of domains by category
    category_list,temp = [],[]
    for key, value in count_of_categories.iteritems(): # Turn the count_of_categories into a dictionary
        temp = [str(key),value]
        category_list.append(temp)
    c3_pie_chart("flask/ba/ba/static/data/content_categories_" + collection,"Content Categories", category_list) # Creat pie chart of categories
    
    wl, bl, neutral = 0,0,0
    whitelisted,blacklisted,neutral_list = [],[],[]
    sec_list = []
    for item in security_categories:
        item = str(item)
        if item == "0":
            neutral += 1
        if item == "-1":
            bl += 1
        if item == "1":
            wl +=1
    whitelisted.append('Whitelisted')
    whitelisted.append(wl)
    blacklisted.append('Blacklisted')
    blacklisted.append(bl)
    neutral_list.append('Neutral')
    neutral_list.append(neutral)
    sec_list.append(whitelisted)
    sec_list.append(blacklisted)
    sec_list.append(neutral_list)
    print sec_list
    c3_pie_chart("flask/ba/ba/static/data/security_categories_" + collection,"Security Categories", sec_list) # Creat pie chart of security categories

def make_metrics_json(collection,outfile):
    collection = connection[DBS_NAME][collection]
    data = collection.find(projection=FIELDS)
    l = []
    times = []
    for line in data:
        dt,domain,ip,inv_security_category,category,lat,lon,asn = line['time'], line['domain'], line['ip'], line['inv'], line['category'], line['lat'], line['lon'], line['asn']
        times.append(dt)
    count_of_stuff = count_items(times) #Count the number items from list sent to function
    for key, value in count_of_stuff.iteritems():
        z = {'count':value,'time':str(key)} # Create Dataframe
        l.append(z)
    json.dump(l, open(outfile,'w'))

def make_multiline_metrics_json(collection):
    collection = connection[DBS_NAME][collection]
    data = collection.find(projection=FIELDS)
    l = []
    times = []
    for line in data:
        dt,domain,ip,inv_security_category,category,lat,lon,asn = line['time'], line['domain'], line['ip'], line['inv'], line['category'], line['lat'], line['lon'], line['asn']
        times.append(dt)
    count_of_stuff = count_items(times) #Count the number items from list sent to function
    for key, value in count_of_stuff.iteritems():
        z = {'value':value,'date':str(key)} # Create Dataframe
        l.append(z)
    return l

def ts_investigate_sec_categories():
    l = []
    for i in timeandsecuritycategory:
        i = i.split(',')
        dt = i[0]
        sec = i[1]
        if sec == '-1':
            item = {'bad':sec,'date':str(dt)}
        if sec == '1':
            item = {'good':sec,'date':str(dt)}
        if sec == '0':
            item = {'neutral':sec,'date':str(dt)}
        l.append(item)
    json.dump(l, open('ts_investigate_security_category.json','w'))



def draw_force_graph(G,filename):
    for n in G:
        G.node[n]['name'] = n
    d = json_graph.node_link_data(G)
    json.dump(d, open(filename,'w'))

def force_graph_setup(incominglist, filename):
    G=nx.Graph()
    for item in incominglist:
        item = item.split(',')
        if len(item) == 2:
            item1, item2 = item[0], item[1]
            G.add_node(item1)
            G.add_node(item2)
            G.add_edge(item1,item2)
        if len(item) == 3:
            item1, item2, item3 = item[0], item[1], item[2]
            G.add_node(item1)
            G.add_node(item2)
            G.add_node(item3)
            G.add_edge(item1,item2)
            G.add_edge(item2,item3)
    draw_force_graph(G,filename)


def create_category_tree(): # Create a json for D3 Tree Layout from a list of two items
    domain_list = []
    asn_list = []
    parent = []
    parents = []
    children = []
    for item in domains_ip_asn:
        item = item.split(',')
        domain,ip,asn = item[0], item[1], item[2]
        if domain in domain_list:
            continue
        else:
            domain_list.append(domain)
            p_line = {"name": asn,"parent": "ASN","children": []} # ASN as a child of ASN
            # ip_line = {"name": ip,"parent": asn,"children": []} # IP as a child of ASN
            # domain_line = {"name": domain,"parent": ip,"children": []} # Domain as a child of IP
            # ip_line['children'].append(domain_line)
            # p_line['children'].append(ip_line) # Add IP as a child of ASN
            parents.append(p_line)
            # print p_line
    level1 = []
    _parent = {"name": "ASN","parent": "null","children": []}

    for parentsdata in parents:
        # print parentsdata
        temp = []
        for item in domains_ip_asn:
            item = item.split(',')
            domain,ip,asn = item[0], item[1], item[2]
            if asn in parentsdata['name']:
                # child = {"name": domain,"parent": asn}
                ip_line = {"name": ip,"parent": asn,"children": []} # IP as a child of ASN
                domain_line = {"name": domain,"parent": ip,"children": []} # Domain as a child of IP
                ip_line['children'].append(domain_line)
                parentsdata['children'].append(ip_line)
        level1.append(parentsdata)
        _parent['children'].append(parentsdata)
    parent.append(_parent)
    print parent
    json.dump(parent, open('treewithd3/domain_ip_asn_tree_domains_not_in_top_1m.json','w'))


def asn_list_to_tree(outfile):
    _domainlist, _iplist, _asnlist = [],[],[] # Hold things to avoid duplicates
    domainchildren, ipchildren, asnchildren = [],[],[] # Hold the child data in the tree
    root = [] # Container list for everything
    for i in domains_ip_asn:
        item = i.split(',')
        domain,ip,asn = item[0], item[1], item[2]
        print asn
        asnline = {"name":asn,"parent":"asn","children":[]}
        ipline = {"name":ip,"parent":asn,"children":[]}
        domainline = {"name":domain,"parent":ip}

        if domain not in _domainlist: # Build a dict containing all the domainline's
            domainchildren.append(domainline)
            _domainlist.append(domain)

        if ip not in _iplist: # Build a dict containing all the ipline's
            _iplist.append(ip)
            ipchildren.append(ipline)

        if asn not in _asnlist: # Build a dict containing all the asnline's
            _asnlist.append(asn)
            asnchildren.append(asnline)

    ip_parentlist = [] # Container list for IP Parent
    for i_item in ipchildren: # Locking the domains to their IP's
        for d_item in domainchildren:
            if d_item['parent'] == i_item['name']:
                i_item['children'].append(d_item)
                ip_parentlist.append(i_item)

    asn_parentlist = [] # Container list for ASN parent
    for a_item in asnchildren: # Locking the IP to their ASN's
        for i_item in ipchildren:
            if i_item['parent'] == a_item['name']:
                a_item['children'].append(i_item)
                asn_parentlist.append(a_item)
        
    parentline = {"name":"asn","parent":"null","children":[]} # Create the parentline
    _parent = parentline # Assign the parentline (has to be done this way..I forget why it worked)
    _parent['children'] = asn_parentlist # Assign the asn_parentlist (which contains the other lists)
    root.append(_parent) # Put all the lists into the root container
    # json.dump(root, open(outfile,'w'))

# process_data_mongo('domains_not_in_top_1m')
process_data_mongo('testdata')
# asn_list_to_tree(domains_ip_asn, 'treewithd3/domain_ip_asn_tree.json')

def get_asn_location():
    from geopy.geocoders import Nominatim
    geolocator = Nominatim()

    import geoip2.database
    geoip2_reader = geoip2.database.Reader("../assets/build/GeoLite2-City.mmdb")
    
    # latitude, longitude = geodata.location.latitude, geodata.location.longitude
    na = []
    eu = []
    asia = []
    africa = []
    aus = []
    atlantic = []
    for ip in ips:
        if valid_ipv4(ip):
            try:
                geodata = geoip2_reader.city(ip) # get lat and lon
                tz = geodata.location.time_zone
                tz = tz.split('/')
                country = str(tz[0])
                city = str(tz[1])
                
                if country == 'America':
                    america.append(country)
                if country == 'Europe':
                    eu.append(country)
                if country == 'Asia':
                    asia.append(country)
                if country == 'Africa':
                    africa.append(country)
                if country == 'Australia':
                    aus.append(country)
                if country == 'Atlantic':
                    atlantic.append(country)
                # else:
                #     print country
            except:
                continue
    print atlantic
    # for i in domain_locations:
    #     item = i.split(',')
    #     d = item[0]
    #     lat = item[1]
    #     lon = item[2]
    #     if lat == '0':
    #         # print ("None: {},{},{}".format(d,lat,lon))
    #         continue
    #     else:
    #         location = geolocator.reverse(lat+','+lon)
    #         # print ("{},{},{}:{}".format(d,lat,lon,location.address))
    #         print d, location

def folium_map():
    import folium
    domains,lats,lons,invs = [],[],[],[]
    for item in domain_locations_inv_status:
        item = item.split(',')
        domain,lat,lon,inv = item[0], float(item[1]), float(item[2]),item[3]
        if lat == 0.0000:
            continue
        else:
            domains.append(domain)
            lats.append(lat)
            lons.append(lon)
            invs.append(inv)
    df = pd.DataFrame({'domain':domains,'lat':lats, 'lon':lons, 'inv':invs})
    map_osm=folium.Map(location=[df['lat'].mean(),df['lon'].mean()],zoom_start=2)#,tiles='Stamen Toner')

    def color(inv_status):
        if inv_status == str(1):
            outline = 'black'
            fillcolor='green'
        if inv_status == str(0):
            outline = 'black'
            fillcolor='white'
        if inv_status == str(-1):
            outline = 'black'
            fillcolor='red'
        return outline,fillcolor

    fg=folium.FeatureGroup(name="Domains Visited")
    for lat,lon,domain,inv in zip(df['lat'],df['lon'],df['domain'],df['inv']):
        outline,fill = color(inv) # colors
        fg.add_child(folium.Marker(location=[lat,lon],popup=(folium.Popup(domain)),icon=folium.Icon(color=fill,icon_color='green')))
        # fg.add_child(folium.CircleMarker(location=[lat,lon],popup=(domain),radius=3, color=outline, fill_color=fill))
    map_osm.add_child(fg)
    map_osm.save(outfile='map.html')

folium_map()
# create_category_tree()

#process_data_mongo('domains_not_in_top_1m')
# force_graph_setup(domains_cats,'flask/ba/ba/static/data/force_graph_categories.json')  # Domains to categories
# force_graph_setup(domains_times,'flask/ba/ba/static/data/force_graph_times.json')  # Time series to domains
# force_graph_setup(domains_ip_asn,'flask/ba/ba/static/data/force_graph_domain_ip_asn.json')  # Domain to IP to ASN
# force_graph_setup(domains_securitycategory,'flask/ba/ba/static/data/force_graph_domains_securitycategory.json')  # Domain to Security Category

# def build_tree(category_data):
#   top_level_map = {}
#   cat_map = {}
#   for cat_name, domain in category_data:
#     cat_map.setdefault(domain, {})
#     cat_map.setdefault(cat_name, {})
#     cat_map[domain][cat_name] = cat_map[cat_name]
#     # if depth == 0:
#     #   top_level_map[cat_name] = cat_map[cat_name]

#   return cat_map

# listofthings = []
# for i in cats_domains:
#     item = i.split(',')
#     listofthings.append(item)
#     print item

# data = build_tree(listofthings)
# json.dump(data, open('data_tree_test.json','w'))

# data = []
# for i in cats_domains:
#     item = i.split(',')
#     # t = tuple(item)
#     # data.append(t)
#     print(item[0] +','+item[1])
# json.dump(data, open('data_tree_test.json','w'))

# root = data[0][0]
# for parent, child in data:    
#     node2children = {parent: []} 
#     childnode = {child: []}
#     children = node2children[parent]
#     children.append(childnode)
#     node2children[child] = childnode[child]

# jsonstr = json.dumps({root: node2children[root]}, indent=4)
# print jsonstr

# ################################
# # Create a json for D3 Tree Layout from a list of two items
# ################################
# c_list = []
# parent = []
# parents = []
# children = []
# for i in cats_domains:
#     item = i.split(',')
#     c,d = item[0], item[1]
#     if c in c_list:
#         continue
#     else:
#         c_list.append(c)
#         p_line = {"name": c,"parent": "categories","children": []}
#         parents.append(p_line)
# level1 = []
# _parent = {"name": "categories","parent": "null","children": []}
# for parentsdata in parents:
#     temp = []
#     for item in cats_domains:
#         item = item.split(',')
#         c,d = item[0], item[1]
#         if c in parentsdata['name']:
#             child = {"name": d,"parent": c}
#             parentsdata['children'].append(child)
#     level1.append(parentsdata)
#     _parent['children'].append(parentsdata)
# parent.append(_parent)
# json.dump(parent, open('treewithd3/domains_not_in_top_1m.json','w'))




# for item in domains_cats:
#     item = item.split(',')
#     item1, item2 = item[0], item[1]
#     print item
#     G.add_node(item1)
#     G.add_node(item2)
# draw_force_graph(G,filename)


        #G.add_edge(item1,item2)
    #draw_force_graph(G,filename)

#tree_categories(domains_cats,'flask/ba/ba/static/data/tree_categories.json')


# metrics_graphics()


# Do these one at a time or the lists fill up over and over again, messing up the data
# process_data_mongo('all_data')
# category_piecharts('all_data')

# process_data_mongo('domains_in_top_1m')
# category_piecharts('domains_in_top_1m')

# process_data_mongo('domains_not_in_top_1m')
# category_piecharts('domains_not_in_top_1m')




###############
# For influx db:

# send_to_influx('none','none') # Just used when creating db's

# process_data_mongo('all_data')
# bandwidth = make_df(times)
# send_to_influx(bandwidth, 'all_data' )

# process_data_mongo('domains_in_top_1m')
# bandwidth = make_df(times)
# send_to_influx(bandwidth, 'domains_in_top_1m' )

# process_data_mongo('domains_not_in_top_1m')
# bandwidth = make_df(times)
#send_to_influx(bandwidth, 'domains_not_in_top_1m' )
######################

# Plotly:
#df = df_count_domains_with_time(timeandcategory)
#plotly_ts(df,'domains_not_in_top_1m','domains_not_in_top_1m_ts.html')