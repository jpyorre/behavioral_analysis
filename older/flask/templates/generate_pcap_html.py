html = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>PCAP Stats</title>
    <link href="main.css" rel="stylesheet" type="text/css">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
<body>
    <script src="../bower_components/jquery/dist/jquery.min.js"></script>
    <script src="../bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
    <script src="../bower_components/d3/d3.min.js"></script>
    <script src="../bower_components/nvd3/build/nv.d3.js"></script>
    <script src="../plotly-latest.min.js"></script>

    <br><br>Stats:
    <iframe width="100%" height="100px" frameborder="0" scrolling="no" src="stats.html"></iframe>

    <br><br>GETs vs POSTs:
    <iframe width="100%" height="480px" frameborder="0" scrolling="yes" src="pcap_category_piechart.html"></iframe>

    <br><br>Timeline:
    <iframe width="100%" height="480px" frameborder="0" scrolling="no" src="pcap_timeseries.html"></iframe>

    GET Requests:<br>
    <object type="image/svg+xml" width="1100" height="650" data="gets_to_dst_ips.svg">
    </object>
    <br>
    POSTS:<br>
    <object type="image/svg+xml" width="1100" height="650" data="posts_to_dst_ips.svg">
    </object>
</body>
</html>
'''

writefile = open('pcap/index.html','w')
writefile.write(html)