function createMap(jsonUrl, iconUrl, divElement, startDate, endDate, 
                   center, zoomLvl){
   if (center==null){
      center = [42.408, -71.120];
   }
   if (zoomLvl==null){
      zoomLvl = 12;
   }
   var landmark = new google.maps.LatLng(center[0],center[1]);
   var myOptions = {
         zoom: zoomLvl, // The larger the zoom number, the bigger the zoom
         center: landmark,
         mapTypeId: google.maps.MapTypeId.ROADMAP
   };
   var map = new google.maps.Map($('#'+divElement).get(0),myOptions);
   $.getJSON(jsonUrl,{sDate: startDate, eDate: endDate},
      function(json){
        if (json == null) {
            //Make this look better
            $('#'+divElement).html("No data found");
            return;
          }
        var points = json['points']
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
   })
   return map;
}

function createBarGraph(jsonUrl, divElement, startDate, endDate){
   $.getJSON(jsonUrl,{sDate: startDate, eDate: endDate},
      function(json){
        if (json == null) {
            //Make this look better
            $('#'+divElement).html("No data found");
            return;
        }
      var data = new google.visualization.DataTable();
      var categoryTitle = json['categoryTitle']
      data.addColumn('string', categoryTitle);
      data.addColumn('number', 'Total Notes');
      data.addRows(json['categoryCounts']);
      var options = {
         title: 'Posts per ' + categoryTitle,
         hAxis: {title: categoryTitle + 's', titleTextStyle: {color: 'purple'}}
                    };
      var chart = new google.visualization.ColumnChart($('#'+divElement).get(0));
      chart.draw(data, options);
  });
}

function createPieChart(jsonUrl, divElement, startDate, endDate, clickUrl){
     $.getJSON(jsonUrl,{sDate: startDate, eDate: endDate},
       function(json){
          if (json == null) {
            //Make this look better
            $('#'+divElement).removeClass('load')
            $('#'+divElement).html("<p style='text-align: center; padding-top: 20%'>No data was found for the dates you selected.</p>");
            return;
          }
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
          function(){
            if(chart.getSelection().length == 1){
               selection = chart.getSelection()[0];
               var guid = noteArray[selection.row][0];
               //console.log(guid);
               var url = clickUrl
                  + evernoteSearchParam + '=' + guid;
               //console.log(url);
               window.open(url);
            }
          });
          })
}

function createWordCloud(jsonUrl, divElement, startDate, endDate, guid, 
                         guidParam){
     var params = {sDate: startDate, eDate: endDate};
     if (guid != null) {
        params[guidParam] = guid;
     }
     $.getJSON(jsonUrl,params,
       function(json){
         if (json['words'].length == 0){
            $('#'+divElement).html("<p style='text-align: center; padding-top: 20%'>No data was found for the dates you selected.</p>");
            return;
         }
         $("#"+divElement).tagCloud(json['words']);
         var children = document.getElementById('tagcloud').childNodes;
         for (var i=0; i<children.length; i=i+2){
           children[i].style.color = '#'+Math.floor(Math.random()*16777215).toString(16);
         }
       });
}

function createLineGraph(jsonUrl, divElement, startDate, endDate, guid, 
                         guidParam){
   var params = {sDate: startDate, eDate: endDate};
   if (guid != null) {
      params[guidParam] = guid;
   }
   $.getJSON(jsonUrl, params, 
      function(json){
         var data = google.visualization.arrayToDataTable(json['data']);
         var options = {
            title: json['title']
         };
         var chart = new google.visualization.LineChart($('#'+divElement).get(0));
         chart.draw(data, options);
      });
}
