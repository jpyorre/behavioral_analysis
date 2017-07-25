import datetime, time, random
from collections import Counter
import dateutil.parser
from flask import Flask
from flask import render_template
import pandas as pd
from pymongo import MongoClient
import json, gmplot
from bson import json_util
from bson.json_util import dumps
from flask import Blueprint
import csv
import folium
import unicodedata

app = Flask(__name__)

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'dns'
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)

times,domains,ips,labels,values,categories = [],[],[],[],[],[]

#collection = connection[DBS_NAME][COLLECTION_NAME]
FIELDS = {'time':True, 'domain':True, 'ip':True, 'inv':True, 'asn':True, 'lat':True,'lon':True, 'category':True,'reputation':True,'urls':True,'subdomains':True,'_id':False}
# data = collection.find(projection=FIELDS)

# for line in data:
#     dt,domain,ip,inv_security_category,category,reputation,urls,subs,lat,lon,asn = line['time'], line['domain'], line['ip'], line['inv'], line['category'], line['reputation'], line['urls'], line['subdomains'], line['lat'], line['lon'], line['asn']
#     times.append(dt)
#     domains.append(domain)
#     ips.append(ip)
#     categories.append(category)
# return data

# def make_map(data,outfile):
#     latlon = []
#     for line in data:
#         dt, domain, category, lat, lon = line['time'], line['domain'], line['category'], line['lat'], line['lon']
#         if lat == "0":
#             continue
#         else:
#             latlon.append({'lat':lat,'lon':lon})
#     with open('static/data/'+ outfile, 'w') as o:
#         json.dump(latlon, o)

def make_map(collection,outfile):
    collection = connection[DBS_NAME][collection]
    data = collection.find(projection=FIELDS)
    domains,lats,lons,invs = [],[],[],[]
    for line in data:
        domain,lat,lon,inv = line['domain'], line['lat'], line['lon'], line['inv']
        print lat
        if lat == None:
            continue
        if lat == "None":
            continue
        if float(lat) == 0.0000:
            continue
        else:
            domains.append(domain)
            lats.append(float(lat))
            lons.append(float(lon))
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

    fg=folium.FeatureGroup(name=collection)
    for lat,lon,domain,inv in zip(df['lat'],df['lon'],df['domain'],df['inv']):
        outline,fill = color(inv) # colors
        fg.add_child(folium.Marker(location=[lat,lon],popup=(folium.Popup(domain)),icon=folium.Icon(color=fill,icon_color='green')))
        # fg.add_child(folium.CircleMarker(location=[lat,lon],popup=(domain),radius=3, color=outline, fill_color=fill))
    map_osm.add_child(fg)
    map_osm.save(outfile)

# def make_map_google(data,outfile):
#     lats, lons = [],[]
#     for line in data:
#         dt, domain, category, lat, lon = line['time'], line['domain'], line['category'], line['lat'], line['lon']
#         if lat == "0":
#             continue
#         else:
#             try:
#                 lats.append(float(lat))
#                 lons.append(float(lon))
#             except:
#                 continue
#     gmap = gmplot.GoogleMapPlotter(lats[0], lons[0], 4)
#     gmap.heatmap(lats, lons)
#     # gmap.draw('static/data/' + outfile)
#     gmap.draw('templates/' + outfile)

def count_items(listofitems):
    listofitems_counted = Counter()
    for d in listofitems:
        listofitems_counted[d] += 1
    return(listofitems_counted)

def ts_investigate_sec_categories(collection,outfile):
    collection = connection[DBS_NAME][collection]
    data = collection.find(projection=FIELDS)
    l = []
    for line in data:
        # dt, inv_security_category = line['time'], line['inv']
        dt, inv_security_category, domain = line['time'], line['inv'], line['domain']
        if inv_security_category == '-1':
            item = {'value':inv_security_category,'v':'bad','date':str(dt),'z':domain}
        if inv_security_category == '1':
            item = {'value':inv_security_category,'v':'good','date':str(dt),'z':domain}
        if inv_security_category == '0':
            item = {'value':inv_security_category,'v':'neutral','date':str(dt),'z':domain}
        l.append(item)
    json.dump(l, open(outfile,'w'))

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
        z = {'value':value,'date':str(key)} # Create Dataframe
        l.append(z)
    json.dump(l, open(outfile,'w'))

