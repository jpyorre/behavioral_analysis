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

    <iframe width="100%" height="480px" frameborder="0" scrolling="no" src="domainbar.html"></iframe>
    <iframe width="100%" height="480px" frameborder="0" scrolling="no" src="timebar.html"></iframe>'''

htmltail = '''</body>
</html>'''

htmloutput = htmlhead + htmltail

writefile = open('index.html','w')
writefile.write(htmloutput)