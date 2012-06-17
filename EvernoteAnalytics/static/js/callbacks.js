function createMapCallback(jsonUrl, usernameStr, iconUrl, divElement){
  return function() {
    $.getJSON(jsonUrl,{username : usernameStr},
      function(json){
        var points = json['points']
        var center = [42.408, -71.120]
        var landmark = new google.maps.LatLng(center[0],center[1]);
        var myOptions = {
          zoom: 12, // The larger the zoom number, the bigger the zoom
          center: landmark,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById(divElement),myOptions);
        var elephant = iconUrl;
        for (i = 0; i<points.length; i++) {
           var land = new google.maps.LatLng(points[i][1],points[i][2]);
           var marker = new google.maps.Marker({
             position: land,
             title: points[i][0],
             icon: elephant
           });
           marker.setMap(map);
           var statwindow = new google.maps.InfoWindow();
           google.maps.event.addListener(marker, 'click', (function(marker, i) {
             return function(){
              statwindow.setContent(points[i][0]);
              statwindow.open(map, marker);
             }
           })(marker,i));
         }
      })};
}

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
