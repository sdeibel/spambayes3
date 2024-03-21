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

To be written soon...

### More information

See the README.txt file for the original readme and for the full un-pruned
version of spambayes that I started with: https://github.com/mpwillson/spambayes3


