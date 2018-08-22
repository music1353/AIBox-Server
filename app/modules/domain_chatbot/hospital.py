import os
import json
import pymongo
import datetime
import app.modules.logger.logging as log
from app.modules.domain_chatbot.user import User
from config import BASE_DIR, LOG_DIR, MONGO_URI, client

class Hospital:

    # 讀取hospital.json的模板並收集word
    def __init__(self, word_domain, flag):
        self.flag = flag
        self.word_domain = word_domain

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/hospital.json'), 'r', encoding='UTF-8') as input:
            self.template = json.load(input)

        self.collect_data()

    # 當處於回覆流程中，將word填入hospital.json模板中
    def collect_data(self):
        if self.word_domain is not None and self.flag is not None:
            if self.flag == 'hospital_init':
                for data in self.word_domain:
                    if data['domain'] == '醫院':
                        self.template['醫院'] = data['word']
                    if data['domain'] == '醫院問題':
                        self.template['醫院問題'] = data['word']
            else:
                if self.flag == 'hospital_ques_get':
                    for data in self.word_domain:
                        if data['domain'] == '醫院問題':
                            self.template['醫院問題'] = data['word']
                                
        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/hospital.json'), 'w',encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):
        content = {}
        
        if self.template['醫院問題'] == '':
            content['flag'] = 'hospital_ques_get'
            content['response'] = self.template['醫院問題回覆']
            self.store_conversation(content['response'])
        else:
            # 去醫院開放資料找到對應的資訊
            db = client['aiboxdb']
            hospital_collect = db['hospital']
            hospital_doc = hospital_collect.find_one({'機構名稱': {'$regex': self.template['醫院']}})

            # 回覆查到的資訊
            if self.template['醫院問題'] in hospital_doc:
                self.template['查詢結果'] = '{0}的{1}是{2}'.format(self.template['醫院'], self.template['醫院問題'], hospital_doc[self.template['醫院問題']])
            else:
                self.template['查詢結果'] = '沒有查詢到您想要的資訊'

            content['flag'] = 'hospital_done'
            content['response'] = self.template['查詢結果']
            
            self.clean_template()
            self.store_conversation(content['response'])

        return json.dumps(content, ensure_ascii=False)

    # 清除hospital.json的欄位內容
    def clean_template(self):
        
        for key in dict(self.template).keys():
            if '回覆' not in key:
                self.template[key] = ''

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/hospital.json'), 'w', encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 上傳對話紀錄至資料庫
    def store_conversation(self, response):
        User.store_conversation(response)