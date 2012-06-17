function createPieChartCallback(jsonUrl, usernameStr, divElement){
   return function(){
     $.getJSON(jsonUrl,{username : usernameStr},
       function(json){
          keyToDisplayMap = json['keyToDisplayMap'];
          noteMapping = json['noteMapping'];
          displayObjectName = json['displayObjectName'];
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
          var chart = new google.visualization.PieChart(document.getElementById(divElement));
          chart.draw(data, options);
          })};
}
