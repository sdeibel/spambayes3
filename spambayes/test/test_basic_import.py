import unittest

class TestImports(unittest.TestCase):

    def test_basic_import(self):
        raise unittest.SkipTest('still imports things that have been removed')
        from spambayes import CorePlugin
        from spambayes import CoreUI
        from spambayes import Corpus
        from spambayes import CostCounter
        from spambayes import Dibbler
        from spambayes import FileCorpus
        from spambayes import Histogram
        from spambayes import ImageStripper
        from spambayes import ImapUI
        from spambayes import Options
        from spambayes import OptionsClass
        from spambayes import ProxyUI
        from spambayes import PyMeldLite
        from spambayes import ServerUI
        from spambayes import Stats
        from spambayes import TestDriver
        from spambayes import TestToolsUI
        from spambayes import Tester
        from spambayes import UserInterface
        from spambayes import Version
        from spambayes import XMLRPCPlugin
        from spambayes import cdb
        from spambayes import cdb_classifier
        from spambayes import chi2
        from spambayes import classifier
        from spambayes import dbmstorage
        from spambayes import dnscache
        from spambayes import hammie
        from spambayes import hammiebulk
        from spambayes import i18n
        from spambayes import mboxutils
        from spambayes import message
        from spambayes import msgs
        from spambayes import oe_mailbox
        from spambayes import optimize
        from spambayes import port
        from spambayes import postfixproxy
        from spambayes import safepickle
        from spambayes import smtpproxy
        from spambayes import storage
        from spambayes import tokenizer
