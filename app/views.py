from app import app
from config import BASE_DIR, MODEL_DIR, MONGO_URI
from flask import jsonify, request
from app.modules.domain_matcher.matcher import Matcher
from app.modules.domain_chatbot.chatbot import Chatbot
import os
import pymongo

matcher = Matcher()
matcher.load_rule_data(os.path.join(BASE_DIR, 'domain_matcher/rule'))
matcher.load_word2vec_model(os.path.join(MODEL_DIR, "20180320all_model.bin"))
print(matcher.rule_data)

# 連進MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client['aiboxdb']
print('success connect to mongodb.')

@app.route('/api/login/', methods=['POST'])
def login():
    # 收到的專屬語
    user_nickname = request.form['user_nickname']
    
    # 查看資料庫是否有此專屬語
    collect = db['users']
    has_nick_name = collect.find_one({'nickname': user_nickname})
    
    if has_nick_name is None:
        resp = {
            'status': 404,
            'result': '',
            'msg': '沒有此專屬語'
        }
        
        return jsonify(resp)
    else:
        resp = {
            'status': 200,
            'result': has_nick_name,
            'msg': '登入成功'
        }
        
        # 紀錄登入狀況
        login_collect = db['login']
        login_collect.update({'_id': 0},{'$set':{'is_login': True, "user_nickname": user_nickname}})
        
        return jsonify(resp)

    
@app.route('/api/logout/', methods=['POST'])
def logout():
    login_collect = db['login']
    login_collect.update({'_id': 0},{'$set':{'is_login': False, "user_nickname": ''}})
    
    resp = {
        'status': 200,
        'result': '',
        'msg': '登出成功'
    }
    
    return jsonify(resp)


@app.route('/api/checkLogin/', methods=['POST'])
def checkLogin():
    login_collect = db['login']
    login_doc = login_collect.find_one({'_id': 0})
    print(login_doc['is_login'])
    
    if login_doc['is_login'] is True:
        return login_doc['user_nickname']
    else:
        return 'not login'

    
@app.route('/api/chatbot/', methods=['POST'])
def chatbot_resp():
    # check login
    login_collect = db['login']
    login_doc = login_collect.find_one({'_id': 0})
    if login_doc['is_login'] is True:
        user_nickname = login_doc['user_nickname']
    else:
        user_nickname = ''

    flag = request.form['flag']
    if flag == '':
        flag = None

    sentence = request.form['response']
    print(flag)

    domain_score = matcher.match_domain(sentence, user_nickname=user_nickname, flag=flag)
    print(domain_score)
    chat = Chatbot(domain_score, flag=flag)
    message = chat.response_word()

    return message
    