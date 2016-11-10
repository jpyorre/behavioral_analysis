from collections import Counter
import sys
import pandas as pd
#from nvd3 import discreteBarChart, pieChart
import datetime

# Plotly:
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from plotly.offline.offline import _plot_html
import cufflinks as cf
import plotly.graph_objs as go

input_file = sys.argv[1]

def process_data():

    # Count the number of times a something is seen:
    def count_stuff(listofitems):
        listofitems_counted = Counter()
        for d in listofitems:
            t = d.split(',')[0]
            info = d.split(',')[1]
            listofitems_counted[t] += 1
        return(listofitems_counted) 

    #####################################
    # Process input file:
    event_ids = []
    task_categories = []

    all_items = []
    successful_logons = []
    successful_logoffs = []
    logon_attempts = []
    failed_logon_attempts = []

    # Open the input file, convert datetime to datetime object and add separate items:
    with open(input_file) as f:
        for item in f:
            rawline = item.strip()
            s = rawline.split(',')
            audit_result = s[0]
            dateandtime = s[1]
            dt = datetime.datetime.strptime(dateandtime, "%m/%d/%Y %I:%M:%S %p")
            source = s[2]
            event_id = s[3]
            task_category = s[4]
            info = s[5]
            task_categories.append(task_category)
            event_ids.append(event_id)
            
            line = "{0},{1}".format(dt,info)
            all_items.append(line)

            if event_id == '4624':  # Successful Logons
                line = "{0},{1}".format(dt,info)
                successful_logons.append(line)

            if event_id == '4634':  # Successful Logoffs
                line = "{0},{1}".format(dt,info)
                successful_logoffs.append(line)

            if event_id == '4648':  # Logon attempt
                line = "{0},{1}".format(dt,info)
                logon_attempts.append(line)
        
            if event_id == '4625':  # Failed Logon attempts
                line = "{0},{1}".format(dt,info)
                failed_logon_attempts.append(line)
            
        #for item in successful_logons:
        #    print item
         
        def make_a_list_of_dates_and_counts(listofitems):
            # Turn the count_of_successful_logons into a dictionary
            counted_items = []
            temp = []
            for key, value in listofitems.iteritems():
                temp = [key,value]
                counted_items.append(temp)
            return counted_items

        _all_items = count_stuff(all_items) 
        _count_of_successful_logons = count_stuff(successful_logons) 
        _count_of_successful_logoffs = count_stuff(successful_logoffs) 
        _count_of_logon_attempts = count_stuff(logon_attempts) 
        _count_of_failed_logon_attempts = count_stuff(failed_logon_attempts) 

        

        all_events = make_a_list_of_dates_and_counts(_all_items)
        successful_logons = make_a_list_of_dates_and_counts(_count_of_successful_logons)
        successful_logoffs = make_a_list_of_dates_and_counts(_count_of_successful_logoffs)
        logon_attempts = make_a_list_of_dates_and_counts(_count_of_logon_attempts)
        failed_logon_attempts = make_a_list_of_dates_and_counts(_count_of_failed_logon_attempts)
        
        #############################
        # HTML for plotly plots:
        #############################
        html_start = """<html>
        <head>
          <script src="../flask/static/plotly-latest.min.js"></script>
        </head>
        <body>"""
    
        html_end = """
        </body>
        </html>"""
        #print security_categories_list
        #####################################
        # CHART GENERATION
        #####################################

        #########################
        # Successful Logons
        x = []
        y = []
        for item in successful_logons:   
            x.append(item[0])
            y.append(item[1])
        
        df_successful_logons = pd.DataFrame(y, x)
        plot_html, plotdivid, width, height =  _plot_html(df_successful_logons.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='Successful Logons',dimensions=(600,600)), False, "", True, '100%', 525, False)
        html_bar_chart = html_start + plot_html + html_end
        f = open('successful_logons.html', 'w')
        f.write(html_bar_chart)
        f.close()

        ##########################
        # successful logoffs
#        x = []
#        y = []
#        for item in successful_logoffs:   
#            x.append(item[0])
#            y.append(item[1])
        
#        df_successful_logoffs = pd.DataFrame(y, x)
#        plot_html, plotdivid, width, height =  _plot_html(df_successful_logoffs.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='Successful Logoffs',dimensions=(600,600)), False, "", True, '100%', 525, False)
#        html_bar_chart = html_start + plot_html + html_end
#        f = open('successful_logoffs.html', 'w')
#        f.write(html_bar_chart)
#        f.close()

        ##########################
        # Failed logon attempts
        x = []
        y = []
        for item in failed_logon_attempts:   
            x.append(item[0])
            y.append(item[1])
        
        if len(x) >= 1:
            df_failed_logon_attempts = pd.DataFrame(y, x)
            plot_html, plotdivid, width, height =  _plot_html(df_failed_logon_attempts.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='Failed Login Attempts',dimensions=(600,600)), False, "", True, '100%', 525, False)
            html_bar_chart = html_start + plot_html + html_end
            f = open('failed_logon_attempts.html', 'w')
            f.write(html_bar_chart)
            f.close()
        else:
            print('No failed login attempts')

        ##########################
        # logon attempts
        x = []
        y = []
        for item in logon_attempts:   
            x.append(item[0])
            y.append(item[1])
        
        df_logon_attempts = pd.DataFrame(y, x)
        plot_html, plotdivid, width, height =  _plot_html(df_logon_attempts.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='Login Attempts',dimensions=(600,600)), False, "", True, '100%', 525, False)
        html_bar_chart = html_start + plot_html + html_end
        f = open('logon_attempts.html', 'w')
        f.write(html_bar_chart)
        f.close()

        ##########################
        # All Events
        x = []
        y = []
        for item in all_events:   
            x.append(item[0])
            y.append(item[1])
        
        df_all_events = pd.DataFrame(y, x)
        plot_html, plotdivid, width, height =  _plot_html(df_all_events.iplot(asFigure=True, kind ='bar', subplots=True, shared_xaxes=True, fill=False, title='All Events',dimensions=(600,600)), False, "", True, '100%', 525, False)
        html_bar_chart = html_start + plot_html + html_end
        f = open('all_events.html', 'w')
        f.write(html_bar_chart)
        f.close()        
        # Time visit Barchart with D3:
#        successful_logins_barchart = discreteBarChart(name='discreteBarChart', height=600, width=1000)
#        successful_logins_barchart.add_serie(y=y, x=x)
#        successful_logins_barchart.buildhtml()
#        writefile = open('successful_logins_barchart.html','w')
#        writefile.write(successful_logins_barchart.htmlcontent)

process_data()