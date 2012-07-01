from django.conf.urls.defaults import patterns, include, url
from settings import STATIC_ROOT
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^$', 'account.views.home_page'),
    url(r'^login/$', 'account.views.login_page' ),
   # uncomment and comment out other post token to get original page
   # url('^post_token/$', 'basic.views.post_evernote_token'),
    url('^organization/$', 'basic.views.organization'),
    url('^usage/$', 'basic.views.usage'),
    url('^tags/$', 'basic.views.tags'),
    url('^notebooks/$', 'basic.views.notebooks'),
    url('^map/$', 'basic.views.map'),
    url('^wordcloud/$', 'basic.views.wordcloud'),
    url('^aboutus/$', 'basic.views.aboutus'),
    url('^post_token/$', 'basic.views.post_evernote_js_token'),
    url('^auth/gettok/$', 'basic.views.run_evernote_auth'),
    url('^auth/usertok/$', 'basic.views.get_evernote_token'),
    url('^auth/login/$', 'basic.views.login_evernote_token'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': STATIC_ROOT}),
    url(r'^account/', include('account.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^data/', include('basic.urls')),
)

