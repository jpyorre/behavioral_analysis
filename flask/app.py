from flask import Flask, render_template, jsonify
import os
#from process_dns import process_data

#app = Flask(__name__)
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/all_traffic.html')
def all_traffic():
    return render_template("all_traffic.html")

@app.route('/timeseries.html')
def timeseries():
    return render_template("timeseries.html")

@app.route('/category_piechart.html')
def category_piechart():
    return render_template("category_piechart.html")

@app.route('/security_category_piechart.html')
def security_category_piechart():
    return render_template("security_category_piechart.html")
    
@app.route('/blacklisted_traffic.html')
def blacklisted_traffic():
    return render_template("blacklisted_traffic.html")

@app.route('/not_categorized_traffic.html')
def not_categorized_traffic():
    return render_template("not_categorized_traffic.html")

@app.route('/suspicious_traffic.html')
def suspicious_traffic():
    return render_template("suspicious_traffic.html")

@app.route('/whitelisted_traffic.html')
def whitelisted_traffic():
    return render_template("whitelisted_traffic.html")

@app.route('/stats.html')
def stats():
    return render_template("stats.html")

@app.route('/pcap/')
def pcap():
    return render_template("pcap/index.html")

@app.route('/pcap/pcap_category_piechart.html')
def pcap_category_piechart():
    return render_template("pcap/pcap_category_piechart.html")

@app.route('/pcap/pcap_timeseries.html')
def pcap_timeseries():
    return render_template("pcap/pcap_timeseries.html")

@app.route('/pcap/gets_to_dst_ips.svg')
def gets_to_dst_ips():
    return render_template("pcap/gets_to_dst_ips.svg")

@app.route('/pcap/posts_to_dst_ips.svg')
def posts_to_dst_ips():
    return render_template("pcap/posts_to_dst_ips.svg")

    
    

#@app.route("/dns")
#def data():
    #return get_data()
    #return process_data()

if __name__ == "__main__":
#    app.run(host='0.0.0.0',port=5000,debug=True)
     app.run(host='127.0.0.1',port=5000,debug=True)
