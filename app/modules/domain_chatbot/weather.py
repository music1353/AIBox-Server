import os
import json
import pymongo
import datetime
import app.modules.logger.logging as log
from app.modules.domain_chatbot.user import User
from config import BASE_DIR, LOG_DIR, MONGO_URI
from app.modules.time_transfer import chin2time
import requests

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
                    if data['domain'] == '城市':
                        self.template['地區'] = data['word']  
            elif self.flag == 'weather_get_location':
                  for data in self.word_domain:
                    if data['domain'] == '城市':
                        self.template['地區'] = data['word']  

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/weather.json'), 'w',encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):
        content = {}
        
        if self.template['地區'] == '':
            content['flag'] = 'weather_get_location'
            content['response'] = self.template['地區回覆']
            self.store_conversation(content['response'])
        else:
            content['flag'] = 'weather_done'
            self.template['天氣回覆'] = self.get_weather(self.template['地區'])
            content['response'] = self.template['天氣回覆']
            self.clean_template()
            self.store_conversation(content['response'])

        return json.dumps(content, ensure_ascii=False)


    def get_weather(self, city):
        '''取得某地區的天氣狀況
        Args:
            city: 地區
        Returns:
            一段地區的天氣狀況文字
        '''

        city_transfer = {
            '新北': '新北市',
            '新北市': '新北市',
            '台北': '臺北市',
            '台北市': '臺北市',
            '台中': '臺中市',
            '台中市': '臺中市',
            '台南': '臺南市',
            '台南市': '臺南市'
        }
        
        for key, values in  city_transfer.items():
            if city == key:
                city = values

        has_city = False
        wx = '' # 天氣現象
        maxT = '' # 最高溫度
        minT = '' # 最低溫度
        ci = '' # 舒適度
        pop = '' # 降雨機率

        # 政府開放資料, 天氣api
        resp = requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314')
        data = json.loads(resp.text)
        records = data['records']['location'] # 各地區的預報紀錄

        for record in records:
            if record['locationName'] == city:
                has_city = True
                elements = record['weatherElement']
                for element in elements:
                    if element['elementName'] == 'Wx': # 天氣現象
                        wx = element['time'][-1]['parameter']['parameterName']
                    if element['elementName'] == 'MaxT': # 最高溫度
                        maxT = element['time'][-1]['parameter']['parameterName']
                    if element['elementName'] == 'MinT': # 最低溫度
                        minT = element['time'][-1]['parameter']['parameterName']
                    if element['elementName'] == 'CI': # 舒適度
                        ci = element['time'][-1]['parameter']['parameterName']
                    if element['elementName'] == 'PoP': # 降雨機率
                        pop = element['time'][-1]['parameter']['parameterName']

        if has_city:
            return '{0}的天氣{1},最高溫度來到{2}度,最低溫度{3}度,{4},降雨機率{5}趴'.format(city, wx, maxT, minT, ci, pop)
        else:
            return '沒有此地區的天氣狀況'


    # 清除location.json的欄位內容
    def clean_template(self):
        
        for key in dict(self.template).keys():
            if self.template[key] != '地區回覆':
                self.template[key] = ''

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/weather.json'), 'w', encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 上傳對話紀錄至資料庫
    def store_conversation(self, response):
        User.store_conversation(response)