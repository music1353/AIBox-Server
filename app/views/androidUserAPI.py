from app import app
from config import MONGO_URI
from flask import session, request, jsonify
import pymongo
from app.modules.health_calculator import health

# 連進MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client['aiboxdb']
print('androidUser api success connect to mongodb.')

# 設置密鑰
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/api/androidUser/login', methods=['POST'])
def androidUser_login():
    '''APP端登入, 使用SESSION記錄登入
    Params:
        user_nickname: 登入帳號為使用者的專屬語
    Returns:
        {
            'status': '200'->登入成功; '404'->登入失敗
            'result': ''
            'msg': ''
        }
    '''

    # user_nickname = request.args.get('user_nickname')
    user_nickname = request.json['user_nickname']
    print('login get user_nickname:', user_nickname)

    # 查看資料庫是否有此專屬語
    collect = db['users']
    has_nick_name = collect.find_one({'nickname': user_nickname})

    if has_nick_name is None:
        resp = {
            'status': '404',
            'result': '',
            'msg': '沒有此專屬語'
        }
        return jsonify(resp)
    else:
        session['login'] = True
        session['user_nickname'] = user_nickname

        resp = {
            'status': '200',
            'result': '',
            'msg': '登入成功'
        }
        return jsonify(resp)

@app.route('/api/androidUser/logout', methods=['POST'])
def androidUser_logout():
    '''APP端登出, 刪除SESSION內的紀錄
    Returns:
        {
            'status': '200'->登出成功
            'result': ''
            'msg': 訊息
        }
    '''

    print('androidUser logout status:', session['login'])
    print('androidUser logout user_nickname:', session['user_nickname'])

    session.pop('login', None)
    session.pop('user_nickname', None)

    resp = {
        'status': '200',
        'result': '',
        'msg': '登出成功'
    }
    return jsonify(resp)

@app.route('/api/androidUser/checkLogin', methods=['POST'])
def androidUser_check_login():
    '''APP端檢查是否登入
    Returns:
        {
            'status': '200'->登入中; '404'->未登入
            'result': 正在登入的user_nickname; 錯誤訊息
            'msg': user_nickname登入中
        }
    '''
    
    try:
        if session['login'] == True:
            resp = {
                'status': '200',
                'result': session['user_nickname'],
                'msg': session['user_nickname']+'登入中'
            }
            return jsonify(resp)
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '未登入'
        }
        return jsonify(resp)

@app.route('/api/androidUser/getProfile', methods=['GET'])
def androidUser_get_profile():
    '''取得用戶的個人資訊
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 個人資訊資料; 錯誤訊息
            'msg': 訊息
        }
    '''
    try:
        user_nickname = session['user_nickname']
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得用戶個人資訊錯誤'
        }
        return jsonify(resp)
    
    profile = {
        'nickname': user_doc['nickname'],
        'gendenr': user_doc['gender'],
        'age': user_doc['age'],
        'height': user_doc['height'],
        'weight': user_doc['weight'],
        'bmi_value': user_doc['health']['bmi_value']
    }

    resp = {
        'status': '200',
        'result': profile,
        'msg': '取得個人資訊成功'
    }
    return jsonify(resp)

@app.route('/api/androidUser/getHealth', methods=['GET'])
def androidUser_get_health():
    '''取得用戶的生活習慣(健康狀況)
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 用戶生活習慣資料; 錯誤訊息
            'msg': 訊息
        }
    '''

    try:
        user_nickname = session['user_nickname']
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得用戶生活習慣錯誤'
        }
        return jsonify(resp)

    resp = {
        'status': '200',
        'result': user_doc['health'],
        'msg': '取得用戶生活習慣成功'
    }
    return jsonify(resp)

@app.route('/api/androidUser/getNeedWater')
def androidUser_get_needwater():
    '''取的用戶需要攝取的水量(c.c.)
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 用戶需要攝取的水量; 錯誤訊息
            'msg': 訊息
        }
    '''

    try:
        user_nickname = session['user_nickname']
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得用戶需要攝取的水量錯誤'
        }
        return jsonify(resp)

    needwater = health.cal_water(user_doc['weight'])
    
    resp = {
        'status': '200',
        'result': needwater,
        'msg': '取得用戶需要攝取的水量成功'
    }
    return jsonify(resp)

@app.route('/api/androidUser/getNeedCalorie')
def androidUser_get_needcalorie():
    '''取的用戶需要攝取的熱量(c.c.)
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 用戶需要攝取的熱量; 錯誤訊息
            'msg': 訊息
        }
    '''

    try:
        user_nickname = session['user_nickname']
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得用戶需要攝取的熱量錯誤'
        }
        return jsonify(resp)

    needcalorie = health.cal_BMR(user_doc['gender'], user_doc['weight'], user_doc['height'], user_doc['age'])
    
    resp = {
        'status': '200',
        'result': needcalorie,
        'msg': '取得用戶需要攝取的熱量成功'
    }
    return jsonify(resp)


@app.route('/api/androidUser/getConversation', methods=['GET'])
def androidUser_get_conversation():
    '''取得用戶的對話紀錄
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 用戶的對話紀錄(沒資料為空list); 錯誤訊息
            'msg': 訊息
        }
    '''

    try:
        user_nickname = session['user_nickname']
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得用戶對話紀錄錯誤'
        }
        return jsonify(resp)

    resp = {
        'status': '200',
        'result': user_doc['conversation'],
        'msg': '取得用戶對話記錄成功'
    }
    return jsonify(resp)

@app.route('/api/androidUser/getRemind', methods=['GET'])
def androidUser_get_remind():
    '''取得用戶的提醒
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 用戶提醒的資料(沒資料為空list); 錯誤訊息
            'msg': 訊息
        }
    '''

    try:
        user_nickname = session['user_nickname']
    except Exception as err:
        resp = {
            'status': '404',
            'result': err,
            'msg': '取得用戶提醒錯誤'
        }
        return jsonify(resp)

    remind_collect = db['reminder']
    user_remind_doc = remind_collect.find({'user_nickname': user_nickname})

    result_list = []
    for item in user_remind_doc:
        obj = {
            'remind_time': item['remind_time'],
            'dosomething': item['dosomething']
        }
        result_list.append(obj)

    resp = {
        'status': '200',
        'result': result_list,
        'msg': '取得用戶提醒成功'
    }

    return jsonify(resp)

    
    