'''from nvd3 import pieChart
type = 'pieChart'
chart = pieChart(name=type, color_category='category20c', height=450, width=450)
xdata = ["Orange", "Banana", "Pear", "Kiwi", "Apple", "Strawberry", "Pineapple"]
ydata = [3, 4, 0, 1, 5, 7, 3]
extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
chart.buildcontent()'''


from nvd3 import lineChart
chart = lineChart(name="lineChart", x_is_date=False, x_axis_format="AM_PM")

xdata = range(24)
ydata = [0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 4, 3, 3, 5, 7, 5, 3, 16, 6, 9, 15, 4, 12]
ydata2 = [9, 8, 11, 8, 3, 7, 10, 8, 6, 6, 9, 6, 5, 4, 3, 10, 0, 6, 3, 1, 0, 0, 0, 1]

extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"}}
chart.add_serie(y=ydata, x=xdata, name='sine', extra=extra_serie)
extra_serie = {"tooltip": {"y_start": "", "y_end": " min"}}
chart.add_serie(y=ydata2, x=xdata, name='cose', extra=extra_serie)
chart.buildhtml()


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
    <script src={{ url_for('static', filename='main.js') }}></script>'''

htmltail = '''</body>
</html>'''

htmloutput = htmlhead + chart.htmlcontent + htmltail

writefile = open('index.html','w')
writefile.write(htmloutput)