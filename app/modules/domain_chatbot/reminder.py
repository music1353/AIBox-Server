import os
import json
import pymongo
import datetime
import app.modules.logger.logging as log
from app.modules.domain_chatbot.user import User
from config import BASE_DIR, LOG_DIR, MONGO_URI

class Reminder:

    # 讀取reminder.json的模板並收集word
    def __init__(self, word_domain, flag):
        self.flag = flag
        self.word_domain = word_domain

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/reminder.json'), 'r', encoding='UTF-8') as input:
            self.template = json.load(input)

        self.collect_data()

    # 當處於回覆流程中，將word填入reminder.json模板中
    def collect_data(self):
        if self.word_domain is not None and self.flag is not None:
            if self.flag == 'reminder_init':
                for data in self.word_domain:
                    if data['domain'] == '時段':
                        self.template['時段'] = data['word']
                    if data['domain'] == '時刻':
                        self.template['時刻'] = data['word']
                    if data['domain'] == 'none':
                        self.template['事情'] = self.template['事情'] + data['word']
            else:
                if self.flag == 'reminder_session':
                    for data in self.word_domain:
                        if data['domain'] == '時段':
                            self.template['時段'] = data['word']
                elif self.flag == 'reminder_time':
                    for data in self.word_domain:
                        if data['domain'] == '時刻':
                            self.template['時刻'] = data['word']
                elif self.flag == 'reminder_dosomething':
                    for data in self.word_domain:
                        print('dosome data', data)
                        if data['domain'] == 'none':
                            self.template['事情'] = data['word']
                            

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/reminder.json'), 'w',encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):
        content = {}
        
        if self.template['時段'] =='':
            content['flag'] = 'reminder_session'
            content['response'] = self.template['時段回覆']
            self.store_conversation(content['response'])
        elif self.template['時刻'] == '':
            content['flag'] = 'reminder_time'
            content['response'] = self.template['時刻回覆']
            self.store_conversation(content['response'])
        elif self.template['事情'] == '':
            content['flag'] = 'reminder_dosomething'
            content['response'] = self.template['事情回覆']
            self.store_conversation(content['response'])
        else:
            content['flag'] = 'reminder_done'
            content['response'] = self.template['完成回覆']
            self.store_database()
            self.clean_template()
            self.store_conversation(content['response'])

        return json.dumps(content, ensure_ascii=False)

    # 提醒上傳至資料庫
    def store_database(self):
        logger = log.Logging('reminder:store_database')
        logger.run(LOG_DIR)
        try:
            client = pymongo.MongoClient(MONGO_URI)
            db = client['aiboxdb']
            collect = db['reminder']

            database_template = {
                '_id': collect.count() + 1,
                'session': self.template['時段'],
                'time': self.template['時刻'],
                'dosomething': self.template['事情'],
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            collect.insert_one(database_template)
            logger.debug_msg('successfully store to database')
        except ConnectionError as err:
            logger.error_msg(err)

    # 清除location.json的欄位內容
    def clean_template(self):
        for key in dict(self.template).keys():
            if '回覆' not in key and '數字' not in key and '單位' not in key:
                self.template[key] = ''

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/reminder.json'), 'w', encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 上傳對話紀錄至資料庫
    def store_conversation(self, response):
        User.store_conversation(response)