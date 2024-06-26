#! /usr/bin/env python

"""FileCorpus.py - Corpus composed of file system artifacts

Classes:
    FileCorpus - an observable dictionary of FileMessages
    ExpiryFileCorpus - a FileCorpus of young files
    FileMessage - a subject of Spambayes training
    FileMessageFactory - a factory to create FileMessage objects
    GzipFileMessage - A FileMessage zipped for less storage
    GzipFileMessageFactory - factory to create GzipFileMessage objects

Abstract:
    These classes are concrete implementations of the Corpus framework.

    FileCorpus is designed to manage corpora that are directories of
    message files.

    ExpiryFileCorpus is an ExpiryCorpus of file messages.

    FileMessage manages messages that are files in the file system.

    FileMessageFactory is responsible for the creation of FileMessages,
    in response to requests to a corpus for messages.

    GzipFileMessage and GzipFileMessageFactory are used to persist messages
    as zipped files.  This can save a bit of persistent storage, though the
    ability of the compresser to do very much deflation is limited due to the
    relatively small size of the average textual message.  Still, for a large
    corpus, this could amount to a significant space savings.

    See Corpus.__doc__ for more information.

To Do:
    o Suggestions?
"""

# This module is part of the spambayes project, which is Copyright 2002-2007
# The Python Software Foundation and is covered by the Python Software
# Foundation license.



__author__ = "Tim Stone <tim@fourstonesExpressions.com>"
__credits__ = "Richie Hindle, Tim Peters, all the spambayes contributors."

import email

from spambayes import Corpus
from spambayes import message
import os, gzip, fnmatch, time, stat
from spambayes.Options import options

class FileCorpus(Corpus.Corpus):

    def __init__(self, factory, directory, filter='*', cacheSize=250):
        '''Constructor(FileMessageFactory, corpus directory name, fnmatch
filter'''

        Corpus.Corpus.__init__(self, factory, cacheSize)

        self.directory = directory
        self.filter = filter

        # This assumes that the directory exists.  A horrible death occurs
        # otherwise. We *could* simply create it, but that will likely only
        # mask errors

        # This will not pick up any changes to the corpus that are made
        # through the file system. The key list is established in __init__,
        # and if anybody stores files in the directory, even if they match
        # the filter, they won't make it into the key list.  The same
        # problem exists if anybody removes files. This *could* be a problem.
        # If so, we can maybe override the keys() method to account for this,
        # but there would be training side-effects...  The short of it is that
        # corpora that are managed by FileCorpus should *only* be managed by
        # FileCorpus (at least for now).  External changes that must be made
        # to the corpus should for the moment be handled by a complete
        # retraining.
        for filename in os.listdir(directory):
            if fnmatch.fnmatch(filename, filter):
                self.msgs[filename] = None

    def makeMessage(self, key, content=None):
        '''Ask our factory to make a Message'''
        msg = self.factory.create(key, self.directory, content)
        return msg

    def addMessage(self, message, observer_flags=0):
        '''Add a Message to this corpus'''
        if not fnmatch.fnmatch(message.key(), self.filter):
            raise ValueError

        if options["globals", "verbose"]:
            print(('adding', message.key(), 'to corpus'))

        message.directory = self.directory
        message.store()
        # superclass processing *MUST* be done
        # perform superclass processing *LAST!*
        Corpus.Corpus.addMessage(self, message, observer_flags)

    def removeMessage(self, message, observer_flags=0):
        '''Remove a Message from this corpus'''
        if options["globals", "verbose"]:
            print(('removing', message.key(), 'from corpus'))

        message.remove()

        # superclass processing *MUST* be done
        # perform superclass processing *LAST!*
        Corpus.Corpus.removeMessage(self, message, observer_flags)

    def __repr__(self):
        '''Instance as a representative string'''

        nummsgs = len(self.msgs)
        if nummsgs != 1:
            s = 's'
        else:
            s = ''

        if options["globals", "verbose"] and nummsgs > 0:
            lst = ', ' + '%s' % (list(self.keys()))
        else:
            lst = ''

        return "<%s object at %8.8x, directory: %s, %s message%s%s>" % \
            (self.__class__.__name__, \
            id(self), \
            self.directory, \
            nummsgs, s, lst)


class ExpiryFileCorpus(Corpus.ExpiryCorpus, FileCorpus):
    '''FileCorpus of "young" file system artifacts'''

    def __init__(self, expireBefore, factory, directory, filter='*', cacheSize=250):
        '''Constructor(FileMessageFactory, corpus directory name, fnmatch
filter'''

        Corpus.ExpiryCorpus.__init__(self, expireBefore)
        FileCorpus.__init__(self, factory, directory, filter, cacheSize)


