htmlhead = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>DNS Traffic Stats</title>
    <link href="main.css" rel="stylesheet" type="text/css">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
<body>
    <script src="../bower_components/jquery/dist/jquery.min.js"></script>
    <script src="../bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
    <script src="../bower_components/d3/d3.min.js"></script>
    <script src="../bower_components/nvd3/build/nv.d3.js"></script>
    <script src="../plotly-latest.min.js"></script>

    <!--<br><br>Stats:-->
    <!--<iframe width="100%" height="200px" frameborder="1" scrolling="no" src="stats.html"></iframe>-->

    <br><br>GETs vs POSTs:
    <iframe width="100%" height="500px" frameborder="1" scrolling="yes" src="pcap_category_piechart.html"></iframe>

    <br><br>Timeline:
    <iframe width="100%" height="600px" frameborder="1" scrolling="no" src="pcap_timeseries.html"></iframe>
    '''
    

htmltail = '''</body>
</html>'''

htmloutput = htmlhead + htmltail

writefile = open('pcap/index.html','w')
writefile.write(htmloutput)