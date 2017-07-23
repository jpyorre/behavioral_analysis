# This takes a log file that looks like this (originally from AD logs, focusing on the loggoffs and logons):
# Audit Success,10/26/2016 10:15:37 AM,Microsoft-Windows-Security-Auditing,4634,Logoff,"An account was logged off.
#
# It writes the following files:
# ./data/
#   all_events.json
#   failed_logon_attempts.json
#   logon_attempts.json
#   multiline_metrics.json
#   successful_logoffs.json
#   successful_logons.json
# The javascript for metricsgraphics is in ../assets/js/custom/ad_analysis_metrics_custom.js
#
# Run like this:
# python generate_AD_metrics.py inputfile.log (auditlines.txt if you want to try the example file - testdata.txt)
# When done, open AD_metrics.html to display results
# Warning, with large log files, it may be super slow when opening in a browser

from collections import Counter
import sys
import pandas as pd
import datetime, json

input_file = sys.argv[1]

def write_to_json(data,outfile):
    l = []
    for line in data:
        dt, count = line[0], line[1]
        item = {'value':str(count),'date':str(dt)}
        l.append(item)
    json.dump(l, open(outfile,'w'))

def make_multiline_metrics_json(data1,data2,data3,data4,outfile):
    d1,d2,d3,d4,multiline_list = [],[],[],[],[]
    for line in data1:
        dt, count = line[0], line[1]
        item = {'value':str(count),'date':str(dt)}
        d1.append(item)
    for line in data2:
        dt, count = line[0], line[1]
        item = {'value':str(count),'date':str(dt)}
        d2.append(item)
    for line in data3:
        dt, count = line[0], line[1]
        item = {'value':str(count),'date':str(dt)}
        d3.append(item)
    for line in data4:
        dt, count = line[0], line[1]
        item = {'value':str(count),'date':str(dt)}
        d4.append(item)
    multiline_list.append(d1)
    multiline_list.append(d2)
    multiline_list.append(d3)
    multiline_list.append(d4)
    json.dump(multiline_list, open(outfile,'w'))

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

        # CHART GENERATION
        # Successful Logons
        write_to_json(successful_logons,'data/successful_logons.json')
        write_to_json(successful_logoffs,'data/successful_logoffs.json')
        write_to_json(failed_logon_attempts,'data/failed_logon_attempts.json')
        write_to_json(logon_attempts,'data/logon_attempts.json')
        write_to_json(all_events,'data/all_events.json')

        make_multiline_metrics_json(successful_logons,successful_logoffs,failed_logon_attempts,logon_attempts,'data/multiline_metrics.json')
 

process_data()