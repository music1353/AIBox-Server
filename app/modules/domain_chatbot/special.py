import json


class Special:

    def response(self):
        content = {}
        content['flag'] = 'special_done'
        content['response'] = '我聽不懂，請您使用其他服務'
        return json.dumps(content, ensure_ascii=False)
