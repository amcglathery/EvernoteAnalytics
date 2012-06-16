from django.conf.urls.defaults import *
from basic.views import *

urlpatterns = patterns( '',
     url( r'^notebook_json/$', notebook_count_json, name = 'notebook_json'),
)
