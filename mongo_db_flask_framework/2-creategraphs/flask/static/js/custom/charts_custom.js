var randomColorGenerator = function () { 
    return '#' + (Math.random().toString(16) + '0000000').slice(2, 8); 
};

horizontalbar('/static/data/categories_all_data.json', 'categories_bar');
function horizontalbar(endpoint, elem) {
    var oReq = new XMLHttpRequest();
    oReq.onreadystatechange =  function() {
        if ( oReq.readyState === XMLHttpRequest.DONE ) {
            if ( oReq.status === 200 ) {
                var data = JSON.parse(oReq.responseText);
                // data['data']['datasets'][0]['backgroundColor'] = default_colors;
                var ctx = document.getElementById(elem);
                var cats = new Chart(ctx, {
                    type: 'horizontalBar',
                    data: data["data"],
                    options: {
                        barThickness: 10, 
                        title: {
                        display: true,
                        text: 'Categories (all domains)'
                        },
                        legend: {
                            display: false
                            }
                    }
                })
            }
        }
    };
    oReq.open('GET', endpoint);
    oReq.send();
}

// used for a pie chart for all domains
category_Chart1('/static/data/categories_all_data.json', 'categories_pie_all');
function category_Chart1(endpoint, elem) {
    var oReq = new XMLHttpRequest();
    oReq.onreadystatechange =  function() {
        if ( oReq.readyState === XMLHttpRequest.DONE ) {
            if ( oReq.status === 200 ) {
                var data = JSON.parse(oReq.responseText);
                // data['data']['datasets'][0]['backgroundColor'] = default_colors;
                var ctx1 = document.getElementById(elem);                
                var catpiechart1 = new Chart(ctx1, {
                    type: 'pie',
                    data: data["data"],
                    options: {
                        barThickness: 10, 
                        responsive: true,
                        maintainAspectRatio: false,
                        title: {
                        display: true,
                        text: 'Categories (all domains)'
                        },

                        legend: {
                            display: false,
                            position: 'right'
                            }
                    }
                })
            }
        }
    };
    oReq.open('GET', endpoint);
    oReq.send();
}

category_Chart2('/static/data/categories_domains_in_top_1m.json', 'categories_pie_domains_in_top_1m');
function category_Chart2(endpoint, elem) {
    var oReq = new XMLHttpRequest();
    oReq.onreadystatechange =  function() {
        if ( oReq.readyState === XMLHttpRequest.DONE ) {
            if ( oReq.status === 200 ) {
                var data = JSON.parse(oReq.responseText);
                // data['data']['datasets'][0]['backgroundColor'] = default_colors;
                var ctx2 = document.getElementById(elem);                
                var catpiechart2 = new Chart(ctx2, {
                    type: 'pie',
                    data: data["data"],
                    options: {
                        barThickness: 10, 
                        responsive: true,
                        maintainAspectRatio: false,
                        title: {
                        display: true,
                        text: 'Categories (In Top Domains)'
                        },

                        legend: {
                            display: false,
                            position: 'right'
                            }
                    }
                })
            }
        }
    };
    oReq.open('GET', endpoint);
    oReq.send();
}

category_Chart3('/static/data/categories_domains_not_in_top_1m.json', 'categories_pie_domains_not_in_top_1m');
function category_Chart3(endpoint, elem) {
    var oReq = new XMLHttpRequest();
    oReq.onreadystatechange =  function() {
        if ( oReq.readyState === XMLHttpRequest.DONE ) {
            if ( oReq.status === 200 ) {
                var data = JSON.parse(oReq.responseText);
                // data['data']['datasets'][0]['backgroundColor'] = default_colors;
                var ctx3 = document.getElementById(elem);                
                var catpiechart3 = new Chart(ctx3, {
                    type: 'pie',
                    data: data["data"],
                    options: {
                        barThickness: 10, 
                        responsive: true,
                        maintainAspectRatio: false,
                        title: {
                        display: true,
                        text: 'Categories (Not in Top Domains)'
                        },

                        legend: {
                            display: false,
                            position: 'right'
                            }
                    }
                })
            }
        }
    };
    oReq.open('GET', endpoint);
    oReq.send();
}

inv_sec_categories('/static/data/inv_sec_categories.json', 'inv_categories_pie');
function inv_sec_categories(endpoint, elem) {
    var oReq = new XMLHttpRequest();
    oReq.onreadystatechange =  function() {
        if ( oReq.readyState === XMLHttpRequest.DONE ) {
            if ( oReq.status === 200 ) {
                var data = JSON.parse(oReq.responseText);
                // data['data']['datasets'][0]['backgroundColor'] = default_colors;
                var ctx = document.getElementById(elem);
                var catpiechart = new Chart(ctx, {
                    type: 'pie',
                    data: data["data"],
                    options: {
                        barThickness: 10, 
                        responsive: true,
                        maintainAspectRatio: false,
                        title: {
                        display: true,
                        text: 'Investigate Security Categories'
                        },

                        legend: {
                            display: true,
                            position: 'left'
                            }
                    }
                })
            }
        }
    };
    oReq.open('GET', endpoint);
    oReq.send();
}