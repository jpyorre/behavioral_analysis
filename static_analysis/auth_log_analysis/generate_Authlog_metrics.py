# This takes an auth.log log file that looks like this (originally from ssh auth logs on a Debian system and displays the invalid logons:
# Jul  9 07:46:22 evol sshd[26462]: Invalid user dave from 179.125.52.114
#
# It writes the following files:
# ./data/
#   invalid_logon_attempts.json
# The javascript for metricsgraphics is in ../assets/js/custom/auth_log_metrics_custom.js
#
# Run like this:
# python generate_Authlog_metrics.py inputfile.log (auditlines.txt if you want to try the example file - auth.log)
# When done, open authlog_metrics.html to display results

# A lot of code is commented out as this is still being added to. I'm adding other things, like:
# successful logons
# successful user logons vs successful cron login events
# Username analysis

from collections import Counter
import sys
import datetime, json

input_file = sys.argv[1]

def write_to_json(data,outfile):
    l = []
    for line in data:
        # dt, username, count = line[0], line[1], line[2]
        # item = {'value':str(count),'date':str(dt), 'username':username}
        dt, count = line[0], line[1]
        item = {'value':str(count),'date':str(dt)}
        l.append(item)
    json.dump(l, open(outfile,'w'))

# def make_multiline_metrics_json(data1,data2,data3,data4,outfile):
#     d1,d2,d3,d4,multiline_list = [],[],[],[],[]
#     for line in data1:
#         dt, count = line[0], line[1]
#         item = {'value':str(count),'date':str(dt)}
#         d1.append(item)
#     for line in data2:
#         dt, count = line[0], line[1]
#         item = {'value':str(count),'date':str(dt)}
#         d2.append(item)
#     for line in data3:
#         dt, count = line[0], line[1]
#         item = {'value':str(count),'date':str(dt)}
#         d3.append(item)
#     for line in data4:
#         dt, count = line[0], line[1]
#         item = {'value':str(count),'date':str(dt)}
#         d4.append(item)
#     multiline_list.append(d1)
#     multiline_list.append(d2)
#     multiline_list.append(d3)
#     multiline_list.append(d4)
#     json.dump(multiline_list, open(outfile,'w'))

# Count the number of times a something is seen:
def count_stuff(listofitems):
    listofitems_counted = Counter()
    usernames = []
    for d in listofitems:
        t = d.split(',')[0]
        info = d.split(',')[1]
        listofitems_counted[t] += 1
        usernames.append(info)
    return(listofitems_counted,usernames) 

def make_a_list_of_dates_and_counts(listofitems):
    # Turn the count_of_successful_logons into a dictionary
    counted_items = []
    temp = []
    for key, value in listofitems.iteritems():
        temp = [key,value]
        counted_items.append(temp)
    return counted_items

# Process input file:
def process_data():
    event_ids = []
    task_categories = []

    all_items = []
    invalid_logon_attempts = []
    invalid_usernames = []
    successful_logons = []

    # Open the input file, convert datetime to datetime object and add separate items:
    with open(input_file) as f:
        for item in f:
            rawline = item.strip()
            if "Invalid" in rawline:
                s = rawline.split('  ')
                if len(s) == 2:
                    s2 = s[1].split(' ')
                    month = s[0]
                    day = s2[0]
                    times = s2[1]
                    message = s2[4],s2[5]
                    attempted_username = s2[6]
                    attacker_ip = s2[8]
                    rawdatetime = "{0} {1} {2}".format(month,day,times)
                    dt = datetime.datetime.strptime(rawdatetime, "%b %d %H:%M:%S")
                    dt = dt.replace(year=2017) # year isn't specified, so I have to put it in manually :(
                    invalidlogonline = "{0},{1}".format(dt,attempted_username)
                    invalid_logon_attempts.append(invalidlogonline)
                else:
                    s2 = rawline.split(' ')
                    month = s2[0]
                    day = s2[1]
                    times = s2[2]
                    message = s2[5],s2[6]
                    attempted_username = s2[7]
                    attacker_ip = s2[9]
                    rawdatetime = "{0} {1} {2}".format(month,day,times)
                    dt = datetime.datetime.strptime(rawdatetime, "%b %d %H:%M:%S")
                    dt = dt.replace(year=2017) # year isn't specified, so I have to put it in manually :(
                    invalidlogonline = "{0},{1}".format(dt,attempted_username)
                    invalid_logon_attempts.append(invalidlogonline)
                # print dt,message,attempted_username,attacker_ip

            # if "opened" in rawline:
            #     s = rawline.split('  ')
            #     if len(s) == 2:
            #         s2 = s[1].split(' ')
            #         month = s[0]
            #         day = s2[0]
            #         times = s2[1]
            #         message = s2[4],s2[5]
            #         username = s2[6]
            #         ip = s2[8]
            #         rawdatetime = "{0} {1} {2}".format(month,day,times)
            #         dt = datetime.datetime.strptime(rawdatetime, "%b %d %H:%M:%S")
            #         dt = dt.replace(year=2017) # year isn't specified, so I have to put it in manually :(
            #         connectionopenedline = "{0},{1}".format(dt,username)
            #         successful_logons.append(connectionopenedline)
            #     else:
            #         s2 = rawline.split(' ')
            #         month = s2[0]
            #         day = s2[1]
            #         times = s2[2]
            #         message = s2[5],s2[6]
            #         username = s2[7]
            #         ip = s2[9]

            #         print s2
            #         rawdatetime = "{0} {1} {2}".format(month,day,times)
            #         dt = datetime.datetime.strptime(rawdatetime, "%b %d %H:%M:%S")
            #         dt = dt.replace(year=2017) # year isn't specified, so I have to put it in manually :(
            #         connectionopenedline = "{0},{1}".format(dt,username)
            #         successful_logons.append(connectionopenedline)
 
    # _all_items = count_stuff(all_items) 
    # _count_of_successful_logons = count_stuff(successful_logons) 
    # _count_of_successful_logoffs = count_stuff(successful_logoffs) 
    # _count_of_logon_attempts = count_stuff(logon_attempts) 
    _count_of_invalid_logon_attempts, usernames = count_stuff(invalid_logon_attempts) 





    # all_events = make_a_list_of_dates_and_counts(_all_items)
    # successful_logons = make_a_list_of_dates_and_counts(_count_of_successful_logons)
    # successful_logoffs = make_a_list_of_dates_and_counts(_count_of_successful_logoffs)
    # logon_attempts = make_a_list_of_dates_and_counts(_count_of_logon_attempts)
    failed_logon_attempts = make_a_list_of_dates_and_counts(_count_of_invalid_logon_attempts)

    # print zipped
    # print failed_logon_attempts

    # print failed_logon_attempts

#         # CHART GENERATION
#         # Successful Logons
    # write_to_json(successful_logons,'data/successful_logons.json')
    # write_to_json(successful_logoffs,'data/successful_logoffs.json')
    write_to_json(failed_logon_attempts,'data/invalid_logon_attempts.json')
    # write_to_json(logon_attempts,'data/logon_attempts.json')
    # write_to_json(all_events,'data/all_events.json')

#         make_multiline_metrics_json(successful_logons,successful_logoffs,failed_logon_attempts,logon_attempts,'static/data/multiline_metrics.json')
 

process_data()