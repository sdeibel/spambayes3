# Spambayes3 - Python 3 version of only the sb_filter.py part of spambayes

This fork ports a tiny part of spambayes to Python3 and removes everything
other than what's needed for using sb_filter.py with procmail and then run
sb_mboxtrain.py on folders of user-selected spam or ham.

The project has been long-defunct and I decided to just focus on the parts
that are still useful and toss the rest, so it's at least in theory easier
to maintain the still-useful parts of this classic Tim Peters project.

This is based on mpwillison's earlier work at https://github.com/mpwillson/spambayes3 
which is/was a port of parts of spambayes version 1.1b3. I don't think I
actually added much to that work, other than pruning and adding a few very
simple-minded unit tests for sb_mboxtrain.

### Database

Only bsddb is supported for storing the spam/ham database, since that's all
I was using.  I'm running this on Rocky 9 and the system-provided db package
works:

```
sudo dnf install python3-bsddb3
```

### Unit Tests

I've removed irrelevant unit tests, added a very few mainly so I could get
code coverage statistics in tossing out unneeded files, and fixed a few
that were failing.  There are still some failures for parts I don't use:

* Some of the gzip file message tsts in test_FileCorpus.py.
* Some SBHeaderMessageTests in test_message.py fail because I didn't understand
  what this code should be doing and don't think I need this, although some
  of message.py is in use.
* Two tests in test_stats.py file; I'm hoping it doesn't matter...

I've included the Wing Pro 10 project file spambayes3.wpr.  If you use that,
you'll need to add the full path to the spambayes3 directory to the Python
Path under the Environment tab in Project Properties.  You can then run the
unit tests and if you enable Use Code Coverage in Wing Pro's Testing menu
then you can get code coverage reports in the editor or as HTML and in
other forms.

### Installing

To install this you need to copy the following directories:

* Copy the spambayes directory into the site-packages for your Python
* Place scripts/sb_* into a directory on your path, such as /usr/local/bin

Once installed, you can set up your configuration.  First configure spambayes
with the following in .spambayesrc in your home directory:

```
[Storage]
persistent_use_database=dbm
persistent_storage_file=~/.hammiedb
```

Then you can set up a .procmailrc like something like this (your paths
will vary):

:0 fw:hamlock
| /usr/bin/sb_filter.py
:0 :spambayeslock
* ^X-Spambayes-Classification: spam
/home/username/mail/spam-bayes

Then the idea is that this filters out spam into the folder spam-bayes using
the classification database .hammiedb. You build up that database over time
by placing email into a spam folder, or a ham folder if you're trying to
retrain spambayes to not identify something as spam. The a cron task runs
sb_mboxtrain.py to process those emails to train the database.

You'll need to create those two SPAM and HAM folders in your mail directory,
for example ~/mail/NEW-HAM and ~/mail/NEW-SPAM.

The you'll need a script spambayes-train to run the training process,
something like this (which is a fabricated clunky example from a larger
script that does this for multiple users):

```
#!/bin/bash
export PYTHONPATH=/path/to/spambayes3
/usr/local/bin/sb_mboxtrain.py -d /home/uname/.hammiedb -s /home/uname/mail/NEW-SPAM
/usr/local/bin/sb_mboxtrain.py -d /home/uname/.hammiedb -g /home/uname/mail/NEW-HAM
rm -f /home/uname/mail/NEW-SPAM /home/uname/mail/NEW-HAM
touch /home/uname/mail/NEW-SPAM /home/uname/mail/NEW-HAM
```

If you want to run this every 5 minutes with cron, create a crontab like this:

```
0,5,10,15,20,25,30,35,40,45,50,55 * * * * /usr/local/bin/cronic /path/to/spambayes-train
```

This uses cronic to avoid sending emails with useless status information every
five minutes.  A copy is included in this repository.

Then do 'crontab crontab' to load it and 'crontab -l' to check it.

Obviously, there are many other ways to configure this to run sb_mboxtrain.py.

### More information

See the README.txt file for the original readme and for the full un-pruned
version of spambayes that I started with: https://github.com/mpwillson/spambayes3


