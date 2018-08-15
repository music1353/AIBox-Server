import os
import json
import pymongo
import datetime
import app.modules.logger.logging as log
from app.modules.health_calculator import bmi, stroke_score
from config import BASE_DIR, LOG_DIR, MONGO_URI, client

class User:
    # 讀取user.json的模板並收集word
    def __init__(self, word_domain=None, flag=None):
        self.flag = flag
        self.word_domain = word_domain

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/user.json'), 'r', encoding='UTF-8') as input:
            self.template = json.load(input)

        self.collect_data()

    # 當處於回覆流程中，將word填入user.json模板中
    def collect_data(self):
        if self.word_domain is not None and self.flag is not None:
            if self.flag == 'user_nickname':
                for data in self.word_domain:
                    self.template['專屬語'] = data['word']
            elif self.flag == 'user_gender':
                for data in self.word_domain:
                    if data['domain'] == '性別':
                        if data['word'] == '男' or data['word'] == '男生':
                            self.template['性別'] = 'man'
                        else:
                            self.template['性別'] = 'woman'
            elif self.flag == 'user_tall':
                for data in self.word_domain:
                    if data['domain'] == '數字':
                        self.template['身高'] = data['word']
            elif self.flag == 'user_kg':
                for data in self.word_domain:
                    if data['domain'] == '數字':
                        self.template['體重'] = data['word']
            elif self.flag == 'user_age':
                for data in self.word_domain:
                    if data['domain'] == '數字':
                        self.template['年紀'] = data['word']
            elif self.flag == 'user_smoke':
                for data in self.word_domain:
                    if data['domain'] == '是':
                        self.template['吸菸'] = 'True'
                        break
                    if data['domain'] == '非':
                        self.template['吸菸'] = 'False'
                        break
            elif self.flag == 'user_workout':
                for data in self.word_domain:
                    if data['domain'] == '數字':
                        self.template['運動'] = data['word']
                    elif data['domain'] == '時刻':
                        self.template['運動'] = str(data['word']).rstrip('分')

            elif self.flag == 'user_heart':
                for data in self.word_domain:
                    if data['word'] == '有' or data['word'] == '會' or data['word'] == '沒錯':
                        self.template['心律不整'] = 'True'
                    else:
                        self.template['心律不整'] = 'False'
            elif self.flag == 'user_stroke':
                for data in self.word_domain:
                    if data['word'] == '有' or data['word'] == '會' or data['word'] == '沒錯':
                        self.template['中風'] = 'True'
                    else:
                        self.template['中風'] = 'False'
            elif self.flag == 'user_hypertension':
                for data in self.word_domain:
                    if data['word'] == '有' or data['word'] == '會' or data['word'] == '沒錯':
                        self.template['高血壓'] = 'True'
                    else:
                        self.template['高血壓'] = 'False'
            elif self.flag == 'user_cholesterol':
                for data in self.word_domain:
                    if data['word'] == '有' or data['word'] == '會' or data['word'] == '沒錯':
                        self.template['高膽固醇'] = 'True'
                    else:
                        self.template['高膽固醇'] = 'False'
                for data in self.word_domain:
                    if data['word'] == '有' or data['word'] == '會' or data['word'] == '沒錯':
                        self.template['糖尿病'] = 'True'
                    else:
                        self.template['糖尿病'] = 'False'

            with open(os.path.join(BASE_DIR, 'domain_chatbot/template/user.json'), 'w',encoding='UTF-8') as output:
                json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):
        content = {}

        if self.template['專屬語'] == '':
            content['flag'] = 'user_nickname'
            content['response'] = self.template['專屬語回覆']
        elif self.template['性別'] == '':
            content['flag'] = 'user_gender'
            content['response'] = self.template['性別回覆']
        elif self.template['身高'] == '':
            content['flag'] = 'user_tall'
            content['response'] = self.template['身高回覆']
        elif self.template['體重'] == '':
            content['flag'] = 'user_kg'
            content['response'] = self.template['體重回覆']
        elif self.template['年紀'] == '':
            content['flag'] = 'user_age'
            content['response'] = self.template['年紀回覆']
        elif self.template['吸菸'] == '':
            content['flag'] = 'user_smoke'
            content['response'] = self.template['吸菸回覆']
        elif self.template['運動'] == '':
            content['flag'] = 'user_workout'
            content['response'] = self.template['運動回覆']
        elif self.template['心律不整'] == '':
            content['flag'] = 'user_heart'
            content['response'] = self.template['心律不整回覆']
        elif self.template['中風'] == '':
            content['flag'] = 'user_stroke'
            content['response'] = self.template['中風回覆']
        elif self.template['高血壓'] == '':
            content['flag'] = 'user_hypertension'
            content['response'] = self.template['高血壓回覆']
        elif self.template['高膽固醇'] == '':
            content['flag'] = 'user_cholesterol'
            content['response'] = self.template['高膽固醇回覆']
        elif self.template['糖尿病'] == '':
            content['flag'] = 'user_diabetes'
            content['response'] = self.template['糖尿病回覆']
        else:
            content['flag'] = 'user_done'
            content['response'] = self.template['完成回覆']
            self.store_user_setting()
            self.clean_template()

        return json.dumps(content, ensure_ascii=False)

    # 個人化資料上傳至資料庫
    def store_user_setting(self):
        logger = log.Logging('user:store_database')
        logger.run(LOG_DIR)
        try:
            # client = pymongo.MongoClient(MONGO_URI)
            db = client['aiboxdb']
            collect = db['users']

            # 計算bmi、中風機率
            bmi_value = bmi.cal(gender=self.template['性別'], cm=int(self.template['身高']), kg=int(self.template['體重']))
            bmi_result = bmi.result(bmi_value)
            self.template['bmi值'] = bmi_value
            self.template['bmi狀況'] = bmi_result
            score = 0;
            for key, value in dict(self.template).items():
                if value == 'True':
                    score = score + 1
            stroke_result = stroke_score.result(score, int(self.template['運動']), self.template['bmi狀況'])
            self.template['中風風險'] = stroke_result

            database_template = {
                '_id': collect.count() + 1,
                'nickname': self.template['專屬語'],
                'gender': self.template['性別'],
                'age': self.template['年紀'],
                'height': self.template['身高'],
                'weight': self.template['體重'],
                'health': {
                    'smoking': self.template['吸菸'],
                    'exercise': self.template['運動'],
                    'heart_problem': self.template['心律不整'],
                    'stroke': self.template['中風'],
                    'high_blood': self.template['高血壓'],
                    'high_cholesterol': self.template['高膽固醇'],
                    'diabetes': self.template['糖尿病'],
                    'bmi_value': str(self.template['bmi值']),
                    'bmi': self.template['bmi狀況'],
                    'stroke_score': self.template['中風風險']
                },
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'conversation':[],
                'daily_concern': []
            }
            collect.insert_one(database_template)
            logger.debug_msg('successfully store to database')
        except ConnectionError as err:
            logger.error_msg(err)

    # 清除user.json的欄位內容
    def clean_template(self):
        for key in dict(self.template).keys():
            if '回覆' not in key and '數字' not in key and '單位' not in key:
                self.template[key] = ''

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/user.json'), 'w', encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 上傳對話紀錄至資料庫
    @classmethod
    def store_conversation(cls, response):
        if cls.user_nickname is None:
            print('no user_nickname')
            pass
        else:
            # client = pymongo.MongoClient(MONGO_URI)
            db = client['aiboxdb']
            collect = db['users']

            conversations = {
                'question': cls.question,
                'response': response,
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            collect.find_one_and_update({'nickname': cls.user_nickname}, {'$push': {'conversation': conversations}}, upsert=False)

    # 取得未斷詞的問題句子
    @classmethod
    def get_question(cls, question, user_nickname):
        cls.question = question
        cls.user_nickname = user_nickname







