import os
import json
import pymongo
import datetime
import app.modules.logger.logging as log
from app.modules.domain_chatbot.user import User
from config import BASE_DIR, LOG_DIR, MONGO_URI, client
from app.modules.time_transfer import chin2time

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
                    if data['domain'] == '天':
                        # 若有'天'進來，把預設的今天刪除
                        self.template['天'] = self.template['天'].replace('今天', '')

                        # 若是禮拜幾的格式，檢查是否有缺禮拜"幾"
                        if '禮拜' in data['word'] or '星期' in data['word']:
                            print('禮拜流程:', data['word'])
                            day, error = chin2time.weekday_transfer(data['word'])
                            if error==True and day==None:
                                self.flag = 'reminder_day'
                                self.template['天'] = ''
                            else:
                                self.template['天'] = data['word']
                        elif '月' in data['word'] or '日' in data['word'] or '號' in data['word']:
                            self.template['天'] = self.template['天'] + data['word']

                            if '月' in self.template['天'] and '日' in self.template['天'] or '月' in self.template['天'] and '號' in self.template['天']:
                                print('幾月幾日流程:', self.template['天'])
                                day, error = chin2time.date_transfer(self.template['天'])
                                if error==True:
                                    self.flag = 'reminder_day'
                                    self.template['天'] = ''
                        else:
                            self.template['天'] = data['word']
                            print('其他流程:', self.template['天'])
                    if data['domain'] == '時段':
                        self.template['時段'] = data['word']
                    if data['domain'] == '時刻':
                        self.template['時刻'] = self.template['時刻'] + data['word']
                    if data['domain'] == 'none':
                        self.template['事情'] = self.template['事情'] + data['word']
            else:
                if self.flag == 'reminder_day':
                    for data in self.word_domain:
                        if data['domain'] == '天':
                            # 若是禮拜幾的格式，檢查是否有缺禮拜"幾"
                            if '禮拜' in data['word'] or '星期' in data['word']:
                                print('禮拜流程', data['word'])
                                day, error = chin2time.weekday_transfer(data['word'])
                                if error==True and day==None:
                                    self.flag = 'reminder_day'
                                    self.template['天'] = ''
                                else:
                                    self.template['天'] = data['word']
                            elif '月' in data['word'] or '日' in data['word'] or '號' in data['word']:
                                self.template['天'] = self.template['天'] + data['word']
                                
                                if '月' in self.template['天'] and '日' in self.template['天']:
                                    print('幾月幾日流程', self.template['天'])
                                    day, error = chin2time.date_transfer(self.template['天'])
                                    if error == True:
                                        self.flag = 'reminder_day'
                                        self.template['天'] = ''
                            else:
                                self.template['天'] = data['word']
                    if data['domain'] == '時段':
                        self.template['時段'] = data['word']
                    if data['domain'] == '時刻':
                        self.template['時刻'] = self.template['時刻'] + data['word']
                    if data['domain'] == 'none':
                        self.template['事情'] = self.template['事情'] + data['word']
                elif self.flag == 'reminder_session':
                    for data in self.word_domain:
                        if data['domain'] == '時段':
                            self.template['時段'] = data['word']
                elif self.flag == 'reminder_time':
                    for data in self.word_domain:
                        if data['domain'] == '時刻':
                            self.template['時刻'] = data['word']
                elif self.flag == 'reminder_dosomething':
                    for data in self.word_domain:
                        print('dosomething:', data)
                        if data['domain'] == 'none':
                            self.template['事情'] = data['word']
                elif self.flag == 'reminder_dosomething_check':
                    for data in self.word_domain:
                        if data['domain']=='是':
                            self.template['事情確認'] = 'true'
                        else:
                            self.template['事情'] = ''
                            self.flag = 'reminder_dosomething'
                            

        with open(os.path.join(BASE_DIR, 'domain_chatbot/template/reminder.json'), 'w',encoding='UTF-8') as output:
            json.dump(self.template, output, indent=4, ensure_ascii=False)

    # 根據缺少的word，回覆相對應的response
    def response(self):
        content = {}
        
        if self.template['天'] =='':
            content['flag'] = 'reminder_day'
            content['response'] = self.template['天回覆']
            self.store_conversation(content['response'])
        elif self.template['時段'] =='':
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
        elif self.template['事情確認'] == 'false':
            content['flag'] = 'reminder_dosomething_check'
            content['response'] = self.template['事情確認回覆'] + self.template['事情']
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
            db = client['aiboxdb']
            collect = db['reminder']
            
            # 判斷用戶是否登入，有的話加入user_nickname
            login_collect = db['login']
            login_doc = login_collect.find_one({'_id': 0})
            user_nickname = ''
            if login_doc['is_login'] == True:
                user_nickname = login_doc['user_nickname']
                
            # 轉換template的資料成date及time
            if '禮拜' in self.template['天'] or '星期' in self.template['天']:
                day, error = chin2time.weekday_transfer(self.template['天'])
            elif '月' in self.template['天'] and '日' in self.template['天'] or '號' in self.template['天']:
                day, error = chin2time.date_transfer(self.template['天'])
            else:
                day = chin2time.day_transfer(self.template['天'])
            
            time = chin2time.time_transfer(self.template['時段'], self.template['時刻'])
            remind_time = str(day) + ' ' + str(time)
            print('提醒時間轉換:', remind_time)
            
            database_template = {
                '_id': collect.count() + 1,
                'user_nickname': user_nickname,
                'remind_time': remind_time,
                'dosomething': user_nickname + '，您該' + self.template['事情'],
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(database_template)
            collect.insert_one(database_template)
            logger.debug_msg('successfully store to database')
        except ConnectionError as err:
            logger.error_msg(err)

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