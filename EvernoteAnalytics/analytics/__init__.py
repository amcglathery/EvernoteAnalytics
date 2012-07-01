""" Class is used to retreive statistics based on a user profile """
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
from evernote.edam.notestore.ttypes import *
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
from collections import defaultdict, Counter
from datetime import date, timedelta, datetime
from monthdelta import MonthDelta as monthdelta
import re, nltk

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

   def get_first_note_timestamp(self):
      nf = NoteFilter()
      nf.order = 1
      nf.ascending = True
      firstNote = self.noteStore.findNotes(self.profile.evernote_token,
         nf,0,1).notes[0]
      return firstNote.created
         

   #I thought about making this a map to the objects themselves but I
   #was worried about performance and was planning on putting this into
   #JSON right away 
   def get_guid_map(self, notebookNames=True, tagNames=False):
      """ returns a map from guid to a given object, pass with parameters for
          different data to be included. Default is only notebooks
      """
      guidMap = {}
      if notebookNames:
         notebooks = self.noteStore.listNotebooks(self.profile.evernote_token)
         for notebook in notebooks:
            guidMap[notebook.guid] = notebook.name
      if tagNames:
         tags = self.noteStore.listTags(self.profile.evernote_token)
         for tag in tags:
            guidMap[tag.guid] = tag.name
      return guidMap

   def get_notes_in_tags(self):
      return self.noteStore.findNoteCounts(self.profile.evernote_token,
         NoteFilter(), False).tagCounts.items()

   def get_tag_name(self, tagGuid):
      return self.noteStore.getTag(self.profile.evernote_token, 
         tagGuid).name

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

   def get_note_metadata(self, noteFilter=NoteFilter()):
      """ Returns a count of number of posts per weekday as well as 
          a list of the geolocations (if available). In the form
          [notetitile, latitude, longitude] """
      noteMetadataList = self.noteStore.findNotesMetadata(self.profile.evernote_token,
      noteFilter, 0, 200,
      NotesMetadataResultSpec(includeCreated=True,includeAttributes=True,
                                 includeTitle=True))
      dayCounter = defaultdict(int)
      monthCounter = defaultdict(int)
      hourCounter = defaultdict(int)
      geoLocations = []

      for metadata in noteMetadataList.notes:
         d = datetime.fromtimestamp(metadata.created/1000)
         dayCounter[d.weekday()] += 1
         monthCounter[d.month] += 1
         hourCounter[d.hour] += 1
         a = metadata.attributes
         if a.latitude is not None:
            geoLocations.append([metadata.title,a.latitude,a.longitude])
         
      return { 'monthCounter': monthCounter, 'hourCounter': hourCounter,
               'dayCounter' : dayCounter, 'geoLocations' : geoLocations }
  
   def get_word_count(self, nf=NoteFilter(), numWords=None):
      #currently never repopulates unless user store is empty
      if self.profile.notes_word_count is None:
         guidToWordCount = self.update_word_count()
      else:
         guidToWordCount = self.profile.notes_word_count
      c = Counter()
      for d in guidToWordCount.values():
         c.update(d)
      if numWords is None:
         return c.most_common()
      else:
         return c.most_common(numWords)
      
   def update_word_count(self, nf=NoteFilter()):
      noteList = self.noteStore.findNotes(self.profile.evernote_token,
                                          nf, 0, 200).notes
      d = dict()
      stopwords = nltk.corpus.stopwords.words('english')
      ever_stop = ['_en_todo_false', '_en_todo_true'] 
      for note in noteList: 
         words = self.noteStore.getNoteSearchText(self.profile.evernote_token,
         note.guid, False, True)
         c = Counter(w.lower() for w in re.findall(r"\w+", words) if not w in stopwords and w not in ever_stop)
         d[note.guid] = c
      self.profile.notes_word_count = d
      self.profile.save()
      return d

   #Both of these helper functions are very broken
   def get_all_notes(self, notefilter):
       """ This is a helper method that will handle paginations in the data """
       noteList = self.noteStore.findNotes(self.profile.evernote_token,
                                          notefilter, 0, 50)
       notes = noteList.notes
#       raise Exception(str(noteList.startIndex) + " " + str(len(notes)) + 
#                        " " + str(noteList.totalNotes))
       while noteList.totalNotes != len(notes):
          noteList = self.noteStore.findNotes(self.profile.evernote_token,
                  notefilter, noteList.startIndex + len(notes), 50)
          notes.extend(noteList.notes)
       return notes

   #BROKEN
   def get_all_metadata(self, notefilter, resultSpec):
       """ helper method to handle paginations """
       noteList = self.noteStore.findNotesMetadata(self.profile.evernote_token,
                                          notefilter, 0, 50, resultSpec)
       notes = noteList.notes
       while noteList.totalNotes != len(notes) - 1:
          raise Exception(str(noteList.startIndex) + " " + str(len(notes)) + 
                        " " + str(noteList.totalNotes))
          noteList = self.noteStore.findNotesMetadata(self.profile.evernote_token,
                  notefilter, noteList.startIndex + len(notes), 50, resultSpec)
          notes.extend(noteList.notes)
       return notes

   def create_date_filter(self, range1, range2=None, created=True):
       """Adds a date filter into a given note filter (or creates one)
          if only 1 range is specified then it is a since filter
          if created is true then return a created filter, 
          if false, then an updated one """
       nf = NoteFilter()
       filtertype = ""
       if created:
         filtertype = "created:"
       else: 
         filtertype = "updated:"
       filt = filtertype + range1.strftime("%Y%m%d")
       if range2 is not None:
         filt += " -" + filtertype + range2.strftime("%Y%m%d")
       nf.words = filt
       return nf
       
   def date_from_today(self, day=0, week=0, month=0, year=0):
      d = (date.today() - timedelta(days=day,weeks=week)) - monthdelta(months=month + year * 12)
      return d

