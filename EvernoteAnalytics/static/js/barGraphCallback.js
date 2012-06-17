function createBarGraphCallback(jsonUrl, usernameStr, divElement){
  return function() {
    $.getJSON(jsonUrl,{username : usernameStr},
      function(json){
          var data = new google.visualization.DataTable();
    var data = new google.visualization.DataTable();
    var categoryTitle = json['categoryTitle']
    data.addColumn('string', categoryTitle);
    data.addColumn('number', 'Total Notes');
    data.addRows(json['categoryCounts']);
    var options = {
       title: '',
       hAxis: {title: categoryTitle + 's', titleTextStyle: {color: 'purple'}}
                    };
    var chart = new google.visualization.ColumnChart(document.getElementById(divElement));
    chart.draw(data, options);
  })};
}
