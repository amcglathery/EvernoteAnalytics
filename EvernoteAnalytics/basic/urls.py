from django.conf.urls.defaults import *
from basic.views import *

urlpatterns = patterns( '',
     url( r'^notebook_json/$', notebook_count_json, name = 'notebook_count_json'),
     url( r'^tag_json/$', tag_count_json, name = 'tag_count_json'),
     url( r'^days_json/$', day_count_json, name = 'day_count_json'),
     url( r'^geoloc_json/$', geo_loc_json, name = 'geo_loc_json'),
     url( r'^word_json/$', word_count_json, name = 'word_count_json'),
     url( r'^month_json/$', month_count_json, name = 'month_count_json'),
)
