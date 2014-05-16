import sys
import os

dirname = os.path.dirname(__file__)
parentDir = os.path.abspath(os.path.join(dirname, os.path.pardir))
sys.path.insert(0, parentDir)
from config import *
filename = os.path.join(parentDir, 'gfl_syntax', 'scripts')

DATA_DIR = os.path.join(DIRECTORY, 'data')
USER_DIR = os.path.join(DIRECTORY, 'users')
TEMP_DIR = os.path.join(DIRECTORY, 'temp')
OUTPUT_DIR = os.path.join(DIRECTORY, 'output')

