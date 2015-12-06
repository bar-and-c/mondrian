# mondrian
A simple Python app to monitor Jenkins and Gerrit status in a Mondrian-inspired GUI.

### Purpose
The purpose of this application is to provide a quick way to check the status of 
software developers' build, test and code review tools. Since the immediate need
for me was to monitor build and test status from Jenkins, and code review status 
from Gerrit, these are the only servers the application currently deals with. 

The result is presented in a GUI that is inspired by Piet Mondrian. There are no
visual indication of what the coloured boxes mean; the intention there is that 
when all is well, all fields are white, and since there are so few, you can easily
learn which field represents what. 
The plan is to run it on a Raspberry Pi, to be tacked onto a display. Like a piece
of living and informative art. 
(Unfortunately wxPython 3 turned out to be a pain to install on the Pi, so I might
change to Tkinter.)

### Usage

You must create a config file, containing e.g. the URLs to Jenkins and Gerrit, and 
also the build and test jobs to monitor. The name of the file must be mondrian.json,
and it must be located where the rest of the application is. 
The repo contains an example file, mondrian_example_config.json, with examples from 
publically available servers. 

The application is started by calling mondrian.py, with optional arguments:

* -t, as in "top window", i.e. a small window that stays on top of others.
* -f, for full screen presentation (where it also tries to keep the screen saver at bay).
* -p, for "power save", meaning that outside work hours, it does not pull any data from
servers, and (in full screen mode) does not try to keep the screen saver away.
* No arguments spawns a small normal window, like -t but not on top.

The flags '-f' and '-t' are mutually exclusive.
Escape key to exit in all cases.

### Status presentation

In its current implementation, there is a big field in the middle, which is build 
status. It sits in the middle and is big, since it is very important. 
Obviously tests are important as well, but this is *my* layout, OK? You can alter
the layout to suit your needs.
Speaking of tests, there are two fields to the right of the build field; the one on
the top represents the continuous integration test job(s), and the bottom one holds
the status for "other" tests. Again, feel free to tweak this to your needs. 
Finally, there are two small fields at the bottom of the window, below the build
field. The left contains status of "ready for review" on Gerrit, and the right holds
the status of "reviewed", i.e. ready for merge or more work. 

![mondrian.py screenshot](doc/mondrian.jpg "In this example, the build and CI test job is OK, but 'other tests' fail, and (bottom row) there are a lot of changes on Gerrit that need your attention.")


The status is reported by colouring the fields on the screen as follows: 

* white is "good", 
* blue is "almost good", 
* yellow is "almost bad", and
* red is (surprise!) "bad".

The concept of good/bad is different for the three groups. 
The Jenkins status (build and test jobs) can be:

* "bad", if there are any failed job in that group,
* "almost bad", if there are any unstable jobs on that group,
* "good", if there are any successful jobs (but no failed or unstable), or
* "almost good", if there are only aborted and/or not run jobs in that group.

The Gerrit status fields can be:

* "good" if there are no issues at all (e.g. nothing at all ready for review),
* "almost good", if the number of issues is less than a configured limit,
* "almost bad", if the number of issues is less than another configured limit,
* "bad", if the number of issues in that group is over the "almost bad" limit.

These limits are defined in mondrian.json.


### Requirements
There are a few python modules you will need to install. I may have forgotten some, but 
you will at least need:

- wxPython Phoenix (3.x)
- jenkinsapi
- PyUserInput


### Known issues
Resizing the windows doesn't work on Windows. I haven't tried to fix it, since I don't run it on Windows, and normally only in full screen anyway.

### Credits
I started this work by tweaking a Jenkins monitor using LEDs, to be run from a Raspberry Pi.
https://www.perforce.com/blog/150910/continuous-delivery-fun-jenkins-raspberry-pi
The file jenkins_status.py originates in that project. 
Thank you, Liz Lam!


Håkan Eriksson, 
November 29, 2015
