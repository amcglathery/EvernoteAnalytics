""" Class is used to retreive statistics based on a user profile """
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
from evernote.edam.notestore.ttypes import *
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
from collections import defaultdict

class EvernoteStatistics:

   def __init__(self, profile=None):
      noteStoreHttpClient = THttpClient.THttpClient(profile.evernote_note_store_url)
      noteStoreProtocol =  TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
      self.noteStore = NoteStore.Client(noteStoreProtocol)
      self.profile = profile

   def get_notebooks(self):
      return self.noteStore.listNotebooks(self.profile.evernote_token)
   
#   def get_statistics_for_notebook(self, notebook=None):
 #     #Maybe don't need this? check out findNotecounts

   def get_number_of_notes(self, notebook=None):
      filt = NoteFilter()
      filt.notebookGuid = notebook.guid
      return self.noteStore.findNoteCounts(self.profile.evernote_token, 
        filt, False).notebookCounts[notebook.guid]
   
   def get_notes_in_notebooks(self):
      return self.noteStore.findNoteCounts(self.profile.evernote_token,
         NoteFilter(), False).notebookCounts.items()

   def get_notebook_name(self, notebookGuid):
      return self.noteStore.getNotebook(self.profile.evernote_token,
         notebookGuid).name
