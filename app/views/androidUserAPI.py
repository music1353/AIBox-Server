from app import app
from config import MONGO_URI, client
from flask import session, request, jsonify
import pymongo
from app.modules.health_calculator import health
from datetime import datetime, timedelta

# 連進MongoDB
db = client['aiboxdb']

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
        # 記錄到session
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

    if(session.get('login') != None):
        print('androidUser logout status:', session['login'])
        print('androidUser logout user_nickname:', session['user_nickname'])

        # 刪除session
        session.pop('login', None)
        session.pop('user_nickname', None)

        resp = {
            'status': '200',
            'result': '',
            'msg': '登出成功'
        }
        return jsonify(resp)
    else:
        resp = {
            'status': '404',
            'result': '',
            'msg': '原本就沒有此登入紀錄, 登出失敗'
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
        if session.get('login') == True:
            resp = {
                'status': '200',
                'result': session['user_nickname'],
                'msg': session['user_nickname']+'登入中'
            }
            return jsonify(resp)
        else:
            resp = {
                'status': '404',
                'result': '',
                'msg': '未登入'
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
    
    if(session.get('user_nickname') is not None):
        user_nickname = session.get('user_nickname')
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    else:
        resp = {
            'status': '404',
            'result': '未登入',
            'msg': '取得用戶需要攝取的水量錯誤'
        }
        return jsonify(resp)
    
    profile = {
        'nickname': user_doc['nickname'],
        'gender': user_doc['gender'],
        'age': user_doc['age'],
        'height': user_doc['height'],
        'weight': user_doc['weight'],
        'bmi_value': user_doc['health']['bmi_value'],
        'bmi': user_doc['health']['bmi']
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

    if(session.get('user_nickname') is not None):
        user_nickname = session.get('user_nickname')
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    else:
        resp = {
            'status': '404',
            'result': '未登入',
            'msg': '取得用戶需要攝取的水量錯誤'
        }
        return jsonify(resp)

    resp = {
        'status': '200',
        'result': user_doc['health'],
        'msg': '取得用戶生活習慣成功'
    }
    return jsonify(resp)

@app.route('/api/androidUser/getNeed')
def androidUser_get_need():
    '''取得用戶需要攝取的水量(c.c.)及卡路里(大卡)
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 用戶需要攝取的水量及卡路里; 錯誤訊息
            'msg': 訊息
        }
    '''

    if(session.get('user_nickname') is not None):
        user_nickname = session.get('user_nickname')
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    else:
        resp = {
            'status': '404',
            'result': '未登入',
            'msg': '取得用戶需要攝取的水量錯誤'
        }
        return jsonify(resp)

    needwater = health.cal_water(user_doc['weight'])
    needcalorie = health.cal_BMR(user_doc['gender'], user_doc['weight'], user_doc['height'], user_doc['age'])

    resp = {
        'status': '200',
        'result': {
            'needwater': needwater,
            'needcalorie': needcalorie
        },
        'msg': '取得用戶需要攝取的熱量成功'
    }
    return jsonify(resp)


@app.route('/api/androidUser/getConversation', methods=['GET'])
def androidUser_get_conversation():
    '''取得用戶的對話紀錄, 且會過濾掉過期的提醒資料
    Returns:
        {
            'status': '200'->取得成功; '404'->取得失敗
            'result': 用戶的對話紀錄(沒資料為空list); 錯誤訊息
            'msg': 訊息
        }
    '''

    if(session.get('user_nickname') is not None):
        user_nickname = session.get('user_nickname')
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    else:
        resp = {
            'status': '404',
            'result': '未登入',
            'msg': '取得用戶需要攝取的水量錯誤'
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

    if(session.get('user_nickname') != None):
        user_nickname = session.get('user_nickname')
    else:
        resp = {
            'status': '404',
            'result': '未登入',
            'msg': '取得用戶需要攝取的水量錯誤'
        }
        return jsonify(resp)

    remind_collect = db['reminder']
    user_remind_doc = remind_collect.find({'user_nickname': user_nickname})

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
        'msg': '取得用戶提醒成功'
    }

    return jsonify(resp)

@app.route('/api/androidUser/concernLock', methods=['POST'])
def androidUser_concern_lock():
    '''讓concern模組知道現在是對誰做關心
    Params:
        user_nickname: 使用者的專屬語
    Returns:
        {
            'status': '200'->成功; '404'->失敗
            'result': ''
            'msg': 訊息
        }
    '''

    user_nickname = request.json['user_nickname']
    print('concern lock:', user_nickname)

    # 記錄到db
    concern_lock_collect = db['concern_lock']
    concern_lock_collect.update({'_id': 0}, {'$set':{'user_nickname': user_nickname, 'lock': True, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
    #
    resp = {
        'status': '200',
        'result': '',
        'msg': user_nickname + '進入關心狀態'
    }
    return jsonify(resp)

@app.route('/api/androidUser/concernRelease', methods=['POST'])
def androidUser_concern_release():
    '''讓concern模組知道現在是對誰解除關心狀態
    Params:
        user_nickname: 使用者的專屬語
    Returns:
        {
            'status': '200'->成功; '404'->失敗
            'result': ''
            'msg': 訊息
        }
    '''

    user_nickname = request.json['user_nickname']
    print('concern release:', user_nickname)

    # 刪除到db登入紀錄
    concern_lock_collect = db['concern_lock']
    concern_lock_collect.update({'_id': 0}, {'$set':{'user_nickname': '', 'lock': False, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})

    resp = {
        'status': '200',
        'result': '',
        'msg': user_nickname + '退出提醒狀態'
    }
    return jsonify(resp)

@app.route('/api/androidUser/dailyConcern', methods=['GET'])
def androidUser_get_daily_concern():
    '''取得使用者的daily concern資訊
    Returns:
        {
            'status': '200'->成功; '404'->失敗
            'result': 使用者的daily concern訊息
            'msg': 訊息
        }
    '''

    if(session.get('user_nickname') is not None):
        user_nickname = session.get('user_nickname')
        collect = db['users']
        user_doc = collect.find_one({'nickname': user_nickname})
    else:
        resp = {
            'status': '404',
            'result': '未登入',
            'msg': '取得用戶daily concern錯誤'
        }
        return jsonify(resp)

    daily_concern_data = user_doc['daily_concern']

    daily_concern_list = [] # 擺放整理後的結果
    date_list = []

    today = datetime.today()
    print('today:', today)
    todayNum = datetime.today().weekday()
    print('todayNum:', todayNum)
    date_diff = -1

    # 0 => 星期一, 1 => 星期二, 2 => 星期三, etc
    if todayNum == 0:
        date_diff = 1
    elif todayNum == 1:
        date_diff = 2
    elif todayNum == 2:
        date_diff = 3
    elif todayNum == 3:
        date_diff = 4
    elif todayNum == 4:
        date_diff = 5
    elif todayNum == 5:
        date_diff = 6
    elif todayNum == 6:
        date_diff = 0
    print('date_diff:', date_diff)

    # 過濾日期
    for data in daily_concern_data:
        date_str = data['date']
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

        if (today - date).days <= date_diff:
            date = date_str.split(' ')[0]
            print(date)
            if date not in date_list:
                date_list.append(date)

        # 算各日期平均
    for date in date_list:
        count = 0
        diastolic = 0
        systolic = 0

        for data in daily_concern_data:
            concern_date = data['date'].split(' ')[0]

            if concern_date == date and 'diastolic' in data and data['diastolic']!='':
                count = count + 1
                diastolic = diastolic + int(data['diastolic'])
                systolic = systolic + int(data['systolic'])
        
        if count != 0:
            obj = {
                'dateWeekNum': datetime.strptime(date, '%Y-%m-%d').weekday(),
                'date': date,
                'diastolic': str(diastolic/count),
                'systolic': str(systolic/count)
            }
            daily_concern_list.append(obj)

    resp = {
        'status': '200',
        'result': daily_concern_list,
        'msg': '取得daily_concern成功'
    }
    return jsonify(resp)
    