# AIBox-Server

> 基於Python Flask所搭建的智慧音箱Server



## Requirements

* jieba==0.39
* Flask==0.12.2
* gensim==3.1.0
* pymongo==3.6.0
* whoosh==2.7.4



## Semantic Recognition Method

1. 從良醫網及健康百科收集語料後，使用Word2Vec訓練模型

2. 將不同類型的字詞分為不同domain，並將domain內concept的字詞，與使用者斷詞後的字詞丟入模型內判斷相似度

   ![Imgur](https://i.imgur.com/SW76dNc.png)

3. 根據不同字詞的domain，去資料庫找尋合適的回覆語句



## Get Started

> Run Server

```bash
cd AIBox-Server
python run.py
```


> Run Client

~~~bash
cd AIBox-Client
python client.py
~~~

~~~python
# client.py
import requests
import json

sentence = input('請公威:')
response_info = {'flag': '', 'response': sentence}
message = requests.post("http://127.0.0.1:5000/api/chatbot", json=response_info)
print(message.text)

while True:
    dic = json.loads(message.text)
    flag = dic['flag']
    sentence = input('請公威:')
    response_info = {'flag': flag, 'response': sentence}
    message = requests.post("http://127.0.0.1:5000/api/chatbot", json=response_info)
    print(message.text)
~~~

