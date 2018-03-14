from app import app
from config import BASE_DIR
from flask import jsonify, request
from flask_pymongo import PyMongo
from app.modules.semantic import math2chin
from app.modules.health_calculator import bmi
from app.modules.domain_matcher.matcher import Matcher
import os

mongo = PyMongo(app)

matcher = Matcher()
matcher.load_rule_data(os.path.join(BASE_DIR, 'domain_matcher/rule'))
matcher.load_word2vec_model(os.path.join(os.getcwd(), "app/train_models/word2vec_model/20180309wiki_model.bin"))
print(matcher.rule_data)

@app.route('/')
def index():
    return 'Hello Flask'

# healthAPI
@app.route('/api/healthAPI/bmi/<gender>/<kg>/<cm>', methods=['GET'])
def get_bmi(gender, kg, cm):
    result_bmi = bmi.cal(gender, kg, cm)
    
    response = {
        'status': 200,
        'msg': '請求成功',
        'result': result_bmi
    }
    
    return jsonify(response)

@app.route('/api/healthAPI/bmi/', methods=['GET'])
def get_bmi_re():
    gender = request.args.get('gender')
    kg = request.args.get('kg')
    cm = request.args.get('cm')
    
    result_bmi = bmi.cal(gender, kg, cm)
    
    response = {
        'status': 200,
        'msg': '請求成功',
        'result': result_bmi
    }
    
    return jsonify(response)
    

@app.route('/api/semanticAPI/<int:math_id>', methods=['GET'])
def get_math2chin(math_id):
    chin_id = math2chin.math2ch(math_id)
    
    response = {
        'status': 200,
        'msg': '請求成功',
        'result': chin_id
    }
    
    return jsonify(response)

@app.route('/api/goodsAPI/', methods=['GET'])
def get_goodsList():
    goods = mongo.db.goods.find()
    
    good_list = []
    for good in goods:
        good.pop('_id')
        good_list.append(good)
        
    response = {
        'status': 200,
        'msg': '請求成功',
        'result': good_list
    }
    return jsonify(response)

@app.route('/api/domainAPI/', methods=['GET'])
def get_domain():
    sentence = request.args.get('sentence')
    
    domain_score = matcher.match_domain(sentence)
    print(domain_score)
    
    return jsonify(domain_score)
    