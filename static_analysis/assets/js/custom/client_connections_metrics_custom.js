d3.json("data/192.168.1.64.json", function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "192.168.1.64",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById("192.168.1.64_client_connection_times"),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });
  d3.json("data/192.168.1.21.json", function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "192.168.1.21",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById("192.168.1.21_client_connection_times"),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });
  d3.json("data/192.168.1.65.json", function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "192.168.1.65",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById("192.168.1.65_client_connection_times"),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });
  d3.json("data/192.168.1.25.json", function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "192.168.1.25",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById("192.168.1.25_client_connection_times"),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });
  