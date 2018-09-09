from app import app
from config import MONGO_URI, client
from flask import session, request, jsonify
import pymongo
import requests
import json
from datetime import datetime

# 連進MongoDB
db = client['aiboxdb']

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

@app.route('/api/android/getAllLocation', methods=['GET'])
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

@app.route('/api/android/getLastLocation', methods=['GET'])
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

@app.route('/api/android/getWeather', methods=['GET'])
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

    city = request.args.get('city')
    print(city)
    has_city = False

    city_transfer = {
        '新北': '新北市',
        '新北市': '新北市',
        '台北': '臺北市',
        '台北市': '臺北市',
        '台中': '臺中市',
        '台中市': '臺中市',
        '台南': '臺南市',
        '台南市': '臺南市'
    }
    
    for key, values in  city_transfer.items():
        if city == key:
            city = values

    weather = {
        'Wx': '', # 天氣現象
        'MaxT': '', # 最高溫度
        'MinT': '', # 最低溫度
        'CI': '', # 舒適度
        'PoP': '', # 降雨機率
        'info': '' # 讓app可以換相對應的背景
    }

    # 政府開放資料, 天氣api
    resp = requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314')
    data = json.loads(resp.text)
    records = data['records']['location'] # 各地區的預報紀錄

    for record in records:
        if record['locationName'] == city:
            has_city = True
            elements = record['weatherElement']
            for element in elements:
                if element['elementName'] == 'Wx': # 天氣現象
                    weather['Wx'] = element['time'][-1]['parameter']['parameterName']
                if element['elementName'] == 'MaxT': # 最高溫度
                    weather['MaxT'] = element['time'][-1]['parameter']['parameterName']
                if element['elementName'] == 'MinT': # 最低溫度
                    weather['MinT'] = element['time'][-1]['parameter']['parameterName']
                if element['elementName'] == 'CI': # 舒適度
                    weather['CI'] = element['time'][-1]['parameter']['parameterName']
                if element['elementName'] == 'PoP': # 降雨機率
                    weather['PoP'] = element['time'][-1]['parameter']['parameterName']
            
            # app天氣背景資訊
            if '雨' in weather['Wx']:
                weather['info'] = 'rainy'
            elif '晴' in weather or '熱' in weather:
                weather['info'] = 'sunny'
            elif '雲' in weather['Wx']:
                weather['info'] = 'cloudy'
            else:
                weather['info'] = 'cloudy'
            

    if has_city is True:
        resp = {
            'status': '200',
            'result': weather,
            'msg': '取得某城市的天氣狀況成功'
        }
        return jsonify(resp)
    else:
        resp = {
            'status': '404',
            'result': '沒有此城市',
            'msg': '取得某城市的天氣狀況失敗'
        }
        return jsonify(resp)

@app.route('/api/android/getHospital', methods=['GET'])
def android_get_hospital():
    '''取得醫院的資訊
    Params:
        hospital: 醫院名稱
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 取得醫院的資訊; 錯誤訊息
            'msg': 訊息
        }
    '''

    hospital = request.args.get('hospital')

    db = client['aiboxdb']
    hospital_collect = db['hospital']
    hospital_doc = hospital_collect.find_one({'機構名稱': {'$regex': hospital}})

    if hospital_doc != None:
        hospital_doc.pop('_id')
        resp = {
            'status': '200',
            'result': hospital_doc,
            'msg': '取得醫院資訊成功'
        }
        return jsonify(resp)
    else:
        resp = {
            'status': '404',
            'result': '沒有此醫院',
            'msg': '取得醫院資訊失敗'
        }
        return jsonify(resp)

@app.route('/api/android/getECPhone', methods=['GET'])
def android_get_ec_phone():
    '''取得緊急聯絡電話
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 取得緊急聯絡電話; 錯誤訊息
            'msg': 訊息
        }
    '''

    db = client['aiboxdb']
    temp_ec_phone_collect = db['temp_ec_phone']
    temp_ec_phone_doc = temp_ec_phone_collect.find_one({'_id': 0})

    if temp_ec_phone_doc['phone'] != '':
        resp = {
            'status': '200',
            'result': {
                'phone': temp_ec_phone_doc['phone']
            },
            'msg': '取得緊急聯絡電話成功'
        }

        temp_ec_phone_doc = temp_ec_phone_collect.find_one_and_update({'_id': 0}, {'$set': {'phone': ''}}, upsert=False)

        return jsonify(resp)
    else:
        resp = {
            'status': '404',
            'result': "null",
            'msg': '取得緊急聯絡電話失敗'
        }
        return jsonify(resp)

@app.route('/api/android/getActivity', methods=['GET'])
def android_get_activity():
    '''取得活動資訊
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 取得活動資訊; 錯誤訊息
            'msg': 訊息
        }
    '''

    db = client['aiboxdb']
    open_activity_collect = db['open_activity']
    open_activity_doc = open_activity_collect.find({}, {'_id': False})

    resp = {
        'status': '200',
        'result': list(open_activity_doc),
        'msg': '取得活動資訊成功'
    }
    return jsonify(resp)