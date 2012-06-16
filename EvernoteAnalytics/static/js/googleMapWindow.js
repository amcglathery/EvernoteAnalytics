//Needs jquery and jsapi before invoking
//Takes in as arguments:
//points - Array of [pointTitle, lat, long]
//iconurl - url for icon displays
//name for the div element
 function gmapsWindow(points, iconUrl, elementName){
  return function() {
    var center = [42.408, -71.120]
    var landmark = new google.maps.LatLng(center[0],center[1]);
    var myOptions = {
     zoom: 12, // The larger the zoom number, the bigger the zoom
     center: landmark,
     mapTypeId: google.maps.MapTypeId.ROADMAP
     };
    var map = new google.maps.Map(document.getElementById("map_canvas"),myOptions);
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
  }
}