def make_multiline_metrics_list(collection):
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

def make_multiline_metrics_json(outfile):
    multiline_list = []
    all_data_l = make_multiline_metrics_list('all_data')
    multiline_list.append(all_data_l)
    domains_in_top_1m_l = make_multiline_metrics_list('domains_in_top_1m')
    multiline_list.append(domains_in_top_1m_l)
    domains_not_in_top_1m_l = make_multiline_metrics_list('domains_not_in_top_1m')
    multiline_list.append(domains_not_in_top_1m_l)
    json.dump(multiline_list, open(outfile,'w'))
########################
# create_charts_json() calls make_coords(), which uses listes made in make_lists_for_coords()
def make_coords(workinglist):
    x = []
    y = []
    count_of_stuff = count_items(workinglist) #Count the number items from list sent to function
    for key, value in count_of_stuff.iteritems():
        x.append(key)
        y.append(value)
        # print key,value
    return x,y

def create_charts_json(listofstuff,outfile,randomcolors): # For the charts.js stuff (called in category_info())
    x,y = make_coords(listofstuff)
    if randomcolors == False:
    # Make new colors for each field:
        colors = []
        for i in x:
            r = lambda: random.randint(0,255)
            color = ('#%02X%02X%02X' % (r(),r(),r()))
            colors.append(color)
    else:
        colors = randomcolors
    json_out = { 'data': {
                    'labels': x,
                    'datasets': [ {
                        'data' : y,
                        'backgroundColor': colors,
                         'hoverBackgroundColor': colors,
                        'fill': True
                    } ] }
        }
    json.dump(json_out, open(outfile,'w'))

def create_category_tree(collection,outfile): # Create a json for D3 Tree Layout from a list of two items
    collection = connection[DBS_NAME][collection]
    data = collection.find(projection=FIELDS)
    cats_domains = []
    for line in data:
        domain,category,ip,asn = line['domain'], line['category'], line['ip'], line['asn']
        cat_domain = "{},{}".format(category,domain)
        cats_domains.append(cat_domain)
    c_list = []
    parent = []
    parents = []
    children = []
    for i in cats_domains:
        item = i.split(',')
        c,d = item[0], item[1]
        if c in c_list:
            continue
        else:
            c_list.append(c)
            p_line = {"name": c,"parent": "categories","children": []}
            parents.append(p_line)
    level1 = []
    _parent = {"name": "categories","parent": "null","children": []}
    for parentsdata in parents:
        temp = []
        for item in cats_domains:
            item = item.split(',')
            c,d = item[0], item[1]
            if c in parentsdata['name']:
                child = {"name": d,"parent": c}
                parentsdata['children'].append(child)
        level1.append(parentsdata)
        _parent['children'].append(parentsdata)
    parent.append(_parent)
    json.dump(parent, open(outfile,'w'))

def asn_list_to_tree(collection, outfile): # Create a tree of ASN to IP to Domain
    collection = connection[DBS_NAME][collection]
    data = collection.find(projection=FIELDS)
    asns_ips_domains = []
    for line in data:
        asn,ip,domain = line['asn'], line['ip'], line['domain']
        asn_ip_domain = "{},{},{}".format(asn,ip,domain)
        asns_ips_domains.append(asn_ip_domain)

    _domainlist, _iplist, _asnlist = [],[],[] # Hold things to avoid duplicates
    domainchildren, ipchildren, asnchildren = [],[],[] # Hold the child data in the tree
    root = [] # Container list for everything
    for i in asns_ips_domains:
        item = i.split(',')
        domain,ip,asn = item[0], item[1], item[2]
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
    json.dump(root, open(outfile,'w'))

