import json


class Special:

    def response(self):
        content = {}
        content['flag'] = 'special_done'
        content['response'] = '我聽不懂...'
        return json.dumps(content, ensure_ascii=False)
