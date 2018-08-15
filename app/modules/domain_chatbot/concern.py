import os
import json
import pymongo
import datetime
import app.modules.logger.logging as log
from app.modules.health_calculator import blood_pressure
from config import BASE_DIR, LOG_DIR, MONGO_URI, client
from flask import session
import requests
from app.modules.time_transfer import chin2time

'''關心使用者的身體健康狀況
morning流程:
    1. morning_init: 初始化
    2. morning_dining: 是否用早餐
    3. morning_measure_blood_pressure: 是否測量血壓
        True -> 4.
        False -> 7.
    4. morning_record_blood_pressure: 是否紀錄血壓
        True -> 5.
        False -> 7.
    5. morning_diastolic_blood_pressure: 紀錄舒張壓
    6. morning_systolic_blood_pressure: 紀錄收縮壓
    7. morning_concern_done: 早上關心完成

noon流程:
    1. noon_init: 初始化
    2. noon_dining: 是否用中餐
    3. noon_snap: 是否要小睡一下
        True -> 4.
        False -> 5.
    4. noon_set_clock: 設定鬧鐘
    5. noon_concern_done: 中午關心完成

night流程:
    1. night_init: 初始化
    2. night_dining: 是否用晚餐
    3. night_measure_blood_pressure: 是否測量血壓
        True -> 4.
        False -> 7.
    4. night_record_blood_pressure: 是否紀錄血壓
        True -> 5.
        False -> 7.
    5. night_diastolic_blood_pressure: 紀錄舒張壓
    6. night_systolic_blood_pressure: 紀錄收縮壓
    7. night_concern_done: 晚上關心完成
'''

