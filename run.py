#!/usr/bin/python

import sys, os, glob
from config import *
path = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, path)
from application import app, DATA_DIR, OUTPUT_DIR, USER_DIR, TEMP_DIR, training, newUser


if __name__ == '__main__':
    directories = [DIRECTORY, DATA_DIR, OUTPUT_DIR, USER_DIR, PREPROC_DIR, TEMP_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.mkdir(directory)
    if not os.path.isfile(os.path.join(DIRECTORY, 'training.json')):
        training()
    if glob.glob(os.path.join(DIRECTORY, 'users', '*.json')) == []:
        newUser(username='default')
    app.run(debug=DEBUG)
