from pymongo import MongoClient
from netaddr import valid_ipv4
from netaddr import valid_ipv6
from collections import Counter
import investigate
import pandas as pd
from tldextract import tldextract
from bson import json_util
from bson.json_util import dumps
import json
from nvd3 import discreteBarChart, pieChart

# Plotly:
'''from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from plotly.offline.offline import _plot_html
import cufflinks as cf
import plotly.graph_objs as go'''

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'tcpdumpdns'
#COLLECTION_NAME = 'connections'
COLLECTION_NAME = '2000'
fields = {'time':True, 'domain':True, '_id':False}

def process_data():
    # Database details:
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=fields)

    # Count the number of times a domain is seen:
    def count_domains(listofitems):
        listofitems = Counter()
        for d in unique_domains:
            t = d.split(',')[0]
            listofitems[d] += 1
        return(listofitems) 

    # Count the number of times a time occurs is seen:
    def count_times(listofitems):
        listofitems = Counter()
        for d in all_times:
            t = d.split(',')[0]
            listofitems[d] += 1
        return(listofitems) 

    #############################
    # Get data from db and save results to a list
    #############################
    timeanddomain = [] # Hold the list of domains for counting
    for project in projects:
        dateandtime = project['time']
        domain = project['domain']
        line = ("{0},{1}").format(dateandtime, domain)
        timeanddomain.append(line)
    
    '''   # Save the time of domain hits
       all_times = []  # Hold the times
       for item in timeanddomain:
           print item
           time = item.split(',')[0]
           all_times.append(time)'''
    #############################
    # Separate IP addresses from Domains
    #############################
    temp1 = [] # Hold the domains that are not IPV4
    unique_domains = []  # Hold the domains that are not IPV4 and IPV6. domain_count(domain) will use this to count the domains
    ip = [] # Hold the IP addresses (IPV4 and IPV6)
    empty_items = 0
    for item in timeanddomain:
        domain = item.split(',')[1]
        if valid_ipv4(domain) == True:
            ip.append(domain)   
        if valid_ipv6(domain) == True:
            ip.append(domain)
        # This next one takes all non-ipv4 items (domains) and adds them to the temp1 list:
        if valid_ipv4(domain) == False:
            temp1.append(domain)
    # This one reads the temp1 list that contains both domains and ipv6 addresses and takes only the non-ipv6 entries and adds them to the unique_domains list:           
    for domain in temp1:
        if valid_ipv6(domain) == False:
            unique_domains.append(domain)

    count_of_domains = count_domains(unique_domains) # Count the domains and save as count_of_domains
    #count_of_times = count_times(all_times) # Count the domains and save as count_of_domains

    # Turn the count_of_domains into a dictionary
    # Used to set a threshold and view domains contacted over or under a certain number
    domainslist = []
    temp = []
    for key, value in count_of_domains.iteritems():
        temp = [key,value]
        domainslist.append(temp)

    '''   timeslist = []
       temp = []
       for key, value in count_of_times.iteritems():
           temp = [key,value]
           timeslist.append(temp)'''
    
    #############################
    # Determine normal in a loose manner:
    #############################

    normal_traffic = []
    suspicious_traffic = []

    # Print domains with a certain number of visits
    for item in domainslist:
    	domain = item[0]
    	count = item[1]

    # if count is greater than or equal to a number: 
    	if count >= 2:
    		#print("{0}, {1}".format(domain,count))
    		normal_traffic.append(item)
    		
    # if count is equal to a number: 
    	if count < 5:
    		#print("{0}, {1}".format(domain,count))
    		suspicious_traffic.append(item)

    # if count is less than or equal to a number: 
    #	if count <= 10:
    #		print("{0}, {1}".format(domain,count))

    ######################################################
    # Take the suspicious domains and unique them, getting them ready to look at using third party tools:
    domain_counts = [] # firstlevel.tld, count
    domain_fullrequest_counts = [] # actual request, firstlevel.tld, count

    temp = [] # Temporary holder to unique the firstlevel.tld, as used below
    for line in suspicious_traffic:
        fulldomain = line[0]
        dom = tldextract.extract(fulldomain)

        if dom.suffix != '':

            domain = dom.domain + '.' + dom.suffix  # Just the first level domain
            # Create a newline, which has the firstlevel domain, the full domain with subdomains and the count
            domain_fullrequest_count = "{0},{1},{2}".format(domain,fulldomain,line[1])

            if  domain in temp:
                continue
            else:
                domain_count = "{0},{1}".format(domain,line[1])
                domain_counts.append(domain_count)
                domain_fullrequest_counts.append(domain_fullrequest_count)
            temp.append(domain) # Unique the domains

    #####################################
    # For a chart of suspicious domains:
    xsuspicious = []
    ysuspicious = []
    for item in domain_counts:
        item = item.split(',')
        xsuspicious.append(item[0]) # Domains
        ysuspicious.append(item[1]) # Count

    ### Domain visit Barchart:
    suspiciousbarchart = discreteBarChart(name='discreteBarChart', height=600, width=1000)
    suspiciousbarchart.add_serie(y=ysuspicious, x=xsuspicious)
    suspiciousbarchart.buildhtml()

    writefile = open('templates/suspicious_domains.html','w')
    writefile.write(suspiciousbarchart.htmlcontent)


