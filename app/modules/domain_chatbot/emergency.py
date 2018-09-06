import os
import json
import pymongo
import app.modules.logger.logging as log
from app.modules.pinyin_compare import pinyin
from app.modules.domain_chatbot.user import User
from config import BASE_DIR, LOG_DIR, MONGO_URI, client

class Emergency:

    # 讀取emergency.json的模板並收集word
    def __init__(self, word_domain, flag):
        self.flag = flag
        self.word_domain = word_domain

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/emergency.json'), 'r', encoding='UTF-8') as input:
            self.template = json.load(input)

        self.collect_data()

    # 當處於回覆流程中，將word填入emergency.json模板中
    def collect_data(self):
        if self.word_domain is not None and self.flag is not None:
            if self.flag == 'emergency_init':
                for data in self.word_domain:
                    if data['domain'] == '緊急聯絡人':
                        self.template['緊急聯絡人拼音'] = pinyin.to_pinyin(data['word'])
            elif self.flag == 'emergency_phone':
                for data in self.word_domain:
                    if data['domain'] == '是':
                        self.template['打電話'] = "true"
                    elif data['domain'] == '非':
                        self.template['打電話'] = "false"
                                
        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/emergency.json'), 'w',encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):
        content = {}
        
        if self.template['打電話'] == '':
            content['flag'] = 'emergency_phone'
            content['response'] = self.template['問打電話回覆']
            self.store_conversation(content['response'])
        else:
            # 判斷用戶是否登入，並找到他的緊急聯絡人電話
            db = client['aiboxdb']
            login_collect = db['login']
            login_doc = login_collect.find_one({'_id': 0})
            user_nickname = ''
            if login_doc['is_login'] == True:
                user_nickname = login_doc['user_nickname']
                
                user_collect = db['users']
                user_doc = user_collect.find_one({'nickname': user_nickname})
                
                for item in user_doc['emergency_contact']:
                    if self.template['緊急聯絡人拼音'] in item['person_pinyin']:
                        self.template['電話'] = item['phone']

                content['flag'] = 'emergency_done'
                if self.template['打電話'] == 'true':
                    # 把電話號碼存進db temp_ec_phone
                    temp_ec_phone_collect = db['temp_ec_phone']
                    temp_ec_phone_doc = temp_ec_phone_collect.find_one_and_update({'_id': 0}, {'$set': {'phone': self.template['電話']}}, upsert=False)

                    content['response'] = self.template['打電話回覆']
                else:
                    content['response'] = self.template['不打電話回覆']
            else:
                content['flag'] = 'emergency_done'
                content['response'] = '請登入音箱後再使用緊急聯絡人功能'

            self.clean_template()
            self.store_conversation(content['response'])

        return json.dumps(content, ensure_ascii=False)

    # 清除emergnecy.json的欄位內容
    def clean_template(self):
        for key in dict(self.template).keys():
            if '回覆' not in key:
                self.template[key] = ''

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/emergency.json'), 'w', encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 上傳對話紀錄至資料庫
    def store_conversation(self, response):
        User.store_conversation(response)