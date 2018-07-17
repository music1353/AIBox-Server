from app import app
from config import MONGO_URI
from flask import session, request, jsonify
import pymongo

# 連進MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client['aiboxdb']
print('android api success connect to mongodb.')

@app.route('/api/android/getAllLocation')
def android_get_all_location():
    '''取得所有查詢的地點
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 所有查詢地點(沒有則為空list); 錯誤訊息
            'msg': 訊息
        }
    '''

    try:
        location_collect = db['location']
        location_doc = location_collect.find().sort("_id", 1)
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得所有查詢地點失敗'
        }
        return jsonify(resp)

    result_list = []
    for item in location_doc:
        obj = {
            'location': item['location'],
            'region': item['region'],
            'number': str(item['number']),
            'unit': item['unit'],
            'date': item['date']
        }
        result_list.append(obj)
    
    resp = {
        'status': '200',
        'result': result_list,
        'msg': '取得所有查詢地點成功'
    }
    return jsonify(resp)

@app.route('/api/android/getLastLocation')
def android_get_last_location():
    '''取得最後一個(最新)查詢的地點
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 最新的查詢地點(沒有則為空物件{}); 錯誤訊息
            'msg': 訊息
        }
    '''
    try:
        location_collect = db['location']
        location_doc = location_collect.find().sort("_id", -1).limit(1) # 找_id最大的
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得最新的查詢地點失敗'
        }
        return jsonify(resp)
    
    obj= {}
    for item in location_doc:
        obj = {
            'location': item['location'],
            'region': item['region'],
            'number': str(item['number']),
            'unit': item['unit'],
            'date': item['date']
        }
    
    resp = {
        'status': '200',
        'result': obj,
        'msg': '取得最後一個(最新)查詢地點成功'
    }
    return jsonify(resp)