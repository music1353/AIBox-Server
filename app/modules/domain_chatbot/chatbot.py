from app.modules.domain_chatbot.user import User
from app.modules.domain_chatbot.disease import Disease
from app.modules.domain_chatbot.location import Location
from app.modules.domain_chatbot.reminder import Reminder
from app.modules.domain_chatbot.special import Special

class Chatbot:

    # 取domain不為'none'的，flag為'user_nickname'不需剔除
    def __init__(self, domain_score, flag=None):

        if flag == 'user_nickname':
            word_domain = []
            for domain in domain_score:
                dic = {}
                dic['word'] = domain['word']
                dic['domain'] = domain['domain']
                word_domain.append(dic)
        else:
            word_domain = []
            for domain in domain_score:
                # 280712, 不過濾none
                dic = {}
                dic['word'] = domain['word']
                dic['domain'] = domain['domain']
                word_domain.append(dic)
                '''
                這是原本代碼
                if domain['domain'] != 'none':
                    dic = {}
                    dic['word'] = domain['word']
                    dic['domain'] = domain['domain']
                    word_domain.append(dic)
                '''
                

        self.word_domain = word_domain
        self.flag = flag

    # 根據flag及domain決定選擇哪個模組的覆流程
    # flag -> None or user_done or disease_done or location_done 表示完成該模組的回覆流程
    # flag -> user_xxx or disease_xxx or loaction_xxx 表處於哪個模組的回覆流程中
    def response_word(self):
        if self.flag is None or self.flag=='user_done' or self.flag=='disease_done' or self.flag=='location_done' or self.flag=='reminder_done':
            domain = self.choose_domain()
            if domain == 'user':
                user = User()
                return user.response()
            # 決定為disease的模組流程，可先收集word
            elif domain == 'disease':
                disease = Disease(word_domain=self.word_domain, flag='disease_get')
                return disease.response()
            # 決定為location的模組流程，可先收集word
            elif domain == 'location':
                location = Location(word_domain=self.word_domain, flag='location_init')
                return location.response()
            # 決定為reminder的模組流程，可先收集word
            elif domain == 'reminder':
                reminder = Reminder(word_domain=self.word_domain, flag='reminder_init')
                return reminder.response()
            # 決定為special(domain=none)的流程
            else:
                special = Special()
                return special.response()
        else:
            if 'user' in self.flag:
                user = User(word_domain=self.word_domain, flag=self.flag)
                return user.response()
            elif 'disease' in self.flag:
                disease = Disease(word_domain=self.word_domain, flag=self.flag)
                return disease.response()
            elif 'location' in self.flag:
                location = Location(word_domain=self.word_domain, flag=self.flag)
                return location.response()
            elif 'reminder' in self.flag:
                reminder = Reminder(word_domain=self.word_domain, flag=self.flag)
                return reminder.response()

    # 選擇哪個domain模組的回覆流程
    def choose_domain(self):
        isUser = False
        isDisease = False
        isLocation = False
        isReminder = False

        for data in self.word_domain:
            if data['domain'] == '個人化' or data['domain'] == '性別':
                isUser = True
            if data['domain'] == '感冒' or data['domain'] == '慢性病':
                isDisease = True
            if data['domain'] == '地點' or data['domain'] == '數字' or data['domain'] == '城市' or data['domain'] == '距離':
                isLocation = True
            if data['domain'] == '提醒':
                isReminder = True

        if isUser:
            return 'user'
        elif isDisease:
            return 'disease'
        elif isLocation:
            return 'location'
        elif isReminder:
            return 'reminder'
        # domain為none的情況
        else:
            return 'none'
