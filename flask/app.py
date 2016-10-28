from flask import Flask, render_template, jsonify
import os
from process_dns import process_data

#app = Flask(__name__)
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dns")
def data():
    #return get_data()
    return process_data()

if __name__ == "__main__":
#    app.run(host='0.0.0.0',port=5000,debug=True)
     app.run(host='127.0.0.1',port=5000,debug=True)
