gfl_web
=======

Uses Python's Flask module to create a web-based interface for GFL-FUDG annotation. 

By Michael Mordowanec, Nathan Schneider

GitHub: http://github.com/Mordeaux/gfl_web

Setup
=====
I used Linux (Ubuntu and Amazon AMI) developing this so these instructions are more Linux-geared. Windows users would probably do something similar. 

The 'best-practices' types in web development recommend the use of a Python Virtual Environment when deploying to a server, which will minimize the chance that installed modules needed for this code will conflict with those installed in /usr/bin/python. I also recommend that you use a virtual environment. Installation of the virtualenv tool is not explained here.

The information below should be all you need to get set up. This project uses Python 2.7. I have deployed it on several versions of Python 2.7. It will fail if you are using Python 2.6. 

Step by Step, Day by Day
------------------------
### Clone this repo and its submodules, gfl_syntax and ace-builds web editor.
```
$ git clone --recursive https://github.com/Mordeaux/gfl_web.git
```
### Virtual Environment
If you don't have virtualenv installed or don't wish to use one skip to Get modules.
```
$ virtualenv env #or other location
```
Change the shebang in the first line of run.py to read:
```
#!/full/path/to/env/bin/python
```
Then:
```
$ source path/to/env/bin/activate
```
You should see the name of your virtual environment in the prompt:
```
(env)$
```
### Get modules
To download all the Python modules needed for this project, simply:
```
$ pip install -r requirements.txt
```
You also need Graphviz, which for Ubuntu can be installed like so:
```
$ sudo apt-get install graphviz
```
### Configure
Now open up config.py and change any settings you need to change. I highly recommend following the instructions in there to create a new SECRET_KEY.

### Fire it up, Fire it up
Enter this:
```
$ ./run.py
```
The app should begin running locally, and tell you which port it is on (typically http//127.0.0.1:5000). When deploying to a server, I have had luck using mod_wsgi, but the details for how to configure that are beyond the scope of this README. They are easily googleable.


Input Files
===========

After running the utility, .preproc files can be added to the preproc directory in the gfl_web directory (or the place specified in config.py). .preproc is the format used by the gfl_syntax tools whose repository (included as a submodule) has scripts to help create it. Files added here will automatically be converted to JSON and appear as a list of batches on the admin screen.

The .preproc format should look something like this for the sentence 'Mike said, "Ideally, I would have liked to use a much, much better example sentence."':

    ---
    % ID uniqueID
    % RAW TEXT
    Mike said, "Ideally, I would have liked to use a much, much better example sentence."

    % TEXT
    Mike said , " Ideally , I would have liked to use a much~1 , much~2 better example sentence . "

    % ANNO
    Mike said Ideally I would have liked to use a much~1 much~2 better example sentence

.preproc files can contain many such sentences, and if placed into the preproc directory they will be sectioned off into batches which can be assigned to annotators in the admin interface. The number of annotations per batch as well as the amount of overlap (for measuring inter-annotator agreement) can be set in config.py.

Usage
=====
The annotation interface is designed to be as self-explanatory as possible. Logging in and out is left to be set up according to the needs of the user. Currently all that one need do is go to 'http://<domain or IP>/login?user=' followed by their username and the program will log them in. 

The admin interface is restricted to only those usernames listed in config.py. If you are not planning to use a safer login method, it is recommended that these names be kept secret and hard to guess.

The annotation interface uses the Ace texteditor, so special thanks to them (http://ace.c9.io/). 


Other
=====
Feel free to fork this project and help develop it.

GFL-FUDG guidelines:
https://github.com/brendano/gfl_syntax/blob/master/guidelines/guidelines.md

Direct any questions about the web interface to Michael Mordowanec:
https://github.com/Mordeaux

Noah's ARK at the Language Technologies Institute at Carnegie Mellon University:
http://www.ark.cs.cmu.edu/
