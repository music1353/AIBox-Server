import os
import json
import pymongo
import datetime
import app.modules.logger.logging as log
from app.modules.domain_chatbot.user import User
from config import BASE_DIR, LOG_DIR, MONGO_URI

class Location:

    # 讀取location.json的模板並收集word
    def __init__(self, word_domain, flag):
        self.flag = flag
        self.word_domain = word_domain

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/location.json'), 'r', encoding='UTF-8') as input:
            self.template = json.load(input)

        self.collect_data()

    # 當處於回覆流程中，將word填入location.json模板中
    def collect_data(self):
        if self.word_domain is not None and self.flag is not None:
            if self.flag == 'location_init':
                for data in self.word_domain:
                    if data['domain'] == '地點':
                        self.template['地點'] = data['word']
                    if data['domain'] == '城市':
                        self.template['區域'] = data['word']
                    # 180706, 新增street.json
                    if data['domain'] == '街道':
                        self.template['區域'] = self.template['區域'] + data['word']
                    if data['domain'] == '距離':
                        self.template['距離'] = data['word']
                    if data['domain'] == '數字':
                        self.template['數字'] = data['word']
            else:
                if self.flag == 'location_get':
                    for data in self.word_domain:
                        if data['domain'] == '地點':
                            self.template['地點'] = data['word']
                elif self.flag == 'location_region':
                    for data in self.word_domain:
                        if data['domain'] == '城市':
                            self.template['區域'] = data['word']
                elif self.flag == 'location_distance':
                    for data in self.word_domain:
                        if data['domain'] == '是非':
                            if data['word'] == '有' or data['word'] == '會' or data['word'] == '沒錯' or data['word'] == '是':
                                self.template['距離'] = 'True'
                            else:
                                self.template['距離'] = 'False'
        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/location.json'), 'w',encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):
        content = {}
        if self.template['地點'] != '':
            if self.template['距離'] != '':
                if self.template['距離'] == 'True':
                    content['flag'] = 'location_done'
                    content['response'] = self.template['完成回覆']
                    self.store_database()
                    self.clean_template()
                    self.store_conversation(content['response'])
                elif self.template['區域'] != '':
                    content['flag'] = 'location_done'
                    content['response'] = self.template['完成回覆']
                    self.store_database()
                    self.clean_template()
                    self.store_conversation(content['response'])
                else:
                    content['flag'] = 'location_region'
                    content['response'] = self.template['區域回覆']
                    self.store_conversation(content['response'])
            elif self.template['區域'] != '':
                content['flag'] = 'location_done'
                content['response'] = self.template['完成回覆']
                self.store_database()
                self.clean_template()
                self.store_conversation(content['response'])
            else:
                content['flag'] = 'location_distance'
                content['response'] = self.template['距離回覆']
                self.store_conversation(content['response'])
        else:
            content['flag'] = 'location_get'
            content['response'] = self.template['地點回覆']
            self.store_conversation(content['response'])

        return json.dumps(content, ensure_ascii=False)

    # 地點上傳至資料庫
    def store_database(self):
        logger = log.Logging('location:store_database')
        logger.run(LOG_DIR)
        try:
            client = pymongo.MongoClient(MONGO_URI)
            db = client['aiboxdb']
            collect = db['location']

            database_template = {
                '_id': collect.count() + 1,
                'location': self.template['地點'],
                'region': self.template['區域'],
                'distance': self.template['距離'],
                'number': self.template['數字'],
                'unit': self.template['單位'],
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            collect.insert_one(database_template)
            logger.debug_msg('successfully store to database')
        except ConnectionError as err:
            logger.error_msg(err)

    # 清除location.json的欄位內容
    def clean_template(self):
        self.template['數字'] = 1000
        self.template['單位'] = '公尺'
        for key in dict(self.template).keys():
            if '回覆' not in key and '數字' not in key and '單位' not in key:
                self.template[key] = ''

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/location.json'), 'w', encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 上傳對話紀錄至資料庫
    def store_conversation(self, response):
        User.store_conversation(response)