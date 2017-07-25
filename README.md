# behavioral_analysis

* This is for code I'm creating as I attempt to do behaviorial analysis on DNS and other data

There are several different things available. See the code within each directory (instructions are in the comments):

* static_analysis:
AD_Analysis/generate_AD_metrics.py: Analyzes an active directory log file and creates some graphs (currently only on successful and unsuccessful logons/logon attempts). A file, testdata.txt is available to try it out.

auth_log_analysis/generate_Authlog_metrics.py: Analyzes an auth log file from a linux system and makes some graphs. A sample file, auth.log is available for testing.

client_connection_analysis/client_connections.py: Takes a DNS log file and separates each client IP, creating a timeline graph for each IP and displaying the bandwidth for each client. This script was written using log files from infoblocks, but can be easily modified for any kind of log file. A sample file, infobloxsample.txt is available to try out.


*mongo_db_flask_framework:
This folder contains a larger ongoing project that is intended to run as a website, used to view whatever logs have been processed. The logs are initially processed and sent to mongodb, then a flask app runs the web portion, pulling data from mongodb to generate graphs, maps and other data.
Currently, the log processing portion is a manual step

*1-processlogs\process_logs.py: Takes a log file and looks up things in Virustotal and Cisco Umbrella Investigate, also categorizes things and builds a timeline. It's output is a bunch of files in the 'processed' directory. You'll need to modify the process_file() function to fit your specific log style. It's currently built for rasperry PI DNS logs, but it's very easy to change.

*1-processlogs\send_to_mongodb.py: This just sends all the data from inside the 'processed' folder to a mongo database running on localhost. You can switch it to an IP if your db is somewhere else (but don't just leave mongo listening on a public server).

There's a file, testdata.txt that can be used to test process_logs.py.

*NOTE: If you're going to use Investigate and Virustotal (and additional third parties I'll add soon), you will have to enter an API key in the text files inside the 'config' folder.

*2-creategraphs\utilities\get_from_mongo.py: This script can be used on the command line to test pulling data from the mongo db before adding them to the flask app.

*2-creategraphs\utilities\separatedates_tofile.py: This will take a log file and write out separate files for each day. Sometimes it's useful for creating more refined timelines.

*2-creategraphs\flask\__init__.py:  First, start your mongodb, then run this (python __init__.py) and it'll start a local web server at localhost:5000. You can visit that and start reviewing various graphs, maps and other data. It pulls everything from mongo (locally, but that can be changed).
There are several javascript libraries used to display things: metricsgraphics.js, D3, folium (mapping). I've played around with C3 and a few other frameworks. Some of the older ones might be commented out in the __init__.py file, but could always be turned back on.