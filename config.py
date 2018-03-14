import os

LOG_DIR = os.path.join(os.getcwd(), 'app/log/')
BASE_DIR = os.path.join(os.getcwd(), 'app/modules/')

class Config(object):
    DEBUG = True
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/dumall'
    # DATABASE_URI = 'sqlite://:memory:'