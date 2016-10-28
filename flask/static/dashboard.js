
# Use the queue library for asynchronous loading.
queue()
.defer(d3.json, "/dns")
.await(makeGraphs);
function makeGraphs(error, apiData) {

##############################
# Transform data using d3 functions. Pass the data inside the apiData variable into the dataSet variable.
# Then parse the data type to fulfill our charting needs and set the data type of total_donations as a number using the + operator

var dataSet = apiData;
var dateFormat = d3.time.format("%m/%d/%Y");
dataSet.forEach(function(d) {
d.date_posted = dateFormat.parse(d.date_posted);
// d.date_posted.setDate(1);
d.total_donations = +d.total_donations;
});
##############################
# Ingest data into crossfilter instance and create dimensions based off it.

var ndx = crossfilter(dataSet);

var datePosted = ndx.dimension(function(d) { return d.date_posted; });
var gradeLevel = ndx.dimension(function(d) { return d.grade_level; });
var resourceType = ndx.dimension(function(d) { return d.resource_type; });
var fundingStatus = ndx.dimension(function(d) { return d.funding_status; });
var povertyLevel = ndx.dimension(function(d) { return d.poverty_level; });
var state = ndx.dimension(function(d) { return d.school_state; });
var totalDonations = ndx.dimension(function(d) { return d.total_donations; });

##############################
# Now we calculate metrics and groups for grouping and counting our data.

var projectsByDate = datePosted.group();
var projectsByGrade = gradeLevel.group();
var projectsByResourceType = resourceType.group();
var projectsByFundingStatus = fundingStatus.group();
var projectsByPovertyLevel = povertyLevel.group();
var stateGroup = state.group();
var all = ndx.groupAll();

//Calculate Groups
var totalDonationsState = state.group().reduceSum(function(d) {
return d.total_donations;
});
var totalDonationsGrade = gradeLevel.group().reduceSum(function(d) {
return d.grade_level;
});
var totalDonationsFundingStatus = fundingStatus.group().reduceSum(function(d) {
return d.funding_status;
});
var netTotalDonations = ndx.groupAll().reduceSum(function(d) {return d.total_donations;});

##############################
# Define the charts using DC.js library

var dateChart = dc.lineChart("#date-chart");
var gradeLevelChart = dc.rowChart("#grade-chart");
var resourceTypeChart = dc.rowChart("#resource-chart");
var fundingStatusChart = dc.pieChart("#funding-chart");
var povertyLevelChart = dc.rowChart("#poverty-chart");
var totalProjects = dc.numberDisplay("#total-projects");
var netDonations = dc.numberDisplay("#net-donations");
var stateDonations = dc.barChart("#state-donations");

##############################
# Define our charts

// A dropdown widget
selectField = dc.selectMenu('#menuselect')
.dimension(state)
.group(stateGroup);
// Widget for seeing the rows selected and rows available in the dataset
dc.dataCount("#row-selection")
.dimension(ndx)
.group(all);
//A number chart
totalProjects
.formatNumber(d3.format("d"))
.valueAccessor(function(d){return d; })
.group(all);
//Another number chart
netDonations
.formatNumber(d3.format("d"))
.valueAccessor(function(d){return d; })
.group(netTotalDonations)
.formatNumber(d3.format(".3s"));
//A line chart
dateChart
//.width(600)
.height(220)
.margins({top: 10, right: 50, bottom: 30, left: 50})
.dimension(datePosted)
.group(projectsByDate)
.renderArea(true)
.transitionDuration(500)
.x(d3.time.scale().domain([minDate, maxDate]))
.elasticY(true)
.renderHorizontalGridLines(true)
.renderVerticalGridLines(true)
.xAxisLabel("Year")
.yAxis().ticks(6);
//A row chart
resourceTypeChart
//.width(300)
.height(220)
.dimension(resourceType)
.group(projectsByResourceType)
.elasticX(true)
.xAxis().ticks(5);
//Another row chart
povertyLevelChart
//.width(300)
.height(220)
.dimension(povertyLevel)
.group(projectsByPovertyLevel)
.xAxis().ticks(4);
//Another row chart
gradeLevelChart
//.width(300)
.height(220)
.dimension(gradeLevel)
.group(projectsByGrade)
.xAxis().ticks(4);
//A pie chart
fundingStatusChart
.height(220)
//.width(350)
.radius(90)
.innerRadius(40)
.transitionDuration(1000)
.dimension(fundingStatus)
.group(projectsByFundingStatus);
//A bar chart
stateDonations
//.width(800)
.height(220)
.transitionDuration(1000)
.dimension(state)
.group(totalDonationsState)
.margins({top: 10, right: 50, bottom: 30, left: 50})
.centerBar(false)
.gap(5)
.elasticY(true)
.x(d3.scale.ordinal().domain(state))
.xUnits(dc.units.ordinal)
.renderHorizontalGridLines(true)
.renderVerticalGridLines(true)
.ordering(function(d){return d.value;})
.yAxis().tickFormat(d3.format("s"));

# Call the dc render function which renders our charts

dc.renderAll();
