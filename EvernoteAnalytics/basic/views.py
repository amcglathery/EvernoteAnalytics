from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from evernote_auth import EvernoteAPI
from analytics import EvernoteStatistics
from account.models import UserProfile
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import logging
import json

def run_evernote_auth(request):
    """ Starts the OAuth token obtaining process by obtaining the token we use
        to request the user's token
    """
    callback_url = request.build_absolute_uri(reverse(
        'basic.views.login_evernote_token', args=[]))

    everAuth = EvernoteAPI()
    return everAuth.get_token(request, callback_url)

def get_evernote_token(request):
    """ View that handles the callback from the Evernote OAuth call and
        stores the OAuth token for the user
    """
    if request.user.is_authenticated():
        everAuth = EvernoteAPI()
        credentials = everAuth.get_user_token(request)
        # credentials here contain OAuth token, save it!
        profile = request.user.profile
        logging.error(credentials['expires'])
        try:
            expires_time = datetime.fromtimestamp(int(credentials['expires']))
        except TypeError:
            logging.error("Error parsing token expires time")
            expires_time = datetime.now()
        profile.evernote_token = credentials['oauth_token']
        profile.evernote_token_expires_time = expires_time
        profile.evernote_note_store_url = credentials['edam_noteStoreUrl']
        profile.save()
    return HttpResponseRedirect(reverse('basic.views.post_evernote_js_token',
        args=[]))

def login_evernote_token(request):
    """ as get_evernote_token(), but logs the user in as well
    """
    everAuth = EvernoteAPI()
    credentials = everAuth.get_user_token(request)
    if not credentials:
        return HttpResponseRedirect(reverse('account.views.login_page', args=[]))
    if request.user.is_authenticated():
        user = request.user
    else:
        evernoteHost = settings.EVERNOTE_HOST
        userStoreUri = "https://" + evernoteHost + "/edam/user"
        userStoreHttpClient = THttpClient.THttpClient(userStoreUri)
        userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
        userStore = UserStore.Client(userStoreProtocol)
        evernoteUser = userStore.getUser(credentials['oauth_token'])
        user = authenticate(username=evernoteUser.username, password=str(evernoteUser.id))
        if not user:
            newUser = User.objects.create_user(evernoteUser.username, evernoteUser.email, str(evernoteUser.id))
            names = evernoteUser.name.split() if evernoteUser.name else None
            newUser.first_name = names[0] if names and len(names) > 0 else ""
            newUser.last_name = names[1] if names and len(names) > 1 else ""
            newUser.save()
            user = authenticate(username=evernoteUser.username, password=str(evernoteUser.id))
        login(request, user)
    profile = request.user.profile
    try:
        expires_time = datetime.fromtimestamp(int(credentials['expires']))
    except TypeError:
        logging.error("Error parsing token expires time")
        expires_time = datetime.now()
    profile.evernote_token = credentials['oauth_token']
    profile.evernote_token_expires_time = expires_time
    profile.evernote_note_store_url = credentials['edam_noteStoreUrl']
    profile.save()
    return HttpResponseRedirect(reverse('basic.views.usage',
        args=[]))


def post_evernote_token(request):
    """ View that is called after a user has sucessfully received a token
        and displays information
    """
    eStats = EvernoteStatistics(request.user.profile)
#    qStats = eStats.get_quick_stats()
    qStats = eStats.get_quick_stats_created_recently(month=12)
    if qStats is None:
      return render_to_response('evernote_resp.html',
         {'numNotebooks' : "No notebooks found for the given time period",
          'notebooks' : "",
          'notes': "",
          'tags': "",
          'days': ""},
         context_instance=RequestContext(request))
    numNotebooks = "Found " + str(qStats['numberOfNotebooks']) + " notebooks:"

    notebookFrequency = qStats['notebookCounts']
    tagFrequency = qStats['tagCounts']
    notes =  "Found " + str(qStats['numberOfNotes']) + " notes"
    notebooks = "Found " + str(qStats['numberOfNotebooks']) + " notebooks:"
    tags = "Found " + str(qStats['numberOfTags']) + " tags: "

    for (notebook, frequency) in notebookFrequency.items():
      notebooks += eStats.get_notebook_name(notebook) + ": " + str(frequency) + " * "
    for (tag, frequency) in tagFrequency.items():
      tags += eStats.get_tag_name(tag) + ": " + str(frequency) + " * "

    dayFrequency = eStats.get_note_creation()
    days = "Number of notes created on the following days: "
    for (day, frequency) in dayFrequency.items():
      days += str(day) + ": " + str(frequency) + " * "

    return render_to_response('evernote_resp.html',
      {'numNotebooks' : numNotebooks,
       'notebooks' : notebooks,
       'notes' : notes,
       'tags'  : tags,
       'days'  : days},
      context_instance=RequestContext(request))