#TO DO: Look at odd domains with NLP to find DGA's, Have a whitelist of domains, such as paypal.com and look through domains, using NLP to find anomolies and comparing the ASN
    #################################
    # Check the suspicious traffic in
    # OpenDNS Investigate:
    token = ()
    with open('investigate_token.txt') as API_KEY:
        token = API_KEY.read()
        token = token.rstrip()

    inv = investigate.Investigate(token)
    
    wl_domains = []
    bl_domains = []
    not_determined_domains = []
    for line in domain_fullrequest_counts:
        line = line.split(',')
        domain = line[0]
        domain_fullrequest_count = "{0},{1},{2}".format(line[0],line[1],line[2])
        
        res = inv.categorization(domain, labels=True)
        status = res[domain]['status']
    
        #print("{0}: {1}".format(domain,status))
        if status == 0:
            not_determined_domains.append(domain_fullrequest_count)
        if status == 1:
            wl_domains.append(domain_fullrequest_count)
        if status == -1:
            #security_category = res[line]['security_categories']
            #domain_and_cat = str(domain) + ":" + str(security_category)
            bl_domains.append(domain_fullrequest_count)
            #print (domain, security_category)

    #####################################
    # CHART GENERATION
    #####################################
    # Time visit Barchart:
    '''xtimedata = []
    ytimedata = []
    for item in timeanddomain:
        item = item.split(',')   
        xtimedata.append(item[0])
        ytimedata.append(item[1])

    timebarchart = discreteBarChart(name='discreteBarChart', height=600, width=1000)
                timebarchart.add_serie(y=ytimedata, x=xtimedata)
                timebarchart.buildhtml()
    timebarchart = discreteBarChart(name='discreteBarChart', height=600, width=1000)
    timebarchart.add_serie(y=df['date'], x=df['counts'])
    #timebarchart.add_serie(y=df.index.values, x=df['domain'])
    timebarchart.buildhtml()

    writefile = open('templates/timebar.html','w')
    writefile.write(timebarchart.htmlcontent)'''

    #####################################
    #alldomains Barchart:
    xdomaindata = []
    ydomaindata = []
    for item in domainslist:
        xdomaindata.append(item[0])
        ydomaindata.append(item[1])

    alldomains = discreteBarChart(name='discreteBarChart', height=300, width=1000)
    alldomains.add_serie(y=ydomaindata, x=xdomaindata)
    alldomains.buildhtml()
    writefile = open('templates/alldomains.html','w')
    writefile.write(alldomains.htmlcontent)

    #####################################
    # For a chart of blacklisted domains:
    xblacklisted = []
    yblacklisted = []
    for item in bl_domains:
        item = item.split(',')
        xblacklisted.append(item[0]) # Domains
        yblacklisted.append(item[2]) # Count

    ### Blacklisted Barchart:
    blacklistedbarchart = discreteBarChart(name='discreteBarChart', height=300, width=600)
    blacklistedbarchart.add_serie(y=yblacklisted, x=xblacklisted)
    blacklistedbarchart.buildhtml()
    writefile = open('templates/blacklisted_domains.html','w')
    writefile.write(blacklistedbarchart.htmlcontent)

    #####################################
    # For a chart of whitelisted domains:
    xwhitelisted = []
    ywhitelisted = []
    for item in wl_domains:
        item = item.split(',')
        xwhitelisted.append(item[0]) # Domains
        ywhitelisted.append(item[2]) # Count

    ### Blacklisted Barchart:
    whitelistedbarchart = discreteBarChart(name='discreteBarChart', height=300, width=600)
    whitelistedbarchart.add_serie(y=ywhitelisted, x=xwhitelisted)
    whitelistedbarchart.buildhtml()
    writefile = open('templates/whitelisted_domains.html','w')
    writefile.write(whitelistedbarchart.htmlcontent)

    #####################################
    # For a chart of neutral listed domains:
    xneutrallisted = []
    yneutrallisted = []
    for item in not_determined_domains:
        item = item.split(',')
        xneutrallisted.append(item[0]) # Domains
        yneutrallisted.append(item[2]) # Count

    ### neutral listed Barchart:
    neutrallistedbarchart = discreteBarChart(name='discreteBarChart', height=300, width=600)
    neutrallistedbarchart.add_serie(y=yneutrallisted, x=xneutrallisted)
    neutrallistedbarchart.buildhtml()
    writefile = open('templates/neutral_domains.html','w')
    writefile.write(neutrallistedbarchart.htmlcontent)

    #print("\n\nWhitelisted domains:\n{0}\n".format(wl_domains))
    #print("Not determined:\n{0}\n".format(not_determined_domains))
    #if bl_domains == []:
    #    print("No blacklisted domains")
    #else:
    #for item in bl_domains:
    #    print item
        #print("Blacklisted domains:\n{0}\n".format(bl_domains))

    #################################
    stats_number_of_u_domains =  str(len(unique_domains)) + " unique domains seen<br>"
    stats_number_of_t_domains =  str(len(timeanddomain)) + " total domains<br>"
    stats_number_of_ips =  str(len(ip)) + " total IP addresses<br>"
    stats_normaltraffic = ('Normal traffic (domains visited over 3 times): {0}<br>').format(len(normal_traffic))
    stats_suspicioustraffic = ('Amount of suspicious traffic domains visited under 2 times): {0}<br>').format(len(suspicious_traffic))
    stats_wl = ('<br>Of the suspicious domains (uniqued):<br>Whitelisted domains (OpenDNS): {0}<br>'.format(len(wl_domains)))
    stats_bl = ('Blacklisted domains (OpenDNS): {0}<br>'.format(len(bl_domains)))
    stats_neutral = ('Neutral domains (OpenDNS): {0}'.format(len(not_determined_domains)))

    stats = stats_number_of_u_domains + stats_number_of_t_domains + stats_number_of_ips + stats_normaltraffic + stats_suspicioustraffic + stats_wl + stats_bl + stats_neutral

    writefile = open('templates/stats.html','w')
    writefile.write(stats)

    # Flask wants something returned:
    json_projects = json.dumps(count_of_domains, default=json_util.default)
    connection.close()
    # Return data to app.py
    return json_projects
    