def gen_cat_json(collection,outfile): # json for categories on categories page:
    collection = connection[DBS_NAME][collection]
    data = collection.find(projection=FIELDS)
    cat = []
    for line in data:
        cat.append(line['category'])
    create_charts_json(cat,outfile,False)
########################
@app.route("/categories")
def category_info():
    gen_cat_json('all_data','static/data/categories_all_data.json')
    gen_cat_json('domains_in_top_1m','static/data/categories_domains_in_top_1m.json')
    gen_cat_json('domains_not_in_top_1m','static/data/categories_domains_not_in_top_1m.json')
    return render_template('category_info.html')

@app.route("/")
def index():
    make_metrics_json('all_data','static/data/ts_all.json') # Create json for All Domains chart (specified in templates/metrics.html and static/js/ba.js)
    make_metrics_json('domains_in_top_1m','static/data/ts_domains_in_top_1m.json') # Create json for domains_in_top_1m chart (specified in templates/metrics.html and static/js/ba.js)
    make_metrics_json('domains_not_in_top_1m','static/data/ts_domains_not_in_top_1m.json') # Create json for domains_not_in_top_1m chart (specified in templates/metrics.html and static/js/ba.js)
    make_multiline_metrics_json('static/data/all_domains_multiline.json') # Create json for All Domains, (multiline chart specified in templates/metrics.html and static/js/ba.js)
    ts_investigate_sec_categories('all_data','static/data/ts_all_investigate_security_category.json')
    ts_investigate_sec_categories('domains_in_top_1m','static/data/ts_domains_in_top_1m_investigate_security_category.json') 
    ts_investigate_sec_categories('domains_not_in_top_1m','static/data/ts_domains_not_in_top_1m_investigate_security_category.json') 

    # json for investigate security categories on metrics page:
    collection = connection[DBS_NAME]['all_data']
    data = collection.find(projection=FIELDS)
    inv_sec = []
    for line in data:
        inv_sec.append(line['inv'])
    static_colors = ["backgroundColor:","#336633","#FF0033","#666666"]
    create_charts_json(inv_sec,'static/data/inv_sec_categories.json',static_colors)
    return render_template('metrics.html')

@app.route("/forcegraph_domain_to_asn")
def forcegraph_domain_to_asn():
    # function to generate forcegraph goes here
    return render_template('forcegraph_domain_to_asn.html')

@app.route("/categories_tree_top")
def categories_tree_top():
    create_category_tree('domains_in_top_1m','static/data/category_tree_domains_in_top_1m.json')
    return render_template('category_tree_domains_in_top_1m.html')

@app.route("/categories_tree_not_top")
def categories_tree_not_top():
    create_category_tree('domains_not_in_top_1m','static/data/category_tree_domains_not_in_top_1m.json')
    return render_template('category_tree_domains_not_in_top_1m.html')

@app.route("/asn_tree_top")
def asn_tree_top():
    asn_list_to_tree('domains_in_top_1m','static/data/domain_ip_asn_tree_domains_in_top_1m.json')
    return render_template('domain_ip_asn_circular_tree_domains_in_top_1m.html')

@app.route("/asn_tree_not_top")
def asn_tree_not_top():
    asn_list_to_tree('domains_not_in_top_1m','static/data/domain_ip_asn_tree_domains_not_in_top_1m.json')
    return render_template('domain_ip_asn_circular_tree_domains_not_in_top_1m.html')


def alldata():
    collection = connection[DBS_NAME]['all_data']
    data = collection.find(projection=FIELDS)
    connection.close()
    return render_template('alldata.html', data = data)

@app.route("/all")
def alldata():
    collection = connection[DBS_NAME]['all_data']
    data = collection.find(projection=FIELDS)
    connection.close()
    return render_template('alldata.html', data = data)

@app.route("/vt_data")
def vtdata():
    collection = connection[DBS_NAME]['vt_data']
    data = collection.find(projection=FIELDS)
    connection.close()
    return render_template('vt_data.html', data = data)

