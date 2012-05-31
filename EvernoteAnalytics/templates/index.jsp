<%-- 

  Demonstrates the use of OAuth to authenticate to the Evernote API.

  Learn more at http://dev.evernote.com/documentation/cloud/chapters/Authentication.php
  
  Copyright 2008-2012 Evernote Corporation. All rights reserved.

--%>
<%@page import="org.jsoup.Jsoup"%>
<%@page import="edu.tufts.evernoteanalytics.GeoLocation"%>
<%@page import="java.util.Map.Entry"%>
<%@page import="edu.tufts.evernoteanalytics.HashCounter"%>
<%@ page import='java.util.*' %>
<%@ page import='java.net.*' %>
<%@ page import='org.json.simple.*' %>
<%@ page import='org.apache.thrift.*' %>
<%@ page import='org.apache.thrift.protocol.TBinaryProtocol' %>
<%@ page import='org.apache.thrift.transport.THttpClient' %>
<%@ page import='com.evernote.edam.type.*' %>
<%@ page import='com.evernote.edam.notestore.*' %>
<%@ page import='com.evernote.oauth.consumer.*' %>
<!DOCTYPE html>
<html>
    <head>
        <link rel ="stylesheet" href="css/bootstrap.css"/>
        <link rel ="stylesheet" href="css/bootstrap-responsive.css"/>
        <link rel="stylesheet" href="amanda/cloud.css" type="text/css" />
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
        <link rel="stylesheet" href="amanda/gmaps.css" type="text/css" />
        <script type="text/javascript" src="amanda/jquery-1.7.2.min.js"></script>
        <script type="text/javascript" src="amanda/jquery.tagcloud-2.js"></script>

        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>


        <style type="text/css">
            body {
                padding-top: 60px;
                padding-bottom: 40px;
                padding-right: auto;
                padding-left: auto;
            }
        </style>
        <title>Evernote Analytics</title>
    </head>

    <%!    /*
         * Replace these values with the API consumer key and consumer secret
         * that you receive from Evernote. If you do not have an Evernote API
         * key, you can request one at
         * http://www.evernote.com/about/developer/api/
         */
        static final String consumerKey = "mrussell13";//"en-oauth-test";
        static final String consumerSecret = "6712f2aeea0ea6bc";//"0123456789abcdef";
        /*
         * Replace this value with https://www.evernote.com to switch from the
         * Evernote sandbox server to the Evernote production server.
         */
        static String content = "";
        static final String urlBase = "https://sandbox.evernote.com";
        static final String requestTokenUrl = urlBase + "/oauth";
        static final String accessTokenUrl = urlBase + "/oauth";
        static final String authorizationUrlBase = urlBase + "/OAuth.action";
        static final String callbackUrl = "index.jsp?action=callbackReturn";
    %>
    <%
        String accessToken = (String) session.getAttribute("accessToken");
        String requestToken = (String) session.getAttribute("requestToken");
        String verifier = (String) session.getAttribute("verifier");

        String action = request.getParameter("action");

        if ("en-oauth-test".equals(consumerKey)) {
    %>
    <%} else {
        if (action != null) {
    %>
    <body onload="gmapswindow()">
        <%

            try {
                if ("reset".equals(action)) {
                    //    System.err.println("Resetting");
                    // Empty the server's stored session information for the current
                    // browser user so we can redo the test.
                    for (Enumeration<?> names = session.getAttributeNames();
                            names.hasMoreElements();) {
                        session.removeAttribute((String) names.nextElement());
                    }
                    accessToken = null;
                    requestToken = null;
                    verifier = null;

                } else if ("getRequestToken".equals(action)) {
                    // Send an OAuth message to the Provider asking for a new Request
                    // Token because we don't have access to the current user's account.
                    SimpleOAuthRequest oauthRequestor =
                            new SimpleOAuthRequest(requestTokenUrl, consumerKey, consumerSecret, null);

                    // Set the callback URL
                    String thisUrl = request.getRequestURL().toString();
                    String cbUrl = thisUrl.substring(0, thisUrl.lastIndexOf('/') + 1) + callbackUrl;
                    oauthRequestor.setParameter("oauth_callback", cbUrl);

                    Map<String, String> reply = oauthRequestor.sendRequest();
                    requestToken = reply.get("oauth_token");
                    session.setAttribute("requestToken", requestToken);

                } else if ("getAccessToken".equals(action)) {
                    // Send an OAuth message to the Provider asking to exchange the
                    // existing Request Token for an Access Token
                    SimpleOAuthRequest oauthRequestor =
                            new SimpleOAuthRequest(requestTokenUrl, consumerKey, consumerSecret, null);
                    oauthRequestor.setParameter("oauth_token",
                            (String) session.getAttribute("requestToken"));
                    oauthRequestor.setParameter("oauth_verifier",
                            (String) session.getAttribute("verifier"));
                    Map<String, String> reply = oauthRequestor.sendRequest();
                    accessToken = reply.get("oauth_token");
                    String noteStoreUrl = reply.get("edam_noteStoreUrl");
                    session.setAttribute("accessToken", accessToken);
                    session.setAttribute("noteStoreUrl", noteStoreUrl);

                } else if ("callbackReturn".equals(action)) {
                    requestToken = request.getParameter("oauth_token");
                    verifier = request.getParameter("oauth_verifier");
                    session.setAttribute("verifier", verifier);
                } else if ("listNotebooks".equals(action)) {
                    String noteStoreUrl = (String) session.getAttribute("noteStoreUrl");
                    THttpClient noteStoreTrans = new THttpClient(noteStoreUrl);
                    TBinaryProtocol noteStoreProt = new TBinaryProtocol(noteStoreTrans);
                    NoteStore.Client noteStore = new NoteStore.Client(noteStoreProt, noteStoreProt);

                  /*  HashCounter<Integer> timeCounter = new HashCounter<Integer>();
                    JSONArray jsonTimeCounters = new JSONArray();*/

                    HashCounter<String> notebookCounter = new HashCounter<String>();
                    JSONArray jsonNotebookCounters = new JSONArray();
                    
                    HashCounter<Integer> dayCounter = new HashCounter<Integer>();
                    JSONArray jsonDayCounters = new JSONArray();

                    HashCounter<String> wordCounter = new HashCounter<String>();
                    JSONArray jsonWordCounters = new JSONArray();

                    List<GeoLocation> geoLocations = new ArrayList<GeoLocation>();
                    JSONArray jsonGeoLocations = new JSONArray();

                    HashCounter<String> tagCounters = new HashCounter<String>();
                    JSONArray jsonTagCounters = new JSONArray();

                    List<Notebook> notebooks = noteStore.listNotebooks(accessToken);
                    for (Notebook notebook : notebooks) {
                        NoteFilter filter = new NoteFilter();
                        filter.setNotebookGuid(notebook.getGuid());
                        List<Note> notes = noteStore.findNotes(accessToken, filter, 0, 15).getNotes();
                        for (Note n : notes) {
                            String htmlcontent = Jsoup.parse(noteStore.getNoteContent(accessToken, n.getGuid())).text().replaceAll("[.,]", "");
                            String[] words = htmlcontent.toLowerCase().split("\\s+");
                            for (String s : words) {
                                if (s.length() > 3) {
                                    wordCounter.add(s);
                                }
                            }
                            GregorianCalendar cdate = new GregorianCalendar();
                            cdate.setTimeInMillis(n.getCreated());
                            dayCounter.add(cdate.get(GregorianCalendar.DAY_OF_WEEK));
                            //timeCounter.add(cdate.get(GregorianCalendar.HOUR_OF_DAY));
                            double lat = n.getAttributes().getLatitude();
                            double lng = n.getAttributes().getLongitude();
                            if (lat != 0.00 && lng != 0.00) {
                                geoLocations.add(new GeoLocation(lat, lng));
                            }
                            List<String> tags = noteStore.getNoteTagNames(accessToken, n.getGuid());
                            for (String t : tags) {
                                tagCounters.add(t);
                            }
                            notebookCounter.add(notebook.getName());
                            //tagCounters.add("Test tag");
                        }
                    }

                    for (Entry<Integer, Integer> e : dayCounter.getEntrySet()) {
                        int dayInt = e.getKey();
                        JSONObject dayObject = new JSONObject();
                        dayObject.put("day", dayInt);
                        dayObject.put("count", e.getValue());
                        jsonDayCounters.add(dayObject);
                    }

          /*          for (Entry<Integer, Integer> e : timeCounter.getEntrySet()) {
                        JSONObject hourCount = new JSONObject();
                        hourCount.put("hour", e.getKey());
                        hourCount.put("count", e.getValue());
                        jsonTimeCounters.add(hourCount);

                    }*/
                    for (GeoLocation g : geoLocations) {
                        JSONObject jsonGeo = new JSONObject();
                        jsonGeo.put("lat", g.getLatitude());
                        jsonGeo.put("lng", g.getLongitude());
                        jsonGeoLocations.add(jsonGeo);
                    }
                    for (Entry<String, Integer> e : wordCounter.getTopx(100)) {
                        JSONObject wordCount = new JSONObject();
                        wordCount.put("tag", e.getKey());
                        wordCount.put("count", e.getValue());
                        jsonWordCounters.add(wordCount);
                    }

                    for (Entry<String, Integer> e : tagCounters.getEntrySet()) {
                        JSONObject tagCounter = new JSONObject();
                        tagCounter.put("tag", e.getKey());
                        tagCounter.put("count", e.getValue());
                        jsonTagCounters.add(tagCounter);
                    }
                    
                    for (Entry<String, Integer> e : notebookCounter.getEntrySet()) {
                        JSONObject notebookCount = new JSONObject();
                        notebookCount.put("notebook", e.getKey());
                        notebookCount.put("count", e.getValue());
                        jsonNotebookCounters.add(notebookCount);
                    }
                    
                    out.println("<script type=\"text/javascript\">");
                    out.println("var dayCount=" + jsonDayCounters);
                    //out.println("var timeCount=" + jsonTimeCounters);
                    out.println("var geoLoc=" + jsonGeoLocations);
                    out.println("var wordCount=" + jsonWordCounters);
                    out.println("var noteCount=" + jsonNotebookCounters);
                    out.println("</script>");


                }
            } catch (Exception e) {
                e.printStackTrace();
                out.println(e.toString());
            }

        %>
        <% }%>

        <!-- Information used by consumer -->
        <!--<h3>Evernote EDAM API Web Test State</h3>
        Consumer key: <%= consumerKey%><br/>
        Request token URL: <%= requestTokenUrl%><br/>
        Access token URL: <%= accessTokenUrl%><br/>
        Authorization URL Base: <%= authorizationUrlBase%><br/>
        <br/>
        User request token: <%= session.getAttribute("requestToken")%><br/>
        User oauth verifier: <%= session.getAttribute("verifier")%><br/>
        User access token: <%= session.getAttribute("accessToken")%><br/>-->


        <!-- Step 1 in OAuth authorization: obtain an unauthorized request token from the provider -->


        <script type="text/javascript">
            google.load("visualization", "1", {packages:["corechart"]});
            google.setOnLoadCallback(drawChart);
            function drawChart() {
                var ret = Array(["Sunday",0],["Monday",0],["Tuesday",0],["Wednesday",0],["Thursday",0],["Friday",0],["Saturday",0]);
                $.each(dayCount, function(i,obj){
                    ret[obj['day']-1] = [ret[obj['day']-1][0],obj['count']];
                })
                var data = new google.visualization.DataTable();
                data.addColumn('string', 'Day');
                data.addColumn('number', 'Total Notes');
                data.addRows(ret);
                var options = {
                    title: '',
                    hAxis: {title: 'Days', titleTextStyle: {color: 'purple'}}
                };

                var chart = new google.visualization.ColumnChart(document.getElementById('chart'));
                chart.draw(data, options);
            }
        </script>
        <div class="navbar navbar-fixed-top">
            <div class="container" style="background: #000000">
                <a class="brand" style="margin-left: 20px; margin-top: 12px">Analysis of Notes</a>
                <div class="nav-collapse">
                    <ul class="nav">
                        <li class="active" style="margin-top: 12px">
                            <% if (requestToken == null && accessToken == null) {%>
                            <a href='?action=getRequestToken'>Get OAuth Request Token</a><br/>
                            <% } else if (requestToken != null && verifier == null && accessToken == null) {
                                String authorizationUrl = authorizationUrlBase + "?oauth_token=" + requestToken;
                            %>
                            <a href='<%= authorizationUrl%>'>Send user to get authorization</a><br/>
                            <% } else if (requestToken != null && verifier != null && accessToken == null) {%>
                            <a href="?action=getAccessToken">
                                Get OAuth Access Token from Provider
                            </a><br/>
                            <% } else if (accessToken != null) {%>
                            <a href="?action=listNotebooks">List notebooks in account</a><br/>
                            <% }%>
                        </li>
                        <li class="active" style="margin-top: 12px">
                            <a href="?action=reset">Reset user session</a>
                            <% }%>
                        </li>
                    </ul>
                </div>
            </div>	
        </div>
        <div class="container" style="margin-top:20px">
            <div class="row">
                <div class="span12" style="background: #ffffff">
                    <h2>Total Posts by Day</h2>
                    <div id="chart"></div>
                </div>
            </div>

            <div class="row" style="">
                <div class="span5"  style="text-align: center; margin-top: 10%; vertical-align: center">
                    <h2>Most Common Words</h2>
                    <div id="tagcloud"></div>
                    <script type="text/javascript">
                        var tags = wordCount;
                        $("#tagcloud").tagCloud(tags);
                        var children = document.getElementById('tagcloud').childNodes;
                        for (var i=0; i<children.length; i=i+2)
                        {
                            //                            console.log(children)
                            children[i].style.color = '#'+Math.floor(Math.random()*16777215).toString(16);
                        }
                    </script>

                </div>  

                <div class="span5" style="text-align: center; margin-left: auto; margin-right: auto;">
                    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
                    <script type="text/javascript">
                        google.load("visualization", "1", {packages:["corechart"]});
                        google.setOnLoadCallback(drawChart);
                        function drawChart() {
                            var data = new google.visualization.DataTable();
//                            console.log(noteCount);
                            var ret = Array();
                            $.each(noteCount, function(i,obj){
                                ret.push([obj['notebook'],obj['count']]);
                            })
//                            console.log(data);
                            data.addColumn('string', 'Notebook');
                            data.addColumn('number', 'Numbers of Notes');
                            data.addRows(ret);
                            var options = {
                                title: 'Posts per Notebook'
                            };

                            var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
                            chart.draw(data, options);
                        }
                    </script>
                    <div id="chart_div" style="width: 900px; height: 500px;"></div>


                </div>
                <br /><br />
                <div class="span12" style="margin-top: 20px">
                    <h2> Geotags of posts </h2>
                    <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=true"></script>
                    <script type="text/javascript">
                        function gmapswindow()
                        {
                            var ret = Array();
                            $.each(geoLoc, function(i,obj){
                                ret.push(['',obj['lat'],obj['lng']]);
                            })
                
                            var points = ret;
                            var center = [42.408, -71.120]
                            var landmark = new google.maps.LatLng(center[0],center[1]);
                            var myOptions = {
                                zoom: 12, // The larger the zoom number, the bigger the zoom
                                center: landmark,
                                mapTypeId: google.maps.MapTypeId.ROADMAP
                            };
                            var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);   
                            var elephant = 'amanda/evernote.jpg';	
                            for (i = 0; i<points.length; i++)	
                            {
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
                    </script>
                    <div id="map_canvas"></div>
                    <div id="loc"></div>
                </div></div>

        </div>
    </div>
    <!-- Google maps -->


</body> 
</html>