def post_evernote_js_token(request):
    """ Test view to work with JSON """
    profile = request.user.profile
    return render_to_response('evernote_js_resp.html',{},
      context_instance=RequestContext(request))

@login_required(login_url='/login/')
def organization(request):
    eStats = EvernoteStatistics(request.user.profile)
    t = eStats.get_first_note_timestamp()
    return render_to_response('organization.html', {'firstNote': t},
      context_instance=RequestContext(request))

@login_required(login_url='/login/')
def usage(request):
    eStats = EvernoteStatistics(request.user.profile)
    t = eStats.get_first_note_timestamp()
    return render_to_response('usage.html', {'firstNote': t},
      context_instance=RequestContext(request))

@login_required(login_url='/login/')
def tags(request):
    eStats = EvernoteStatistics(request.user.profile)
    t = eStats.get_first_note_timestamp()
    return render_to_response('tags.html', {'firstNote': t},
      context_instance=RequestContext(request))

@login_required(login_url='/login/')
def notebooks(request):
    eStats = EvernoteStatistics(request.user.profile)
    t = eStats.get_first_note_timestamp()
    return render_to_response('notebooks.html', {'firstNote': t},
      context_instance=RequestContext(request))

@login_required(login_url='/login/')
def map(request):
    eStats = EvernoteStatistics(request.user.profile)
    t = eStats.get_first_note_timestamp()
    return render_to_response('map.html', {'firstNote': t},
      context_instance=RequestContext(request))

@login_required(login_url='/login/')
def wordcloud(request):
    eStats = EvernoteStatistics(request.user.profile)
    t = eStats.get_first_note_timestamp()
    notebooks = eStats.get_guid_map(notebookNames=True, tagNames=False).items()
    tags = eStats.get_guid_map(notebookNames=False, tagNames=True).items()
    return render_to_response('wordcloud.html', 
      {'firstNote': t,
       'notebooks': notebooks,
       'tags': tags},
      context_instance=RequestContext(request))

def aboutus(request):
    request.user.profile.notes_word_count = None
    request.user.profile.last_update = None
    request.user.profile.word_cloud_done = False
    request.user.profile.save()
    return render_to_response('about.html', {},
      context_instance=RequestContext(request))

def notebook_count_json(request):
    if request.method == 'GET':
      GET = request.GET
      if GET.has_key('sDate') and GET.has_key('eDate'):
         eStats = EvernoteStatistics(request.user.profile)
         startDate = date.fromtimestamp(float(GET['sDate'])/1000)
         endDate = date.fromtimestamp(float(GET['eDate'])/1000)
         filt = eStats.create_date_filter(startDate, endDate)
         qStats = eStats.get_quick_stats(filt)
         if qStats is None:
            return HttpResponse({},content_type='application/json')
         guidToNameMap = eStats.get_guid_map(notebookNames=True)
         noteFrequency = qStats['notebookCounts']
         notebookArray = [[k,v] for k,v in noteFrequency.iteritems()]
         jsonText = json.dumps({'keyToDisplayMap': guidToNameMap,
                                'noteArray': notebookArray,
                                'displayObjectName': 'Notebook',
                                'evernoteSearchParam' : 'b'})
         return HttpResponse(jsonText,content_type='application/json')

def tag_count_json(request):
    if request.method == 'GET':
      GET = request.GET
      if GET.has_key('sDate') and GET.has_key('eDate'):
         eStats = EvernoteStatistics(request.user.profile)
         startDate = date.fromtimestamp(float(GET['sDate'])/1000)
         endDate = date.fromtimestamp(float(GET['eDate'])/1000)
         filt = eStats.create_date_filter(startDate, endDate)
         qStats = eStats.get_quick_stats(filt)
         if qStats is None:
            return HttpResponse({},content_type='application/json')
         guidToNameMap = eStats.get_guid_map(tagNames=True, notebookNames=False)
         tagFrequency = qStats['tagCounts']
         tagArray = [[k,v] for k,v in tagFrequency.iteritems()]
         jsonText = json.dumps({'keyToDisplayMap': guidToNameMap,
                                'noteArray': tagArray,
                                'displayObjectName': 'Tag',
                                'evernoteSearchParam': 't'})
         return HttpResponse(jsonText,content_type='application/json')

