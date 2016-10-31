htmlhead = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Flask Stock Visualizer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href={{ url_for('static', filename='./bower_components/bootstrap/dist/css/bootstrap.min.css') }} rel="stylesheet" media="screen">
    <link href={{ url_for('static', filename='main.css') }} rel="stylesheet" media="screen">
  </head>
  </head>
<body>
    <script src={{ url_for('static', filename='./bower_components/jquery/dist/jquery.min.js') }}></script>
    <script src={{ url_for('static', filename='./bower_components/bootstrap/dist/js/bootstrap.min.js') }}></script>
    <script src={{ url_for('static', filename='./bower_components/d3/d3.min.js') }}></script>
    <script src={{ url_for('static', filename='./bower_components/nvd3/build/nv.d3.js') }}></script>
    <script src={{ url_for('static', filename='main.js') }}></script>
    <script src={{ url_for('static', filename='plotly-latest.min.js') }}></script>

    <br><br>Stats:
    <iframe width="100%" height="100%" frameborder="0" scrolling="no" src="stats.html"></iframe>

    <br><br>Categories:
    <iframe width="100%" height="450px" frameborder="0" scrolling="no" src="category_piechart.html"></iframe>

    <br><br>Security Categories:
    <iframe width="100%" height="450px" frameborder="0" scrolling="no" src="security_category_piechart.html"></iframe>

    <br><br>All domains visited:
    <iframe width="100%" height="310px" frameborder="0" scrolling="no" src="alldomains.html"></iframe>

    <br><br>Blacklisted Domains:
    <iframe width="100%" height="310px" frameborder="0" scrolling="no" src="blacklisted_domains.html"></iframe>

    <br><br>Non-classified Domains:
    <iframe width="100%" height="310px" frameborder="0" scrolling="no" src="neutral_domains.html"></iframe>

    <br><br>Potentially Suspicious Domains:
    <iframe width="100%" height="310px" frameborder="0" scrolling="no" src="suspicious_domains.html"></iframe>

    <br><br>Whitelisted Domains:
    <iframe width="100%" height="310px" frameborder="0" scrolling="no" src="whitelisted_domains.html"></iframe>
    '''
    

htmltail = '''</body>
</html>'''

htmloutput = htmlhead + htmltail

writefile = open('index.html','w')
writefile.write(htmloutput)