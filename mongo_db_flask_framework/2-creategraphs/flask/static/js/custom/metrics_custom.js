//metrics js bits:
d3.json('/static/data/ts_all.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "All Domains",
      // description: "All Domains",
      data: data,
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('ts_all_bandwidth'),
      x_accessor: 'date',
      y_accessor: 'value',
      // x_label: ['All Domains']
    });
  });

    d3.json('/static/data/ts_domains_in_top_1m.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "Domains in the top 1 Million list",
      // description: "Domains in top 1 Million",
      data: data,
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('ts_domains_in_top_1m'),
      x_accessor: 'date',
      y_accessor: 'value'
      // x_label: ['Domains in the top 1 Million list']
    });
  });

    d3.json('/static/data/ts_domains_not_in_top_1m.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    MG.data_graphic({
      title: "Domains not in the top 1 Million list",
      // description: "Domains not in top 1 Million",
      data: data,
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('ts_domains_not_in_top_1m'),
      x_accessor: 'date',
      y_accessor: 'value'
      // x_label: ['Domains not in the top 1 Million list']
    });
  });

d3.json('static/data/all_domains_multiline.json', function(data) {
    for (var i = 0; i < data.length; i++) {
        data[i] = MG.convert.date(data[i], 'date',"%Y-%m-%d %H:%M:%S");
    }

    var all_the_data = MG.clone(data[0]);
    for (i = 1; i < data.length; i++){
        for (var j = 0; j < data[i].length; j++){
            if (i === 2 && all_the_data[j].date < new Date('%Y-%m-%d %H:%M:%S')) {
            } else {
                all_the_data[j]['value' + (i + 1)] = data[i][j].value;
            }
        }
    }
    MG.data_graphic({
        title: "All Queries Aggregated",
        // description: "none",
        data: all_the_data,
        width: 600,
        height: 200,
        right: 40,
        target: document.getElementById('aggregated-all'),
        y_extended_ticks: true,
        x_accessor: 'date',
        y_accessor: ['value', 'value2', 'value3'],
        legend: ['All Domains','Domains in Top 1 Million','Domains Not in Top 1 Million'],
        legend_target: '.legend',
        // x_label: ['All Queries Aggregated'],
        aggregate_rollover: true
    });
});

d3.json('static/data/ts_all_investigate_security_category.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "Security Categories (all domains)",
      // description: "All Domains",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('security_categories_all'),
      x_accessor: 'date',
      y_accessor: 'value',
      color_accessor: 'v',
      color_domain: ['neutral', 'good', 'bad'],
      color_range: ['gray', 'green', 'red'],
      color_type: 'category'
    });
  });

d3.json('static/data/ts_domains_in_top_1m_investigate_security_category.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "Security Categories (In Top Domains)",
      // description: "All Domains",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('security_categories_in_top_1m'),
      x_accessor: 'date',
      y_accessor: 'value',
      color_accessor: 'v',
      color_domain: ['neutral', 'good', 'bad'],
      color_range: ['gray', 'green', 'red'],
      color_type: 'category'
    });
  });

d3.json('static/data/ts_domains_not_in_top_1m_investigate_security_category.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    console.log(data)
    MG.data_graphic({
      title: "Security Categories (Not in Top Domains)",
      // description: "All Domains",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('security_categories_not_in_top_1m'),
      x_accessor: 'date',
      y_accessor: 'value',
      color_accessor: 'v',
      color_domain: ['neutral', 'good', 'bad'],
      color_range: ['gray', 'green', 'red'],
      color_type: 'category'
    });
  });

// for testing:
d3.json('static/data/test_all_investigate_security_category.json', function(data) {
    data = MG.convert.date(data, "date","%Y-%m-%d %H:%M:%S"); 
    // console.log(data)
    MG.data_graphic({
      title: "TEST Security Categories (all domains)",
      // description: "All Domains",
      data: data,
      chart_type: 'point',
      width: 600,
      height: 200,
      right: 40,
      target: document.getElementById('testsecurity_categories_all'),
      x_accessor: 'date',
      y_accessor: 'value',
      color_accessor: 'v',
      // size_accessor:'value',
      color_domain: ['neutral', 'good', 'bad'],
      color_range: ['gray', 'green', 'red'],
      least_squares: true,
      legend: ['neutral', 'good', 'bad'],
      // legend_target: '.legend',
      // aggregate_rollover: true,
      color_type: 'category'
    });
  });