""" Class is used to retreive statistics based on a user profile """
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
from evernote.edam.notestore.ttypes import *
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
from collections import defaultdict
from datetime import date

class EvernoteStatistics:

   def __init__(self, profile=None):
      noteStoreHttpClient = THttpClient.THttpClient(profile.evernote_note_store_url)
      noteStoreProtocol =  TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
      self.noteStore = NoteStore.Client(noteStoreProtocol)
      self.profile = profile

   def get_notebooks(self):
      return self.noteStore.listNotebooks(self.profile.evernote_token)
 
 #  def get_statistics_for_notebook(self, notebook=None):
 #  Maybe don't need this? check out findNotecounts

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

   def get_notes_in_tags(self):
      return self.noteStore.findNoteCounts(self.profile.evernote_token,
         NoteFilter(), False).tagCounts.items()

   def get_tag_name(self, tagGuid):
      return self.noteStore.getTag(self.profile.evernote_token, 
         tagGuid).name

   def get_stats_for_notebook(self, notebook):
      nf = NoteFilter()
      nf.notebookGuid = notebook.guid
      return self.get_notes_statistics(nf, 0, 25)
   
   def get_notes_statistics(self, notefilter, offset, maxnotes):
      notebookCounter = defaultdict(int)
      tagCounter = defaultdict(int)
      dayCounter = defaultdict(int)
      numNotes = 0
      noteList = self.noteStore.findNotes(self.profile.evernote_token,
         notefilter, offset, maxnotes).notes
      for note in noteList:
            #Should get body of notes
           # d = date.fromtimestamp(note.created)
           # dayCounter[d.day] += 1
         numNotes += 1
         notebookCounter[self.get_notebook_name(notefilter.notebookGuid)] += 1
         tags = self.noteStore.getNoteTagNames(self.profile.evernote_token, 
           note.guid)
         for tag in tags:
            tagCounter[tag] += 1
      return {'notebookCounter' : notebookCounter, 
              'tagCounter' : tagCounter, 
              'dayCounter' : dayCounter,
              'numberOfNotes' : numNotes}
