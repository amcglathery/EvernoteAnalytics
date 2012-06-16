from datetime import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from evernote_auth import EvernoteAPI
from analytics import EvernoteStatistics
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import logging
import json

def landing(request):
    return render_to_response('home.html', {},
            context_instance=RequestContext(request))

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
    if request.user.is_authenticated():
        user = request.user
    else:
        evernoteHost = "sandbox.evernote.com"
        userStoreUri = "https://" + evernoteHost + "/edam/user"
        userStoreHttpClient = THttpClient.THttpClient(userStoreUri)
        userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
        userStore = UserStore.Client(userStoreProtocol)
        evernoteUser = userStore.getUser(credentials['oauth_token'])
        user = authenticate(user=evernoteUser.username, password=evernoteUser.id)
        if not user:
            newUser = User.objects.create_user(evernoteUser.username, evernoteUser.email, evernoteUser.id)
            names = evernoteUser.name.split() if evernoteUser.name else None
            newUser.first_name = names[0] if names and len(names) > 0 else ""
            newUser.last_name = names[1] if names and len(names) > 1 else ""
            newUser.save()
            user = authenticate(user=evernoteUser.username, password=evernoteUser.id)
        login(request, user)
    try:
        expires_time = datetime.fromtimestamp(int(credentials['expires']))
    except TypeError:
        logging.error("Error parsing token expires time")
        expires_time = datetime.now()
    user.profile.evernote_token = credentials['oauth_token']
    user.profile.evernote_token_expires_time = expires_time
    user.profile.evernote_note_store_url = credentials['edam_noteStoreUrl']
    user.save()
    return HttpResponseRedirect(reverse('basic.views.post_evernote_js_token',
        args=[]))


def post_evernote_token(request):
    """ View that is called after a user has sucessfully received a token
        and displays information
    """
    eStats = EvernoteStatistics(request.user.profile)
#    qStats = eStats.get_quick_stats()
    qStats = eStats.get_quick_stats_created_recently(month=2)
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
    eStats = EvernoteStatistics(request.user.profile)
    qStats = eStats.get_quick_stats_created_recently(month=2)
    if qStats is None:
      return render_to_response('evernote_resp.html',
         {'numNotebooks' : "No notebooks found for the given time period",
          'notebooks' : "",
          'notes': "",
          'tags': "",
          'days': ""},
         context_instance=RequestContext(request))
    numNotebooks = "Found " + str(qStats['numberOfNotebooks']) + " notebooks:"
    guidToNameMap = eStats.get_guid_map(notebookNames=True, tagNames=True)
    notebookFrequency = qStats['notebookCounts']
    tagFrequency = qStats['tagCounts']
    noteMetadata = eStats.get_note_metadata()
    dayFrequency = noteMetadata['dayCounter']
    geoLocations = noteMetadata['geoLocations']
    return render_to_response('evernote_js_resp.html',
      {'notebookFrequency' : json.dumps(notebookFrequency,separators=(',',':')),
       'tagFrequency' : json.dumps(tagFrequency, separators=(',',':')),
       'dayFrequency' : json.dumps(dayFrequency, separators=(',',':')),
       'geoLocations' : geoLocations,
       'guidMap'  : guidToNameMap},
      context_instance=RequestContext(request))
