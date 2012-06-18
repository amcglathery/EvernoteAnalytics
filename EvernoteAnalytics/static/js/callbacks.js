function createMapCallback(jsonUrl, iconUrl, divElement){
  return function() {
    $.getJSON(jsonUrl,{},
      function(json){
        var points = json['points']
        var center = [42.408, -71.120]
        var landmark = new google.maps.LatLng(center[0],center[1]);
        var myOptions = {
          zoom: 12, // The larger the zoom number, the bigger the zoom
          center: landmark,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map($('#'+divElement).get(0),myOptions);
        var elephant = iconUrl;
        for (var i=0; i<points.length; i++) {
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

function createBarGraphCallback(jsonUrl, divElement){
  return function() {
    $.getJSON(jsonUrl,{},
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
    var chart = new google.visualization.ColumnChart($('#'+divElement).get(0));
    chart.draw(data, options);
  })};
}

function createPieChartCallback(jsonUrl, divElement){
   return function(){
     $.getJSON(jsonUrl,{},
       function(json){
          keyToDisplayMap = json['keyToDisplayMap'];
          noteArray = json['noteArray'];
          displayObjectName = json['displayObjectName'];
          evernoteSearchParam = json['evernoteSearchParam'];
          var data = new google.visualization.DataTable();
          var ret = Array();
          $.each(noteArray, function(i, obj){
            ret.push([keyToDisplayMap[obj[0]],obj[1]]);
          });

          data.addColumn('string', displayObjectName);
          data.addColumn('number', 'Numbers of Notes');
          data.addRows(ret);
          var options = {
              title: 'Posts per ' + displayObjectName
           };
          var chart = new google.visualization.PieChart($('#'+divElement).get(0));
          chart.draw(data, options);
          google.visualization.events.addListener(chart, 'select',
          function selectHandler(){
            if(chart.getSelection().length == 1){
               selection = chart.getSelection()[0];
               var guid = noteArray[selection.row][0];
               console.log(guid);
               var url = 'http://sandbox.evernote.com/Home.action?#'
                  + evernoteSearchParam + '=' + guid;
               console.log(url);
               window.open(url);
            }
          });
          })};
}
