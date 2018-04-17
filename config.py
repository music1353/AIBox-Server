import os

LOG_DIR = os.path.join(os.getcwd(), 'app/logs/')
BASE_DIR = os.path.join(os.getcwd(), 'app/modules/')
MODEL_DIR = os.path.join(os.getcwd(), 'app/training_models/')
MONGO_URI = 'mongodb://aibox:12345@ds231719.mlab.com:31719/aiboxdb'

class Config(object):
    JSON_AS_ASCII = False
    DEBUG = True
    TESTING = True