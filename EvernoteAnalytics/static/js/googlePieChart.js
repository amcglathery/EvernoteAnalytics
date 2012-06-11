//Requires jsapi to have been envoked beforehand and jquery
function createPieChart(noteMapping, keyToDisplayMap, displayObjectName, displayElement){
   google.load("visualization", "1", {packages:["corechart"]});
   google.setOnLoadCallback(drawChart);
   function drawChart() {
     var data = new google.visualization.DataTable();
     var ret = Array();
     $.each(noteMapping, function(i,obj){
        ret.push([keyToDisplayMap[i],obj]);
     })
     data.addColumn('string', displayObjectName);
     data.addColumn('number', 'Numbers of Notes');
     data.addRows(ret);
     var options = {
       title: 'Posts per ' + displayObjectName
     };
     var chart = new google.visualization.PieChart(document.getElementById(displayElement));
     chart.draw(data, options);
   }
}
