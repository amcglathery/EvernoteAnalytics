from datetime import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from evernote_auth import EvernoteAPI
from analytics import EvernoteStatistics
import logging

def landing(request):
    return render_to_response('home.html', {},
            context_instance=RequestContext(request))

def run_evernote_auth(request):
    """ Starts the OAuth token obtaining process by obtaining the token we use
        to request the user's token
    """
    callback_url = request.build_absolute_uri(reverse(
        'basic.views.get_evernote_token', args=[]))

    everAuth = EvernoteAPI()
    return everAuth.get_token(request, callback_url)

def get_evernote_token(request):
    """ View that handles the callback from the Evernote OAuth call and
        stores the OAuth token for the user
    """
    if request.user.is_authenticated:
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
        evernoteHost = "sandbox.evernote.com"
        userStoreUri = "https://" + evernoteHost + "/edam/user"

        profile.save()
    return HttpResponseRedirect(reverse('basic.views.post_evernote_token',
        args=[]))

def post_evernote_token(request):
    evernoteStats = EvernoteStatistics(request.user.profile)
    notebooks = evernoteStats.get_notebooks()

    #Get's specific notebook information after displaying total
    #number of notebooks
    numNotebooks = "Found " + str(len(notebooks)) + " notebooks:"
    notebookSelection = "For notebook " + notebooks[0].name + ":"
    
    noteStats = evernoteStats.get_stats_for_notebook(notebooks[0])
    tagFrequency = noteStats['tagCounter']
    numNotes = noteStats['numberOfNotes']
    notes =  "Found " + str(numNotes) + " notes"
    tags = "Found " + str(len(tagFrequency)) + " tags: "
    
    for (tag, frequency) in tagFrequency.items():
         tags += tag + ": " + str(frequency) + "* "
    return render_to_response('evernote_resp.html', 
      {'numNotebooks' : numNotebooks, 
       'notebookSelection' : notebookSelection,
       'notes' : notes,
       'tags'  : tags}, 
      context_instance=RequestContext(request))
