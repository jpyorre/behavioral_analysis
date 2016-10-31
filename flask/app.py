from flask import Flask, render_template, jsonify
import os
from process_dns import process_data

#app = Flask(__name__)
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/alldomains.html')
def alldomains():
    return render_template("alldomains.html")

@app.route('/category_piechart.html')
def category_piechart():
    return render_template("category_piechart.html")

@app.route('/security_category_piechart.html')
def security_category_piechart():
    return render_template("security_category_piechart.html")
    
@app.route('/blacklisted_domains.html')
def blacklisted():
    return render_template("blacklisted_domains.html")

@app.route('/neutral_domains.html')
def neutral_domains():
    return render_template("neutral_domains.html")

@app.route('/suspicious_domains.html')
def suspicious_domains():
    return render_template("suspicious_domains.html")

@app.route('/whitelisted_domains.html')
def whitelisted_domains():
    return render_template("whitelisted_domains.html")

@app.route('/stats.html')
def stats():
    return render_template("stats.html")

@app.route("/dns")
def data():
    #return get_data()
    return process_data()

if __name__ == "__main__":
#    app.run(host='0.0.0.0',port=5000,debug=True)
     app.run(host='127.0.0.1',port=5000,debug=True)
