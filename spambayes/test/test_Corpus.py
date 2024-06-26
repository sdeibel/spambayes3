# Test the Corpus module.

import sys
import time
import unittest

import sb_test_support
sb_test_support.fix_sys_path()

from spambayes.Corpus import Corpus, ExpiryCorpus, MessageFactory

# We borrow the test messages that test_sb_server uses.
from test_sb_server import good1, spam1, malformed1

class simple_msg(object):
    def __init__(self, key):
        self._key = key
        self.creation_time = time.time()
        self.loaded = False
    def createTimestamp(self):
        return self.creation_time
    def key(self):
        return self._key
    def load(self):
        self.loaded = True

class simple_observer(object):
    # Just want to tell that they have been called, so raise particular
    # errors.
    def onAddMessage(self, msg, flags):
        raise ValueError()
    def onRemoveMessage(self, msg, flags):
        raise TypeError()

class CorpusTest(unittest.TestCase):
    def setUp(self):
        self.factory = MessageFactory()
        self.cacheSize = 100
        self.corpus = Corpus(self.factory, self.cacheSize)

    def test___init__(self):
        self.assertEqual(self.corpus.cacheSize, self.cacheSize)
        self.assertEqual(self.corpus.msgs, {})
        self.assertEqual(self.corpus.keysInMemory, [])
        self.assertEqual(self.corpus.observers, [])
        self.assertEqual(self.corpus.factory, self.factory)

    def test_addObserver(self):
        self.corpus.addObserver(simple_observer())
        self.assertRaises(ValueError, self.corpus.addMessage,
                          simple_msg(0))
        self.assertRaises(TypeError, self.corpus.removeMessage,
                          simple_msg(1))

    def test_addMessage(self):
        msg = simple_msg(0)
        self.assertEqual(self.corpus.get(0), None)
        self.corpus.addMessage(msg)
        self.assertEqual(self.corpus[0], msg)

    def test_removeMessage(self):
        msg = simple_msg(0)
        self.assertEqual(self.corpus.get(0), None)
        self.corpus.addMessage(msg)
        self.assertEqual(self.corpus[0], msg)
        self.corpus.removeMessage(msg)
        self.assertEqual(self.corpus.get(0), None)

    def test_cacheMessage(self):
        msg = simple_msg(0)
        self.corpus.cacheMessage(msg)
        self.assertEqual(self.corpus.msgs[0], msg)
        self.assertTrue(0 in self.corpus.keysInMemory)

    def test_flush_cache(self):
        self.corpus.cacheSize = 1
        msg = simple_msg(0)
        self.corpus.cacheMessage(msg)
        self.assertEqual(self.corpus.msgs[0], msg)
        self.assertTrue(0 in self.corpus.keysInMemory)
        msg = simple_msg(1)
        self.corpus.cacheMessage(msg)
        self.assertEqual(self.corpus.msgs[1], msg)
        self.assertTrue(1 in self.corpus.keysInMemory)
        self.assertTrue(0 not in self.corpus.keysInMemory)

    def test_unCacheMessage(self):
        msg = simple_msg(0)
        self.corpus.cacheMessage(msg)
        self.assertEqual(self.corpus.msgs[0], msg)
        self.assertTrue(0 in self.corpus.keysInMemory)
        self.corpus.unCacheMessage(msg)
        self.assertTrue(0 in self.corpus.keysInMemory)

    def test_takeMessage(self):
        other_corpus = Corpus(self.factory, self.cacheSize)
        msg = simple_msg(0)
        other_corpus.addMessage(msg)
        self.assertEqual(self.corpus.get(0), None)
        self.corpus.takeMessage(0, other_corpus)
        self.assertEqual(msg.loaded, True)
        self.assertEqual(other_corpus.get(0), None)
        self.assertEqual(self.corpus.get(0), msg)

    def test_get(self):
        ids = [0, 1, 2]
        for id in ids:
            self.corpus.addMessage(simple_msg(id))
        self.assertEqual(self.corpus.get(0).key(), 0)

    def test_get_fail(self):
        ids = [0, 1, 2]
        for id in ids:
            self.corpus.addMessage(simple_msg(id))
        self.assertEqual(self.corpus.get(4), None)

    def test_get_default(self):
        ids = [0, 1, 2]
        for id in ids:
            self.corpus.addMessage(simple_msg(id))
        self.assertEqual(self.corpus.get(4, "test"), "test")

    def test___getitem__(self):
        ids = [0, 1, 2]
        for id in ids:
            self.corpus.addMessage(simple_msg(id))
        self.assertEqual(self.corpus[0].key(), 0)

    def test___getitem___fail(self):
        ids = [0, 1, 2]
        for id in ids:
            self.corpus.addMessage(simple_msg(id))
        self.assertRaises(KeyError, self.corpus.__getitem__, 4)

    def test_keys(self):
        self.assertEqual(list(self.corpus.keys()), [])
        ids = [0, 1, 2]
        for id in ids:
            self.corpus.addMessage(simple_msg(id))
        self.assertEqual(list(self.corpus.keys()), ids)

    def test___iter__(self):
        self.assertEqual(tuple(self.corpus), ())
        msgs = (simple_msg(0), simple_msg(1), simple_msg(2))
        for msg in msgs:
            self.corpus.addMessage(msg)
        self.assertEqual(tuple(self.corpus), msgs)

    def test_makeMessage_no_content(self):
        key = "testmessage"
        self.assertRaises(NotImplementedError, self.corpus.makeMessage, key)

    def test_makeMessage_with_content(self):
        key = "testmessage"
        content = good1
        self.assertRaises(NotImplementedError, self.corpus.makeMessage,
                          key, content)


class ExpiryCorpusTest(unittest.TestCase):
    def setUp(self):
        class Mixed(Corpus, ExpiryCorpus):
            def __init__(self, expireBefore, factory, cacheSize):
                Corpus.__init__(self, factory, cacheSize)
                ExpiryCorpus.__init__(self, expireBefore)
        self.factory = MessageFactory()
        self.cacheSize = 100
        self.expireBefore = 10.0
        self.corpus = Mixed(self.expireBefore, self.factory,
                            self.cacheSize)

    def test___init___expiry(self):
        self.assertEqual(self.corpus.expireBefore, self.expireBefore)

    def test_removeExpiredMessages(self):
        # Put messages in to expire.
        expire = [simple_msg(1), simple_msg(2)]
        for msg in expire:
            self.corpus.addMessage(msg)

        # Ensure that we don't expire the wrong ones.
        self.corpus.expireBefore = 0.25
        time.sleep(0.5)

        # Put messages in to not expire.
        not_expire = [simple_msg(3), simple_msg(4)]
        for msg in not_expire:
            self.corpus.addMessage(msg)

        # Run expiry.
        self.corpus.removeExpiredMessages()

        # Check that expired messages are gone.
        for msg in expire:
            self.assertEqual(msg in self.corpus, False)

        # Check that not expired messages are still there.
        for msg in not_expire:
            self.assertEqual(msg in self.corpus, True)
        

def suite():
    suite = unittest.TestSuite()
    clses = (CorpusTest,
             ExpiryCorpusTest,
             )
    for cls in clses:
        suite.addTest(unittest.makeSuite(cls))
    return suite


if __name__=='__main__':
    sb_test_support.unittest_main(argv=sys.argv + ['suite'])
