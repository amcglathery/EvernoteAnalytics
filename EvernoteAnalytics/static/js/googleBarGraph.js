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
