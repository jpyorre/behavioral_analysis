htmlhead = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>DNS Traffic Stats</title>
    <link href={{ url_for('static', filename='main.css') }} rel="stylesheet" type="text/css">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
<body>
    <script src={{ url_for('static', filename='../bower_components/bootstrap/dist/js/bootstrap.min.js') }}></script>
    <script src={{ url_for('static', filename='../flask/static/plotly-latest.min.js') }}></script>

    <!--<br><br>Stats:
    <iframe width="100%" height="200px" frameborder="1" scrolling="no" src="stats.html"></iframe>
    -->

    <iframe width="600px%" height="600px" frameborder="0" scrolling="no" src="all_events.html"></iframe>

    <iframe width="600px%" height="600px" frameborder="0" scrolling="no" src="logon_attempts.html"></iframe>

    <iframe width="600px%" height="600px" frameborder="0" scrolling="no" src="failed_logon_attempts.html"></iframe>

    <iframe width="600px%" height="600px" frameborder="0" scrolling="no" src="successful_logons.html"></iframe>
    '''
    

htmltail = '''</body>
</html>'''

htmloutput = htmlhead + htmltail

writefile = open('index.html','w')
writefile.write(htmloutput)