'''

    # This one's for plotly:
    xtime = []
    ytime = []
    for item in timeanddomain:
        item = item.split(',')
        xtime.append(item[0])
        ytime.append(item[1])

    d = {'date':xtimedata,'domain':ytimedata}
    df = pd.DataFrame(data=d)
    df['counts'] = df.groupby('domain').transform('count')
    
    # For plotly:
    #df2 = pd.DataFrame(data=ytime,index=xtime)
    #df2.index = pd.to_datetime(df2.index)
    #############################
    # HTML for plotly plots:
    #############################
    html_start = """<html>
    <head>
      <script src="../static/plotly-latest.min.js"></script>
    </head>
    <body>"""

    html_end = """
    </body>
    </html>"""

     # Line plot:
    plot_html, plotdivid, width, height =  _plot_html(df2.iplot(asFigure=True, kind ='scatter', subplots=True, shared_xaxes=True, fill=True, title='Count by day',dimensions=(800,800)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('templates/plottest_scatter.html', 'w')
    f.write(html_bar_chart)
    f.close()

    df_suspicious = pd.DataFrame(ysuspicious, xsuspicious)
    #print df_suspicious.head()
    # Line plot:
    plot_html, plotdivid, width, height =  _plot_html(df_suspicious.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='Suspicious Traffic',dimensions=(800,800)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('templates/plotly_suspicious.html', 'w')
    f.write(html_bar_chart)
    f.close()
    
    # Bar chart of domain counts per day:
    # Line plot:
    #plot_html, plotdivid, width, height =  _plot_html(dftest.iplot(asFigure=True, kind = 'line', subplots=False, shared_xaxes=True, fill=True, title='Count by day',dimensions=(800,800)), False, "", True, '100%', 525, False)
    #html_bar_chart = html_start + plot_html + html_end
    #f = open('templates/plottest.html', 'w')
    #f.write(html_bar_chart)
    #f.close()

    # End plotly chart generation

    
'''
#process_data()
    
'''
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
