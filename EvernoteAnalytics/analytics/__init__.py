""" Class is used to retreive statistics based on a user profile """
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
from evernote.edam.notestore.ttypes import *
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
from collections import defaultdict
from datetime import date, timedelta
from monthdelta import monthdelta

class EvernoteStatistics:

   def __init__(self, profile=None):
      noteStoreHttpClient = THttpClient.THttpClient(profile.evernote_note_store_url)
      noteStoreProtocol =  TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
      self.noteStore = NoteStore.Client(noteStoreProtocol)
      self.profile = profile

   def get_notebooks(self):
      return self.noteStore.listNotebooks(self.profile.evernote_token)
 
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

   def get_quick_stats_created_recently(self, day=0, week=0, month=0, year=0):
      """ returns quick stats for notes created since x days/weeks/months/years.
      """
      nf = NoteFilter()
      d = (date.today() - timedelta(days=day,weeks=week)) - monthdelta(months=month + year * 12)
      nf.words = "created:" + d.strftime("%Y%m%d")
      return self.get_quick_stats(nf)
   
   def get_quick_stats(self, noteFilter=NoteFilter()):
      """ Returns (fairly quickly) basic statistics regarding a user and their
           notes for a given filter. No filter will return all the notes for
           a given user
      """
      noteCounts = self.noteStore.findNoteCounts(self.profile.evernote_token,
         noteFilter, False)
      if noteCounts.notebookCounts is None:
         return None
      return {'numberOfNotes' : reduce(lambda x, y: x+y,
                noteCounts.notebookCounts.itervalues()),
              'numberOfNotebooks' : len(noteCounts.notebookCounts),
              'numberOfTags' : len(noteCounts.tagCounts),
              'notebookCounts' : noteCounts.notebookCounts, 
              'tagCounts' : noteCounts.tagCounts}

   def get_note_creation(self, noteFilter=NoteFilter()):
      """ Returns a mapping between weekdays and notes"""
      noteMetadataList = self.noteStore.findNotesMetadata(self.profile.evernote_token,
         noteFilter, 0, 201, NotesMetadataResultSpec(includeCreated=True))
      dayCounter = defaultdict(int)
      for metadata in noteMetadataList.notes:
         d = date.fromtimestamp(metadata.created/1000)
         dayCounter[d.weekday()] += 1
      return dayCounter
   
  #this is SLOW - iterates through all notes
   def get_stats_for_notebook(self, notebook):
      nf = NoteFilter()
      nf.notebookGuid = notebook.guid
      return self.get_notes_statistics(nf, 0, 25)
  
  #this is SLOW - iterates through all notes
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
