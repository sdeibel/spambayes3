import os
import sys
import unittest
import tempfile

import sb_test_support
sb_test_support.fix_sys_path()

import sb_mboxtrain

kTestMessage = """Return-Path: <someone@example.com>
X-Original-To: someoneelse@example.com
Delivered-To: someoneelse@example.com
To: Someone <someone@example.com>
From: Some Else <someoneelse@example.com>
Subject: Test message
Organization: Example Corp
Message-ID: <021e200b-665c-6568-259d-2287f0543ee4@example.com>
Date: Thu, 21 Mar 2024 15:20:24 -0400
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:52.0)
 Gecko/20100101 PostboxApp/7.0.60
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8; format=flowed
Content-Transfer-Encoding: 7bit
Content-Language: en-US

This is a simple test message with a bit of text in it.

"""

class TestMBoxTrain(unittest.TestCase):
    
    def test_spam(self):
        tdb = tempfile.mktemp('.db')
        mbox = tempfile.mktemp('.mbox')
        with open(mbox, 'w') as f:
            f.write(kTestMessage)
        sys.argv = [__file__, '-d', tdb, '-s', mbox]
        sb_mboxtrain.main()
        
    def test_ham(self):
        # tdb = tempfile.mktemp('.db')
        tdb = '/home/sdeibel/test.db'
        assert os.path.exists(tdb)
        mbox = tempfile.mktemp('.mbox')
        with open(mbox, 'w') as f:
            f.write(kTestMessage)
        sys.argv = [__file__, '-d', tdb, '-g', mbox]
        sb_mboxtrain.main()
        
