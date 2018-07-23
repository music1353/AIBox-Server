import os
import json
import pymongo
import datetime
import app.modules.logger.logging as log
from app.modules.domain_chatbot.user import User
from config import BASE_DIR, LOG_DIR, MONGO_URI
from app.modules.time_transfer import chin2time

class Weather:

    # 讀取weather.json的模板並收集word
    def __init__(self, word_domain, flag):
        self.flag = flag
        self.word_domain = word_domain

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/weather.json'), 'r', encoding='UTF-8') as input:
            self.template = json.load(input)

        self.collect_data()

    # 當處於回覆流程中，將word填入weather.json模板中
    def collect_data(self):
        if self.word_domain is not None and self.flag is not None:
            if self.flag == 'weather_init':
                for data in self.word_domain:
                    if data['domain'] == '區域':
                        self.template['區域'] = data['word']  
            elif self.flag == 'weather_get_location':
                  for data in self.word_domain:
                    if data['domain'] == '區域':
                        self.template['區域'] = data['word']  

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/weather.json'), 'w',encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):
        content = {}
        
        if self.template['區域'] =='':
            content['flag'] = 'weather_get_location'
            content['response'] = self.template['區域回覆']
            self.store_conversation(content['response'])
        else:
            content['flag'] = 'weather_done'
            content['response'] = self.template['天氣｀回覆']
            self.clean_template()
            self.store_conversation(content['response'])

        return json.dumps(content, ensure_ascii=False)


    # 清除location.json的欄位內容
    def clean_template(self):
        
        self.template['天'] = '今天'
        self.template['事情確認'] = 'false'
        
        for key in dict(self.template).keys():
            if '回覆' not in key and '天' not in key and '事情確認' not in key:
                self.template[key] = ''

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/reminder.json'), 'w', encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 上傳對話紀錄至資料庫
    def store_conversation(self, response):
        User.store_conversation(response)