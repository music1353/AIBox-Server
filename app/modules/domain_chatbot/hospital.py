import os
import json
import pymongo
import datetime
import app.modules.logger.logging as log
from app.modules.pinyin_compare import pinyin
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
                        # self.template['醫院'] = data['word']
                        self.template['醫院拼音'] = pinyin.to_pinyin(data['word'])
                    if data['domain'] == '醫院問題':
                        self.template['醫院問題'] = data['word']
            elif self.flag == 'hospital_ques_get':
                for data in self.word_domain:
                    if data['domain'] == '醫院問題':
                        self.template['醫院問題'] = data['word']
            elif self.flag == 'hospital_phone':
                for data in self.word_domain:
                    if data['domain'] == '是':
                        self.template['打電話'] = data['word']
                    elif data['domain'] == '非':
                        self.template['不打電話'] = data['word']
            elif self.flag == 'hospital_address':
                for data in self.word_domain:
                    if data['domain'] == '是':
                        self.template['導航地址'] = data['word']
                    elif data['domain'] == '非':
                        self.template['不導航地址'] = data['word']

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
            hospital_doc = hospital_collect.find_one({'拼音機構名稱': {'$regex': self.template['醫院拼音']}})

            flag = ''
            response = ''
            # 回覆查到的資訊
            if self.template['醫院問題'] in hospital_doc and hospital_doc != None:
                self.template['醫院'] = hospital_doc['機構名稱']

                # 若是問電話，則問是否需要撥打電話
                if self.template['醫院問題'] == '電話':
                    if self.template['打電話'] != '':
                        flag = 'hospital_done'
                        response = self.template['打電話回覆']
                        self.clean_template()
                    elif self.template['不打電話'] != '':
                        flag = 'hospital_done'
                        response = self.template['不打電話回覆']
                        self.clean_template()
                    else:
                        response = '{0}的{1}是{2},{3}'.format(self.template['醫院'], self.template['醫院問題'], hospital_doc[self.template['醫院問題']], self.template['電話問題回覆'])
                        flag = 'hospital_phone'
                # 若是問地址，則問是否需要導航地址
                elif self.template['醫院問題'] == '地址':
                    if self.template['導航地址'] != '':
                        flag = 'hospital_done'
                        response = self.template['導航地址回覆']
                        self.clean_template()
                    elif self.template['不導航地址'] != '':
                        flag = 'hospital_done'
                        response = self.template['不導航地址回覆']
                        self.clean_template()
                    else:
                        response = '{0}的{1}是{2},{3}'.format(self.template['醫院'], self.template['醫院問題'], hospital_doc[self.template['醫院問題']], self.template['地址問題回覆'])
                        flag = 'hospital_address'
                else:
                    response = '{0}的{1}是{2}'.format(self.template['醫院'], self.template['醫院問題'], hospital_doc[self.template['醫院問題']])
                    flag = 'hospital_done'
                    self.clean_template()
            else:
                self.template['查詢結果'] = '沒有查詢到您想要的資訊'
                self.clean_template()

            content['flag'] = flag
            content['response'] = response

            self.store_conversation(content['response'])
            if self.template['醫院'] != '':
                self.store_conversation('醫院名稱: ' + self.template['醫院'])

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