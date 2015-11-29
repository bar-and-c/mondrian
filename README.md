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
of living art. 

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

The status is reported as follows: white is "good", blue is "almost good", yellow is 
"almost bad" and red is (surprise!) "bad".
The concept of good/bad is different for the three groups. The build is either good
or bad. One could imagine warnings producing an "almost good/bad" status, but we have
warnings treated as errors. 
The tests are currently only good/bad as well, i.e. if only one of the test jobs in 
a field is not a success, the entire field is red. 
The Gerrit fields are good if there are no issues at all, e.g. nothing at all ready 
for review. Then there are limits, defined in the config file, which defines how many
changes in each category means "almost good", et cetera. 

The config file, mondrian.json, also contains the URLs to Jenkins and Gerrit, and also
the build and test jobs to monitor. 


### Requirements
There are a few python modules you will need to install. I may have forgotten some, but 
you will at least need:

- wxPython
- jenkinsapi

I will update this list when I know for sure.

### Credits
I started this work by tweaking a Jenkins monitor using LEDs, to be run from a Raspberry Pi.
https://www.perforce.com/blog/150910/continuous-delivery-fun-jenkins-raspberry-pi
The file jenkins_status.py originates in that project. 
Thank you, Liz Lam!


Håkan Eriksson, 
November 29, 2015
