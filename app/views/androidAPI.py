from app import app
from config import MONGO_URI
from flask import session, request, jsonify
import pymongo
import requests
import json
from datetime import datetime

# 連進MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client['aiboxdb']
print('android api success connect to mongodb.')

@app.route('/api/android/getRemind', methods=['GET'])
def android_get_remind():
    '''取得沒有user_nickname(未登入)的提醒資料, 且會過濾掉過期的提醒資料
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 為登入提醒的資料(沒資料為空list); 錯誤訊息
            'msg': 訊息
        }
    '''
    
    try:
        remind_collect = db['reminder']
        user_remind_doc = remind_collect.find({'user_nickname': ''})
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得未登入提醒資料失敗'
        }
        return jsonify(resp)

    result_list = []
    for item in user_remind_doc:
        if datetime.strptime(item['remind_time'], '%Y-%m-%d %H:%M:%S') > datetime.today():
            obj = {
                'remind_time': item['remind_time'],
                'dosomething': item['dosomething']
            }
            result_list.append(obj)

    resp = {
        'status': '200',
        'result': result_list,
        'msg': '取得未登入提醒資料成功'
    }

    return jsonify(resp)

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

@app.route('/api/android/getWeather')
def android_get_weather():
    '''取得某城市的天氣狀況
    Params:
        city: 城市名
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 取得某城市的天氣狀況; 錯誤訊息
            'msg': 訊息
        }
    '''

    try:
        city = request.args.get('city')
        print('city:', city)

        # 找到city_id
        city_id = ''
        city_resp = requests.get('https://works.ioa.tw/weather/api/all.json')

        for item in json.loads(city_resp.text):
            if item['name'] == city:
                city_id = item['id']

        # 透過city_id, 查詢氣象資訊
        weather_resp = requests.get('https://works.ioa.tw/weather/api/weathers/'+city_id+'.json')
        weather_resp = json.loads(weather_resp.text)
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得某城市的天氣狀況失敗'
        }
        return jsonify(resp)

    weather = {
        'desc': weather_resp['desc'],
        'temperature': str(weather_resp['temperature']),
        'felt_air_temp': str(weather_resp['felt_air_temp']),
        'humidity': str(weather_resp['humidity']),
        'rainfall': str(weather_resp['rainfall']),
        'specials': []
    }

    # 如果有特別預報
    if weather_resp['specials'] != []:
        for item in weather_resp['specials']:
            obj = {
                'title': item['title'],
                'status': item['status'],
                'desc': item['desc'],
                'at': str(item['at'])
            }
            weather['specials'].append(obj)

    resp = {
        'status': '200',
        'result': weather,
        'msg': '取得某城市的天氣狀況成功'
    }
    return jsonify(resp)