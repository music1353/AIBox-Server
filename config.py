import os
import pymongo

LOG_DIR = os.path.join(os.getcwd(), 'app/logs/')
BASE_DIR = os.path.join(os.getcwd(), 'app/modules/')
MODEL_DIR = os.path.join(os.getcwd(), 'app/training_models/')
MONGO_URI = 'mongodb://aibox:12345@ds231719.mlab.com:31719/aiboxdb'
try:
    client = pymongo.MongoClient(MONGO_URI)
    print('成功連接至mongodb')
except:
    print('連接mongodb失敗')

class Config(object):
    JSON_AS_ASCII = False
    DEBUG = True
    TESTING = True