class FileMessage(object):
    '''Message that persists as a file system artifact.'''

    message_class = message.SBHeaderMessage
    def __init__(self, file_name=None, directory=None):
        '''Constructor(message file name, corpus directory name)'''
        self.file_name = file_name
        self.directory = directory
        self.loaded = False
        self._msg = self.message_class()

    def __getattr__(self, att):
        """Pretend we are a subclass of message.SBHeaderMessage."""
        if hasattr(self, "_msg") and hasattr(self._msg, att):
            return getattr(self._msg, att)
        raise AttributeError()

    def __getitem__(self, k):
        """Pretend we are a subclass of message.SBHeaderMessage."""
        if hasattr(self, "_msg"):
            return self._msg[k]
        raise TypeError()

    def __setitem__(self, k, v):
        """Pretend we are a subclass of message.SBHeaderMessage."""
        if hasattr(self, "_msg"):
            self._msg[k] = v
            return
        raise TypeError()

    def as_string(self, unixfrom=False):
        self.load() # ensure that the substance is loaded
        return self._msg.as_string(unixfrom)

    def pathname(self):
        '''Derive the pathname of the message file'''
        assert self.file_name is not None, \
               "Must set filename before using FileMessage instances."
        assert self.directory is not None, \
               "Must set directory before using FileMessage instances."
        return os.path.join(self.directory, self.file_name)

    def load(self):
        '''Read the Message substance from the file'''
        # This is a tricky one!  Some people might have a combination
        # of gzip and non-gzip messages, especially when they first
        # change to or from gzip.  They should be able to see (but
        # not create) either type, so a FileMessage load needs to be
        # able to load gzip messages, even though it is a FileMessage
        # subclass (GzipFileMessage) that adds the ability to store
        # messages gzipped.  If someone can think of a classier (pun
        # intended) way of doing this, be my guest.
        if self.loaded:
            return

        assert self.file_name is not None, \
               "Must set filename before using FileMessage instances."

        if options["globals", "verbose"]:
            print(('loading', self.file_name))

        pn = self.pathname()

        fp = gzip.open(pn, 'rb')
        try:
            self._msg = email.message_from_string(\
                str(fp.read().decode('utf8')), _class = self.message_class)
        except IOError as e:
            if str(e) == 'Not a gzipped file' or \
               str(e) == 'Unknown compression method':
                # We've probably got both gzipped messages and
                # non-gzipped messages, and need to work with both.
                fp.close()
                fp = open(self.pathname(), 'rb')
                self._msg = email.message_from_string(\
                    fp.read(), _class = self.message_class)
                fp.close()
            else:
                # Don't shadow other errors.
                raise
        else:
            fp.close()
        self.loaded = True

    def store(self):
        '''Write the Message substance to the file'''

        assert self.file_name is not None, \
               "Must set filename before using FileMessage instances."

        if options["globals", "verbose"]:
            print(('storing', self.file_name))

        fp = open(self.pathname(), 'w')
        fp.write(self.as_string())
        fp.close()

    def remove(self):
        '''Message hara-kiri'''
        if options["globals", "verbose"]:
            print(('physically deleting file', self.pathname()))
        try:
            os.unlink(self.pathname())
        except OSError:
            # The file probably isn't there anymore.  Maybe a virus
            # protection program got there first?
            if options["globals", "verbose"]:
                print(('file', self.pathname(), 'can not be deleted'))

    def name(self):
        '''A unique name for the message'''
        assert self.file_name is not None, \
               "Must set filename before using FileMessage instances."
        return self.file_name

    def key(self):
        '''The key of this message in the msgs dictionary'''
        assert self.file_name is not None, \
               "Must set filename before using FileMessage instances."
        return self.file_name

    def __repr__(self):
        '''Instance as a representative string'''
        sub = self.as_string()

        if not options["globals", "verbose"]:
            if len(sub) > 20:
                if len(sub) > 40:
                    sub = sub[:20] + '...' + sub[-20:]
                else:
                    sub = sub[:20]

        return "<%s object at %8.8x, file: %s, %s>" % \
            (self.__class__.__name__, \
            id(self), self.pathname(), sub)

    def __str__(self):
        '''Instance as a printable string'''
        return self.__repr__()

    def createTimestamp(self):
        '''Return the create timestamp for the file'''

        # make sure we don't die if someone has
        #removed the file out from underneath us
        try:
            stats = os.stat(self.pathname())
        except OSError:
            ctime = time.time()
        else:
            ctime = stats[stat.ST_CTIME]

        return ctime


class MessageFactory(Corpus.MessageFactory):
    # Subclass must define a concrete message klass.
    klass = None
    def create(self, key, directory, content=None):
        '''Create a message object from a filename in a directory'''
        if content:
            msg = email.message_from_string(content,
                                            _class=self.klass)
            msg.file_name = key
            msg.directory = directory
            msg.loaded = True
            return msg
        return self.klass(key, directory)
    

class FileMessageFactory(MessageFactory):
    '''MessageFactory for FileMessage objects'''
    klass = FileMessage


class GzipFileMessage(FileMessage):
    '''Message that persists as a zipped file system artifact.'''
    def store(self):
        '''Write the Message substance to the file'''
        assert self.file_name is not None, \
               "Must set filename before using FileMessage instances."

        if options["globals", "verbose"]:
            print(('storing', self.file_name))

        pn = self.pathname()
        gz = gzip.open(pn, 'wb')
        gz.write(self.as_string().encode('utf-8'))
        gz.flush()
        gz.close()


class GzipFileMessageFactory(MessageFactory):
    '''MessageFactory for FileMessage objects'''
    klass = GzipFileMessage