def day_count_json(request):
    if request.method == 'GET':
      GET = request.GET
      if GET.has_key('sDate') and GET.has_key('eDate'):
         eStats = EvernoteStatistics(request.user.profile)
         startDate = date.fromtimestamp(float(GET['sDate'])/1000)
         endDate = date.fromtimestamp(float(GET['eDate'])/1000)
         filt = eStats.create_date_filter(startDate, endDate)
         noteMetadata = eStats.get_note_metadata(filt)
         if noteMetadata is None:
            return HttpResponse({},content_type='application/json')
         dayFrequency = noteMetadata['dayCounter']
         intToDayMap = {0: "Sunday", 1: "Monday", 2: "Tuesday",
                        3: "Wednesday", 4: "Thursday", 5: "Friday",
                        6: "Saturday"}
         daysArray = [[x,0] for x in intToDayMap.values()]
         for (k,v) in dayFrequency.iteritems():
            daysArray[k][1] = v
         jsonText = json.dumps({'categoryCounts': daysArray,
                                'categoryTitle': 'Day'})
         return HttpResponse(jsonText,content_type='application/json')

def month_count_json(request):
    if request.method == 'GET':
      GET = request.GET
      if GET.has_key('sDate') and GET.has_key('eDate'):
         eStats = EvernoteStatistics(request.user.profile)
         startDate = date.fromtimestamp(float(GET['sDate'])/1000)
         endDate = date.fromtimestamp(float(GET['eDate'])/1000)
         filt = eStats.create_date_filter(startDate, endDate)
         noteMetadata = eStats.get_note_metadata(filt)
         if noteMetadata is None:
            return HttpResponse({},content_type='application/json')
         monthFrequency = noteMetadata['monthCounter']
         intToMonthMap = {1: "January", 2: "February", 3: "March",
                          4: "April", 5: "May", 6: "June",
                          7: "July", 8: "August", 9: "September",
                         10: "October", 11: "November", 12: "December"}
         monthsArray = [[x,0] for x in intToMonthMap.values()]
         for (k,v) in monthFrequency.iteritems():
            monthsArray[k-1][1] = v
         jsonText = json.dumps({'categoryCounts': monthsArray,
                                'categoryTitle': 'Month'})
         return HttpResponse(jsonText,content_type='application/json')

def geo_loc_json(request):
    if request.method == 'GET':
      GET = request.GET
      if GET.has_key('sDate') and GET.has_key('eDate'):
         eStats = EvernoteStatistics(request.user.profile)
         startDate = date.fromtimestamp(float(GET['sDate'])/1000)
         endDate = date.fromtimestamp(float(GET['eDate'])/1000)
         filt = eStats.create_date_filter(startDate, endDate)
         noteMetadata = eStats.get_note_metadata(filt)
         if noteMetadata is None:
            return HttpResponse({},content_type='application/json')
         jsonText = json.dumps({'points' : noteMetadata['geoLocations']})
         return HttpResponse(jsonText,content_type='application/json')

def word_count_json(request):
    if request.method == 'GET':
      GET = request.GET
      if GET.has_key('sDate') and GET.has_key('eDate'):
         eStats = EvernoteStatistics(request.user.profile)
         startDate = date.fromtimestamp(float(GET['sDate'])/1000)
         endDate = date.fromtimestamp(float(GET['eDate'])/1000)
         filt = eStats.create_date_filter(startDate, endDate)
         wordCount = eStats.get_word_count(filt, numWords=200)
         #what happens when no data?
         jsonText = json.dumps({'words' : wordCount})
         return HttpResponse(jsonText,content_type='application/json')

def word_update(request):
   if request.method == 'GET':
      eStats = EvernoteStatistics(request.user.profile)
      eStats.update_word_count()
   return HttpResponse("",content_type='application/json') 
