tfwdepub
========

A script for downloading "The Future We Deserve" and converting it in to an
open ePub format.

Currently a bit shonky and needs testing, but if you squint a bit, it works.

:-)

Usage
+++++

Make sure you have the requirements installed like this: ``pip install -r requirements.txt``

If you've run the script before ensure there's not a ``tfwd`` directory in the
root directory of the project.

Run the script like this: ``./scrape.py``

Tail the log file (to see what it's doing) like this: ``tail -f epub.log``

The end result should be an epub file called: ``tfwd.epub``

I've tested it with the EPub reader on Firefox, but Aldiko (on Android)
doesn't appear to parse it correctly. I'll need to check what's going on
before claiming the script is finished.

As always, comments, suggestions, bugs and patches most welcome via the
machinations of GitHub.

N.
