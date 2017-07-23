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
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from plotly.offline.offline import _plot_html
import cufflinks as cf
import plotly.graph_objs as go

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'tcpdumpdns'
COLLECTION_NAME = 'connections'
#COLLECTION_NAME = '2000'
fields = {'time':True, 'domain':True, '_id':False}

def process_data():
    # Database details:
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=fields)

    # Count the number of times a something is seen:
    def count_stuff(listofitems):
        listofitems_counted = Counter()
        for d in listofitems:
            t = d.split(',')[0]
            listofitems_counted[d] += 1
        return(listofitems_counted) 

    # Get data from db and save results to a list
    #############################
    timeanddomain = [] # Hold the list of domains for counting
    for project in projects:
        dateandtime = project['time']
        domain = project['domain']
        line = ("{0},{1}").format(dateandtime, domain)
        timeanddomain.append(line)
    
    # Save the time of domain hits
    all_times = []  # Hold the times
    for item in timeanddomain:
       #print item
       time = item.split(',')[0]
       all_times.append(time)
    
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

    count_of_domains = count_stuff(unique_domains) # Count the domains and save as count_of_domains
    count_of_times = count_stuff(all_times) # Count the domains and save as count_of_domains

    # Turn the count_of_domains into a dictionary
    # Used to set a threshold and view domains contacted over or under a certain number
    domainslist = []
    temp = []
    for key, value in count_of_domains.iteritems():
        temp = [key,value]
        domainslist.append(temp)

    timeslist = []
    temp = []
    for key, value in count_of_times.iteritems():
       temp = [key,value]
       timeslist.append(temp)
    
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

    #################################
    # Check the suspicious traffic in
    # OpenDNS Investigate:
    token = ()
    with open('investigate_token.txt') as API_KEY:
        token = API_KEY.read()
        token = token.rstrip()

    inv = investigate.Investigate(token)

    categories_list = []
    security_categories_list = []
    wl_domains = []
    bl_domains = []
    not_determined_domains = []
    for line in domain_fullrequest_counts:
        line = line.split(',')
        domain = line[0]
        domain_fullrequest_count = "{0},{1},{2}".format(line[0],line[1],line[2])
        
        res = inv.categorization(domain, labels=True)
        status = res[domain]['status']
    
        if status == 0:
            # Get domain categorization and add it to categories_list
            content_category = res[domain]['content_categories']
            if content_category == []:
                continue
            else:
                for value in content_category:
                    categories_list.append(value)
            ##############
            not_determined_domains.append(domain_fullrequest_count)

        if status == 1:
            # Get domain categorization and add it to categories_list
            content_category = res[domain]['content_categories']
            if content_category == []:
                continue
            else:
                for value in content_category:
                    categories_list.append(value)

            ##############
            wl_domains.append(domain_fullrequest_count)
            #print domain_fullrequest_count

        if status == -1:
            bl_domains.append(domain_fullrequest_count)
            security_category = res[domain]['security_categories']
            if security_category == []:
                continue
            else:
                for value in security_category:
                    security_categories_list.append(value)
                    categories_list.append(value)

            # Get domain categorization and add it to categories_list
            content_category = res[domain]['content_categories']
            if content_category == []:
                continue
            else:
                for value in content_category:
                    categories_list.append(value)
            ##############
            #domain_and_cat = str(domain) + ":" + str(security_category)
            

            #print (domain, security_category)

    count_of_categories = count_stuff(categories_list) # Count the categories and save as count_of_categories
    
    # Turn the count_of_categories into a dictionary
    category_list = []
    temp = []
    for key, value in count_of_categories.iteritems():
        temp = [key,value]
        category_list.append(temp)

    count_of_security_categories = count_stuff(security_categories_list) # Count the categories and save as count_of_security_categories
    # Turn the count_of_security_categories into a dictionary
    security_category_list = []
    temp = []
    for key, value in count_of_security_categories.iteritems():
        temp = [key,value]
        security_category_list.append(temp)
    #print security_categories_list
    #####################################
    # CHART GENERATION
    #####################################
    # Time visit Barchart:
    xtimedata = []
    ytimedata = []
    for item in timeanddomain:
        item = item.split(',')   
        xtimedata.append(item[0])
        ytimedata.append(item[1])
    '''
    timebarchart = discreteBarChart(name='discreteBarChart', height=600, width=1000)
                timebarchart.add_serie(y=ytimedata, x=xtimedata)
                timebarchart.buildhtml()
    timebarchart = discreteBarChart(name='discreteBarChart', height=600, width=1000)
    timebarchart.add_serie(y=df['date'], x=df['counts'])
    #timebarchart.add_serie(y=df.index.values, x=df['domain'])
    timebarchart.buildhtml()

    writefile = open('../flask/templates/timebar.html','w')
    writefile.write(timebarchart.htmlcontent)'''

    #####################################
    #alldomains Barchart:
    xdomaindata = []
    ydomaindata = []
    for item in domainslist:
        xdomaindata.append(item[0])
        ydomaindata.append(item[1])

    ### Plotly does this better. All domains visit Barchart:
    '''alldomains = discreteBarChart(name='discreteBarChart', height=300, width=1000)
                alldomains.add_serie(y=ydomaindata, x=xdomaindata)
                alldomains.buildhtml()
                writefile = open('../flask/templates/alldomains.html','w')
                writefile.write(alldomains.htmlcontent)'''

    #####################################
    # For a chart of suspicious domains:
    xsuspicious = []
    ysuspicious = []
    for item in domain_counts:
        item = item.split(',')
        xsuspicious.append(item[0]) # Domains
        ysuspicious.append(item[1]) # Count

    ### Plotly does this better. suspicious visit Barchart:
    '''suspiciousbarchart = discreteBarChart(name='discreteBarChart', height=600, width=1000)
                suspiciousbarchart.add_serie(y=ysuspicious, x=xsuspicious)
                suspiciousbarchart.buildhtml()
            
                writefile = open('../flask/templates/suspicious_domains.html','w')
                writefile.write(suspiciousbarchart.htmlcontent)'''

    #####################################
    # For a chart of blacklisted domains:
    xblacklisted = []
    yblacklisted = []
    for item in bl_domains:
        item = item.split(',')
        xblacklisted.append(item[0]) # Domains
        yblacklisted.append(item[2]) # Count

    ### Plotly does this better. Blacklisted Barchart:
    '''blacklistedbarchart = discreteBarChart(name='discreteBarChart', height=300, width=600)
                blacklistedbarchart.add_serie(y=yblacklisted, x=xblacklisted)
                blacklistedbarchart.buildhtml()
                writefile = open('../flask/templates/blacklisted_domains.html','w')
                writefile.write(blacklistedbarchart.htmlcontent)'''

    #####################################
    # For a chart of whitelisted domains:
    xwhitelisted = []
    ywhitelisted = []
    for item in wl_domains:
        item = item.split(',')
        xwhitelisted.append(item[0]) # Domains
        ywhitelisted.append(item[2]) # Count

    ### Plotly does this better. whitelisted Barchart:
    '''whitelistedbarchart = discreteBarChart(name='discreteBarChart', height=300, width=600)
                whitelistedbarchart.add_serie(y=ywhitelisted, x=xwhitelisted)
                whitelistedbarchart.buildhtml()
                writefile = open('../flask/templates/whitelisted_domains.html','w')
                writefile.write(whitelistedbarchart.htmlcontent)'''

    #####################################

    # For a Pie Chart of categories:
    xcategorylist = []
    ycategorylist = []
    for item in category_list:
        xcategorylist.append(item[0]) # Categories
        ycategorylist.append(item[1]) # Count

    ### Blacklisted Barchart:
    type = 'pieChart'
    categorypiechart = pieChart(name=type, color_category='category20c', height=1000, width=1000)
    xdata = xcategorylist
    ydata = ycategorylist
    extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
    categorypiechart.add_serie(y=ydata, x=xdata, extra=extra_serie)
    categorypiechart.buildhtml()
    writefile = open('../flask/templates/category_piechart.html','w')
    writefile.write(categorypiechart.htmlcontent)

    df_categories = pd.DataFrame(data=ycategorylist,index=xcategorylist)

    
    #####################################
    # For a Pie Chart of security categories:
    xseccategorylist = []
    yseccategorylist = []
    for item in security_category_list:
        xseccategorylist.append(item[0]) # Categories
        yseccategorylist.append(item[1]) # Count

    ### security category piehart:
    type = 'pieChart'
    security_categorypiechart = pieChart(name=type, color_category='category20c', height=450, width=450)
    xdata = xseccategorylist
    ydata = yseccategorylist
    extra_serie = {"tooltip": {"y_start": "", "y_end": ""}}
    security_categorypiechart.add_serie(y=ydata, x=xdata, extra=extra_serie)
    security_categorypiechart.buildhtml()
    writefile = open('../flask/templates/security_category_piechart.html','w')
    writefile.write(security_categorypiechart.htmlcontent)

    #####################################
    # For a chart of neutral listed domains:
    xneutrallisted = []
    yneutrallisted = []
    for item in not_determined_domains:
        item = item.split(',')
        xneutrallisted.append(item[0]) # Domains
        yneutrallisted.append(item[2]) # Count

    ### Plotly does this better. neutral listed Barchart:
    '''neutrallistedbarchart = discreteBarChart(name='discreteBarChart', height=300, width=600)
                neutrallistedbarchart.add_serie(y=yneutrallisted, x=xneutrallisted)
                neutrallistedbarchart.buildhtml()
                writefile = open('../flask/templates/neutral_domains.html','w')
                writefile.write(neutrallistedbarchart.htmlcontent)'''

    #################################
    stats_number_of_u_domains =  str(len(unique_domains)) + " unique domains seen<br>"
    stats_number_of_t_domains =  str(len(timeanddomain)) + " total domains<br>"
    stats_number_of_ips =  str(len(ip)) + " total IP addresses<br>"
    stats_normaltraffic = ('Normal traffic (domains visited over 3 times): {0}<br>').format(len(normal_traffic))
    stats_suspicioustraffic = ('Amount of suspicious traffic domains visited under 2 times): {0}<br>').format(len(suspicious_traffic))
    stats_wl = ('<br>Of the suspicious domains (uniqued):<br>Whitelisted domains (OpenDNS): {0}<br>'.format(len(wl_domains)))
    stats_bl = ('Blacklisted domains (OpenDNS): {0}<br>'.format(len(bl_domains)))
    stats_neutral = ('Neutral domains (OpenDNS): {0}'.format(len(not_determined_domains)))
    stats_categories_list = ('Number of categories seen: {0}'.format(len(categories_list)))

    stats = stats_number_of_u_domains + stats_number_of_t_domains + stats_number_of_ips + stats_normaltraffic + stats_suspicioustraffic + stats_wl + stats_bl + stats_neutral

    writefile = open('../flask/templates/stats.html','w')
    writefile.write(stats)

    # This one's for plotly:
    xtime = []
    ytime = []
    for item in timeanddomain:
        item = item.split(',')
        xtime.append(item[0])
        ytime.append(item[1])

    d = {'date':xtime,'domain':ytime}
    df = pd.DataFrame(data=d)
    df['counts'] = df.groupby('domain').transform('count')
    
    # For plotly:
    df2 = pd.DataFrame(data=ytime,index=xtime)
    df2.index = pd.to_datetime(df2.index)
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
    '''plot_html, plotdivid, width, height =  _plot_html(df2.iplot(asFigure=True, kind ='scatter', subplots=True, shared_xaxes=True, fill=True, title='Count by day',dimensions=(800,800)), False, "", True, '100%', 525, False)
                html_bar_chart = html_start + plot_html + html_end
                f = open('../flask/templates/plottest_scatter.html', 'w')
                f.write(html_bar_chart)
                f.close()'''

    # Suspicious domains
    df_suspicious = pd.DataFrame(ysuspicious, xsuspicious)
    plot_html, plotdivid, width, height =  _plot_html(df_suspicious.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='Suspicious Traffic',dimensions=(600,600)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('../flask/templates/suspicious_traffic.html', 'w')
    f.write(html_bar_chart)
    f.close()
    
    # All domains visited
    df_alldomains = pd.DataFrame(ydomaindata, xdomaindata)
    plot_html, plotdivid, width, height =  _plot_html(df_alldomains.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='All Traffic',dimensions=(600,300)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('../flask/templates/all_traffic.html', 'w')
    f.write(html_bar_chart)
    f.close()

    # Whitelisted
    df_whitelisted = pd.DataFrame(ywhitelisted, xwhitelisted)
    plot_html, plotdivid, width, height =  _plot_html(df_whitelisted.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='Whitelisted Traffic',dimensions=(600,300)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('../flask/templates/whitelisted_traffic.html', 'w')
    f.write(html_bar_chart)
    f.close()

    # Not categorized
    df_not_categorized = pd.DataFrame(yneutrallisted, xneutrallisted)
    plot_html, plotdivid, width, height =  _plot_html(df_not_categorized.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='Non-categorized Traffic',dimensions=(600,300)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('../flask/templates/not_categorized_traffic.html', 'w')
    f.write(html_bar_chart)
    f.close()

    # Blacklisted
    df_blacklisted = pd.DataFrame(yblacklisted, xblacklisted)
    plot_html, plotdivid, width, height =  _plot_html(df_blacklisted.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='Blacklisted Traffic',dimensions=(600,300)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('../flask/templates/blacklisted_traffic.html', 'w')
    f.write(html_bar_chart)
    f.close()
    
    # Time Series
    df_timeseries = pd.DataFrame(ytimedata,xtimedata)
    plot_html, plotdivid, width, height =  _plot_html(df_timeseries.iplot(asFigure=True, kind ='bar', subplots=False, shared_xaxes=True, fill=True, title='Time Series',dimensions=(800,450)), False, "", True, '100%', 525, False)
    html_bar_chart = html_start + plot_html + html_end
    f = open('../flask/templates/timeseries.html', 'w')
    f.write(html_bar_chart)
    f.close()

    # Bar chart of domain counts per day:
    # Line plot:
    #plot_html, plotdivid, width, height =  _plot_html(dftest.iplot(asFigure=True, kind = 'line', subplots=False, shared_xaxes=True, fill=True, title='Count by day',dimensions=(800,800)), False, "", True, '100%', 525, False)
    #html_bar_chart = html_start + plot_html + html_end
    #f = open('../flask/templates/plottest.html', 'w')
    #f.write(html_bar_chart)
    #f.close()

    # End plotly chart generation


    # Flask wants something returned (only used when this script is accessed via flash/app.py. If the dataset is too large, every time you refresh the web app, it will re-run this script. I found it more effective to manually run this script or, later: run it via a cron job)
    #json_projects = json.dumps(count_of_domains, default=json_util.default)
    #connection.close()
    # Return data to app.py
    #return json_projects
process_data()