# @app.route("/map")
# def alltraffic_map():
#     collection = connection[DBS_NAME]['all_data']
#     data = collection.find(projection=FIELDS)
#     make_map(data,'alltraffic_map.json')
#     connection.close()
#     return render_template('map.html', data = data)

############## MAP GENERATION ##################################################
# @app.route("/map_all") # Generate map for domains not in top 1m
# def map_all():
#     # comment back in if you want to generate maps every time you reload
#     make_map('all_data','mapdata/data_domains_all_map.html') 
#     return render_template('map_all_domains_template.html')

@app.route("/map_domains_in_top_1m") # Generate map for domains not in top 1m
def map_domains_in_top_1m():
    # comment back in if you want to generate maps every time you reload
    # make_map('domains_in_top_1m','static/data/data_domains_in_top_1m_map.html') 
    return render_template('map_domains_in_top_1m_template.html')

@app.route("/map_domains_not_in_top_1m") # Generate map for domains not in top 1m
def map_domains_not_in_top_1m():
    # comment back in if you want to generate maps every time you reload
    # make_map('domains_not_in_top_1m','static/data/data_domains_not_in_top_1m_map.html') 
    return render_template('map_domains_not_in_top_1m_template.html')

############## END MAP GENERATION ###############################################

# @app.route("/templates/gmap.html")
# def gmap_data_endpoint():
#     return render_template('gmap.html')

@app.route("/domains_not_in_top_1m")
def domains_not_in_top_1m():
    collection = connection[DBS_NAME]['domains_not_in_top_1m']
    data = collection.find(projection=FIELDS)
    connection.close()
    return render_template('domains_not_in_top_1m.html', data = data)

# @app.route("/domains_not_in_top_1m/map")
# def domains_not_in_top_1m_map():
#     collection = connection[DBS_NAME]['domains_not_in_top_1m']
#     data = collection.find(projection=FIELDS)
#     make_map(data,'domains_not_in_top_1m_map.json')
#     connection.close()
#     return render_template('domains_not_in_top_1m_map.html', data = data)

@app.route("/domains_not_in_top_1m/map")
def domains_not_in_top_1m_map():
    collection = connection[DBS_NAME]['domains_not_in_top_1m']
    data = collection.find(projection=FIELDS)
    make_map(data,'gdomains_not_in_top_1m_map.html')
    connection.close()
    return render_template('gdomains_not_in_top_1m_map.html', data = data)

@app.route("/domains_in_top_1m")
def domains_in_top_1m():
    collection = connection[DBS_NAME]['domains_in_top_1m']
    data = collection.find(projection=FIELDS)
    connection.close()
    return render_template('domains_in_top_1m.html', data = data)

@app.route("/domains_in_top_1m/map")
def domains_in_top_1m_map():
    collection = connection[DBS_NAME]['domains_in_top_1m']
    data = collection.find(projection=FIELDS)
    make_map(data,'domains_in_top_1m.json')
    connection.close()
    return render_template('domains_in_top_1m_map.html', data = data)

@app.route("/bar")
def bar():
    count_of_stuff = count_items(categories) #Count the number items from list sent to function
    for key, value in count_of_stuff.iteritems():
        labels.append(key)
        values.append(value)
    connection.close()
    return render_template('chart.html', values=values, labels=labels)

@app.route("/line")
def line():
    count_of_stuff = count_items(times) #Count the number items from list sent to function
    for key, value in count_of_stuff.iteritems():
        labels.append(key)
        values.append(value)
    connection.close()
    return render_template('line.html', values=values, labels=labels)

@app.route("/pie")
def pie():
    colors = []
    count_of_stuff = count_items(categories) #Count the number items from list sent to function
    for key, value in count_of_stuff.iteritems():
        labels.append(key)
        values.append(value)
        colors.append('#F7464A')
        print key,value
    connection.close()
    return render_template('pie.html', set=zip(values, labels, colors))

if __name__ == "__main__":
	#app.run()
    #app.run(host='0.0.0.0',port=5000,debug=True)
    app.run(host='127.0.0.1',port=5000,debug=True)

