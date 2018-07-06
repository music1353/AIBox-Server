import requets
import json

flag = ''
sentence = '請問台北市中山路的餐廳'
response_info = {'flag': flag, 'response': sentence}
message = requests.post("http://127.0.0.1:5000/api/chatbot", json=response_info)
print(message.text)
dic = json.loads(message.text)