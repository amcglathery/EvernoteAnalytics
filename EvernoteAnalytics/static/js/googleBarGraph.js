//This may only be called after jquery and googlejsapi has been invoked
//parameters:
//categoryCounts - nested arrays in the form [[categoryName,count]]
//categoryTitle - title for bottom header
//displayElement - div element to be displayed in
function drawBarGraph(categoryCounts, categoryTitle, displayElement){
  google.load("visualization", "1", {packages:["corechart"]});
  google.setOnLoadCallback(drawChart);
  function drawChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', categoryTitle);
    data.addColumn('number', 'Total Notes');
    data.addRows(categoryCounts);
    var options = {
       title: '',
       hAxis: {title: categoryTitle + 's', titleTextStyle: {color: 'purple'}}
                    };
    var chart = new google.visualization.ColumnChart(document.getElementById(displayElement));
    chart.draw(data, options);
  }
}
