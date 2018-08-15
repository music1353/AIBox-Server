import os
import json
import pymongo
import app.modules.logger.logging as log
from app.modules.domain_chatbot.user import User
import datetime
from config import BASE_DIR, LOG_DIR, MONGO_URI, client

class Disease:
    # 讀取disease.json的模板並收集word
    def __init__(self, word_domain=None, flag=None):
        self.flag = flag
        self.word_domain = word_domain

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/disease.json'), 'r', encoding='UTF-8') as input:
            self.template = json.load(input)

        self.collect_data()

    # 當處於回覆流程中，將word填入disease.json模板中
    def collect_data(self):
        if self.word_domain is not None and self.flag is not None:
            if self.flag == 'disease_get':
                for data in self.word_domain:
                    if data['domain'] == '慢性病':
                        self.template['疾病'] = data['word']
                        self.template['類別'] = 'chronic'
                    elif data['domain'] == '感冒':
                        self.template['疾病'] = data['word']
                        self.template['類別'] = 'cold'
        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/disease.json'), 'w', encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):

        content = {}
        if self.template['疾病'] != '':
            content['flag'] = 'disease_done'
            self.template['疾病回覆'] = self.get_data_form_database()
            content['response'] = self.template['疾病回覆']
            self.store_conversation(content['response'])

        self.clean_template()

        return json.dumps(content, ensure_ascii=False)

    # 從資料庫取得疾病知識
    def get_data_form_database(self):
        logger = log.Logging('disease:get_data_form_database')
        logger.run(LOG_DIR)
        try:
            db = client['aiboxdb']
            if self.template['類別'] == 'cold':
                collect = db['cold']
            elif self.template['類別'] == 'chronic':
                collect = db['chronic']

            disease_collect = collect.find_one({'name': self.template['疾病']})
            if disease_collect is not None:
                disease_articles = disease_collect['articles']
                for article in disease_articles:
                    logger.debug_msg('successfully get data from database')
                    return article

            return '沒有關於此疾病的資料'

        except ConnectionError as err:
            logger.error_msg(err)

    # 清除disease.json的欄位內容
    def clean_template(self):
        for key in dict(self.template).keys():
            self.template[key] = ''

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/disease.json'), 'w', encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 上傳對話紀錄至資料庫
    def store_conversation(self, response):
        User.store_conversation(response)