class Concern:
    # 讀取對應的關心模板並收集word
    def __init__(self, word_domain=None, flag=None, nickname=None):
        self.flag = flag
        self.word_domain = word_domain
        self.nickname = nickname

        # 判斷是哪種concern, 就選擇那種模板
        if 'morning' in self.flag:
            with open(os.path.join(BASE_DIR, 'domain_chatbot/template/morning_concern.json'), 'r', encoding='UTF-8') as input:
                self.template = json.load(input)
        elif 'noon' in self.flag:
            with open(os.path.join(BASE_DIR, 'domain_chatbot/template/noon_concern.json'), 'r', encoding='UTF-8') as input:
                self.template = json.load(input)
        elif 'night' in self.flag:
            with open(os.path.join(BASE_DIR, 'domain_chatbot/template/night_concern.json'), 'r', encoding='UTF-8') as input:
                self.template = json.load(input)

        self.collect_data()

    # 當處於回覆流程中，將word填入對應的關心模板中
    def collect_data(self):
        if self.word_domain is not None and self.flag is not None:
            if 'morning' in self.flag:
                if self.flag == 'morning_init':
                    pass
                elif self.flag == 'morning_dining':
                    for data in self.word_domain:
                        if data['domain'] == '是':
                            self.template['用餐'] = 'True'
                            break
                        if data['domain'] == '非':
                            self.template['用餐'] = 'False'
                            break
                elif self.flag == 'morning_measure_blood_pressure':
                    for data in self.word_domain:
                        if data['domain'] == '是':
                            self.template['量血壓'] = 'True'
                            break
                        if data['domain'] == '非':
                            self.template['量血壓'] = 'False'
                            break
                elif self.flag == 'morning_record_blood_pressure':
                    for data in self.word_domain:
                        if data['domain'] == '是':
                            self.template['紀錄血壓'] = 'True'
                            break
                        if data['domain'] == '非':
                            self.template['紀錄血壓'] = 'False'
                            break
                elif self.flag == 'morning_record_diastolic_blood_pressure':
                    for data in self.word_domain:
                        if data['domain'] == '數字':
                            self.template['紀錄舒張壓'] = data['word']
                elif self.flag == 'morning_record_systolic_blood_pressure':
                    for data in self.word_domain:
                        if data['domain'] == '數字':
                            self.template['紀錄收縮壓'] = data['word']
                
                with open(os.path.join(BASE_DIR, 'domain_chatbot/template/morning_concern.json'), 'w',encoding='UTF-8') as output:
                  json.dump(self.template, output, indent=4, ensure_ascii=False)

            elif 'noon' in self.flag:
                if self.flag == 'noon_init':
                    pass
                elif self.flag == 'noon_dining':
                    for data in self.word_domain:
                        if data['domain'] == '是':
                            self.template['用餐'] = 'True'
                            break
                        if data['domain'] == '非':
                            self.template['用餐'] = 'False'
                            break
                elif self.flag == 'noon_snap':
                    for data in self.word_domain:
                        if data['domain'] == '是':
                            self.template['小睡'] = 'True'
                            break
                        if data['domain'] == '非':
                            self.template['小睡'] = 'False'
                            break
                elif self.flag == 'noon_set_clock':
                    for data in self.word_domain:
                        if data['domain'] == '時刻':
                            self.template['鬧鐘'] = self.template['鬧鐘'] + data['word']

                with open(os.path.join(BASE_DIR, 'domain_chatbot/template/noon_concern.json'), 'w',encoding='UTF-8') as output:
                  json.dump(self.template, output, indent=4, ensure_ascii=False)

            elif 'night' in self.flag:
                if self.flag == 'night_init':
                    pass
                elif self.flag == 'night_dining':
                    for data in self.word_domain:
                        if data['domain'] == '是':
                            self.template['用餐'] = 'True'
                            break
                        if data['domain'] == '非':
                            self.template['用餐'] = 'False'
                            break
                elif self.flag == 'night_measure_blood_pressure':
                    for data in self.word_domain:
                        if data['domain'] == '是':
                            self.template['量血壓'] = 'True'
                            break
                        if data['domain'] == '非':
                            self.template['量血壓'] = 'False'
                            break
                elif self.flag == 'night_record_blood_pressure':
                    for data in self.word_domain:
                        if data['domain'] == '是':
                            self.template['紀錄血壓'] = 'True'
                            break
                        if data['domain'] == '非':
                            self.template['紀錄血壓'] = 'False'
                            break
                elif self.flag == 'night_record_diastolic_blood_pressure':
                    for data in self.word_domain:
                        if data['domain'] == '數字':
                            self.template['紀錄舒張壓'] = data['word']
                elif self.flag == 'night_record_systolic_blood_pressure':
                    for data in self.word_domain:
                        if data['domain'] == '數字':
                            self.template['紀錄收縮壓'] = data['word']
                
                with open(os.path.join(BASE_DIR, 'domain_chatbot/template/night_concern.json'), 'w',encoding='UTF-8') as output:
                  json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):
        content = {}

        if 'morning' in self.flag:
            if self.template['用餐'] == '':
                content['flag'] = 'morning_dining'
                if self.nickname is not None:
                    content['response'] = self.nickname + '，' + self.template['用餐回覆']
                else:
                    content['response'] = self.template['用餐回覆']
            elif self.template['量血壓'] == '':
                content['flag'] = 'morning_measure_blood_pressure'
                content['response'] = self.template['量血壓回覆']
            elif self.template['量血壓']!='' and self.template['量血壓']=='False':
                content['flag'] = 'morning_concern_done'
                content['response'] = self.template['未量血壓回覆']
                self.store_database()
                self.clean_template()
            elif self.template['紀錄血壓'] == '':
                content['flag'] = 'morning_record_blood_pressure'
                content['response'] = self.template['紀錄血壓回覆']
            elif self.template['紀錄舒張壓']=='' and self.template['紀錄血壓']=='True':
                content['flag'] = 'morning_record_diastolic_blood_pressure'
                content['response'] = self.template['紀錄舒張壓回覆']
            elif self.template['紀錄收縮壓']=='' and self.template['紀錄血壓']=='True':
                content['flag'] = 'morning_record_systolic_blood_pressure'
                content['response'] = self.template['紀錄收縮壓回覆']
            elif self.template['紀錄舒張壓']!='' and self.template['紀錄收縮壓']!='':
                content['flag'] = 'morning_concern_done'

                diastolic = int(self.template['紀錄舒張壓'])
                systolic = int(self.template['紀錄收縮壓'])
                cal_result = blood_pressure.cal_pressure(diastolic, systolic)
                if cal_result == '正常':
                    self.template['血壓狀況'] = '正常'
                    content['response'] = self.template['正常血壓回覆']
                    self.store_database()
                    self.clean_template()
                elif cal_result == '高':
                    self.template['血壓狀況'] = '高'
                    content['response'] = self.template['高血壓回覆']
                    self.store_database()
                    self.clean_template()
                elif cal_result == '低':
                    self.template['血壓狀況'] = '低'
                    content['response'] = self.template['低血壓回覆']
                    self.store_database()
                    self.clean_template()
            else:
                content['flag'] = 'morning_concern_done'
                content['response'] = self.template['完成回覆']
                self.store_database()
                self.clean_template()

            return json.dumps(content, ensure_ascii=False)

        elif 'noon' in self.flag:
            if self.template['用餐'] == '':
                content['flag'] = 'noon_dining'
                if self.nickname is not None:
                    content['response'] = self.nickname + '，' + self.template['用餐回覆']
                else:
                    content['response'] = self.template['用餐回覆']
            elif self.template['小睡'] == '':
                print('snapppp:', self.template['用餐'])
                content['flag'] = 'noon_snap'
                content['response'] = self.template['小睡回覆']
            elif self.template['小睡']!='' and self.template['小睡']=='False':
                content['flag'] = 'noon_concern_done'
                content['response'] = self.template['完成回覆']
                self.store_database()
                self.clean_template()
            elif self.template['小睡']=='True' and self.template['鬧鐘']=='':
                content['flag'] = 'noon_set_clock'
                content['response'] = self.template['鬧鐘回覆']
            else:
                content['flag'] = 'noon_concern_done'
                content['response'] = self.template['完成回覆']
                self.store_database()
                self.clean_template()

            return json.dumps(content, ensure_ascii=False)

        elif 'night' in self.flag:
            if self.template['用餐'] == '':
                content['flag'] = 'night_dining'
                if self.nickname is not None:
                    content['response'] = self.nickname + '，' + self.template['用餐回覆']
                else:
                    content['response'] = self.template['用餐回覆']
            elif self.template['量血壓'] == '':
                content['flag'] = 'night_measure_blood_pressure'
                content['response'] = self.template['量血壓回覆']
            elif self.template['量血壓']!='' and self.template['量血壓']=='False':
                content['flag'] = 'night_concern_done'
                content['response'] = self.template['未量血壓回覆']
                self.store_database()
                self.clean_template()
            elif self.template['紀錄血壓'] == '':
                content['flag'] = 'night_record_blood_pressure'
                content['response'] = self.template['紀錄血壓回覆']
            elif self.template['紀錄舒張壓']=='' and self.template['紀錄血壓']=='True':
                content['flag'] = 'night_record_diastolic_blood_pressure'
                content['response'] = self.template['紀錄舒張壓回覆']
            elif self.template['紀錄收縮壓']=='' and self.template['紀錄血壓']=='True':
                content['flag'] = 'night_record_systolic_blood_pressure'
                content['response'] = self.template['紀錄收縮壓回覆']
            elif self.template['紀錄舒張壓']!='' and self.template['紀錄收縮壓']!='':
                content['flag'] = 'night_concern_done'

                diastolic = int(self.template['紀錄舒張壓'])
                systolic = int(self.template['紀錄收縮壓'])
                cal_result = blood_pressure.cal_pressure(diastolic, systolic)
                if cal_result == '正常':
                    self.template['血壓狀況'] = '正常'
                    content['response'] = self.template['正常血壓回覆']
                    self.store_database()
                    self.clean_template()
                elif cal_result == '高':
                    self.template['血壓狀況'] = '高'
                    content['response'] = self.template['高血壓回覆']
                    self.store_database()
                    self.clean_template()
                elif cal_result == '低':
                    self.template['血壓狀況'] = '低'
                    content['response'] = self.template['低血壓回覆']
                    self.store_database()
                    self.clean_template()
            else:
                content['flag'] = 'night_concern_done'
                content['response'] = self.template['完成回覆']
                self.store_database()
                self.clean_template()

            return json.dumps(content, ensure_ascii=False)
            

    # 關心資料上傳至資料庫
    def store_database(self):
        logger = log.Logging('morning_concern:store_database')
        logger.run(LOG_DIR)

        try:
            db = client['aiboxdb']
            user_collect = db['users']

            # 取得concern_lock的登入user_nickname
            concern_lock_collect = db['concern_lock']
            concern_lock_doc = concern_lock_collect.find_one({'_id': 0})
            if concern_lock_doc['lock'] == True:
                user_nickname = concern_lock_doc['user_nickname']
            
            if 'morning' in self.flag:
                daily_concern = {
                    'type': 'morning',
                    'dining': self.template['用餐'],
                    'diastolic': self.template['紀錄舒張壓'],
                    'systolic': self.template['紀錄收縮壓'],
                    'blood_pressure_status': self.template['血壓狀況'],
                    'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                user_collect.find_one_and_update({'nickname': user_nickname}, {'$push': {'daily_concern': daily_concern}}, upsert=False)

            elif 'noon' in self.flag:
                daily_concern = {
                    'type': 'noon',
                    'dining': self.template['用餐'],
                    'snap': self.template['小睡'],
                    'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                user_collect.find_one_and_update({'nickname': user_nickname}, {'$push': {'daily_concern': daily_concern}}, upsert=False)

                # 紀錄鬧鐘到reminder
                if self.template['小睡']=='True' and self.template['鬧鐘']!='':
                    day = datetime.date.today()
                    time = chin2time.time_transfer('下午', self.template['鬧鐘'])
                    remind_time = str(day) + ' ' + str(time)
                    print('關心鬧鐘時間轉換:', remind_time)

                    reminder_collect = db['reminder']
                    database_template = {
                        '_id': reminder_collect.count() + 1,
                        'user_nickname': user_nickname,
                        'remind_time': remind_time,
                        'dosomething': '起床',
                        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    reminder_collect.insert_one(database_template)

            elif 'night' in self.flag:
                daily_concern = {
                    'type': 'night',
                    'dining': self.template['用餐'],
                    'diastolic': self.template['紀錄舒張壓'],
                    'systolic': self.template['紀錄收縮壓'],
                    'blood_pressure_status': self.template['血壓狀況'],
                    'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                user_collect.find_one_and_update({'nickname': user_nickname}, {'$push': {'daily_concern': daily_concern}}, upsert=False)
                    
        except Exception as err:
            print('Concern Error:', err)
            logger.error_msg(err)

    # 清除對應關心的欄位內容
    def clean_template(self):
        if 'morning' in self.flag:
            for key in dict(self.template).keys():
                if '回覆' not in key:
                    self.template[key] = ''

            with open(os.path.join(BASE_DIR, 'domain_chatbot/template/morning_concern.json'), 'w', encoding='UTF-8') as output:
                json.dump(self.template, output, indent=4, ensure_ascii=False)

        if 'noon' in self.flag:
            for key in dict(self.template).keys():
                if '回覆' not in key:
                    self.template[key] = ''

            with open(os.path.join(BASE_DIR, 'domain_chatbot/template/noon_concern.json'), 'w', encoding='UTF-8') as output:
                json.dump(self.template, output, indent=4, ensure_ascii=False)

        elif 'night' in self.flag:
            for key in dict(self.template).keys():
                if '回覆' not in key:
                    self.template[key] = ''

            with open(os.path.join(BASE_DIR, 'domain_chatbot/template/night_concern.json'), 'w', encoding='UTF-8') as output:
                json.dump(self.template, output, indent=4, ensure_ascii=False)







