d3.json('data/invalid_logon_attempts.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "Invalid SSH Login Attempts",
      // description: "All Domains",
      data: data,
      chart_type: 'histogram',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('invalid_logon_attempts'),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });