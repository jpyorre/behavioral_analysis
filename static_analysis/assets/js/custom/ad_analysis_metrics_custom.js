// d3.json('data/multiline_metrics.json', function(data) {
//   for (var i = 0; i < data.length; i++) {
//         data[i] = MG.convert.date(data[i], "date","%Y-%m-%d %H:%M:%S"); 
//     }
//     // data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
//     console.log(data)
//     MG.data_graphic({
//       title: "All Events Multi-Lines",
//       // description: "All Domains",
//       data: data,
//       // chart_type: 'point',
//       width: 600,
//       height: 200,
//       right: 40,
//       missing_is_hidden: true,
//       target: document.getElementById('multiline_metrics'),
//       x_accessor: 'date',
//       y_accessor: 'value',
//       legend: ['Successful Logons','Successful Logoffs','Failed login attempts','login attempts'],
//       legend_target: '.legend'

//     });
//   });


d3.json('data/all_events.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "All Events",
      // description: "All Domains",
      data: data,
      chart_type: 'histogram',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('all_events'),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });

d3.json('data/successful_logons.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "An account was successfully logged on",
      // description: "All Domains",
      data: data,
      chart_type: 'histogram',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('successful_logons'),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });

d3.json('data/successful_logoffs.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "An account was logged off",
      // description: "All Domains",
      data: data,
      chart_type: 'histogram',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('successful_logoffs'),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });

d3.json('data/failed_logon_attempts.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "An account failed to log on",
      // description: "All Domains",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('failed_logon_attempts'),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });

d3.json('data/logon_attempts.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "Logon attempted using explicit credentials",
      // description: "All Domains",
      data: data,
      chart_type: 'histogram',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('logon_attempts'),
      x_accessor: 'date',
      y_accessor: 'value',
    });
  });
