import os
directory = os.path.abspath(os.path.dirname(__file__))

#----------------------------------------
# Configure these settings to your taste:
#----------------------------------------
# The secret key is needed for Flask to 
# enable the sessions environment. It is 
# recommended that you generate a new one
# by opening a python interpreter, then:
# >>>import os
# >>>os.urandom(24)
# 'Lcc\\\xef$\xc8vG\x12\xcc\x11\xbfKE5\x03\x98\xdc\xbc\xcc.JQ'
SECRET_KEY = '\x13\xf4\x95\xb3\x86p\xbf\x1b\xb6B\xc2b\xf4\x96\xf5\xa78;\x8a+\xf2\xdat\xc2'
#----------------------------------------
# DEBUG mode will allow Werkzeug to give
# helpful debug information. It is 
# usually considered best to set this to
# False when deploying to a server.
DEBUG = True
#----------------------------------------
# Admins should be a list of usernames
# who you wish to have access to the
# admin interface to assign batches. 
# This should be a list of strings, eg:
# ['admin1', 'admin2']
ADMINS = ['mordo']
#----------------------------------------
# The preproc directory is where the app
# will look for your datasets. Be sure
# these are in the .preproc format!
# Check the README file if you aren't
# sure what this means.
PREPROC_DIR = os.path.join(directory, 'preproc')
#----------------------------------------
# These settings determine how the 
# annotations will be split up amongst
# users. ANNOTATIONS_PER_BATCH sets how
# many annotations will be included in 
# each batch that is assigned. OVERLAP
# specifies how many annotations in each
# batch will be double annotated. Be sure
# this is an even number!
ANNOTATIONS_PER_BATCH = 10
OVERLAP = 4
#----------------------------------------
# This is where the data for your app 
# will be stored. Probably best left 
# as the default.
DIRECTORY = os.path.join(directory, 'data')
#----------------------------------------
# This toggles the normalization task in
# the app.
NORMALIZATION_TASK = False
#----------------------------------------
# This is the tag that will be appended
# to the saved file of each users
# submissions.
OUTPUT = '_output.json'
