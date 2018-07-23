# AIBox-Server

> 基於Python Flask所搭建的智慧音箱Server

[![Flask](https://img.shields.io/badge/Flask-0.12.2-blue.svg)](http://flask.pocoo.org/) [![gensim](https://img.shields.io/badge/gensim-3.1.0-blue.svg)](https://radimrehurek.com/gensim/models/word2vec.html) [![gensim](https://img.shields.io/badge/pymongo-3.6.0-blue.svg)](https://api.mongodb.com/python/current/) 



## Requirements

* jieba==0.39
* Flask==0.12.2
* gensim==3.1.0
* pymongo==3.6.0
* whoosh==2.7.4



## Semantic Recognition Method

1. 從良醫網及健康百科收集語料 (約有16500篇文章)，使用 Word2Vec 訓練模型

2. 將不同類型的字詞分為不同 domain，並將 domain 內 concept 的字詞，與使用者斷詞後的字詞丟入模型內判斷相似度。

   ![Imgur](https://i.imgur.com/SW76dNc.png)

   

   若字詞沒有在模型內，會產生 KeyError，則會進到我們額外定義好的 domain (直接比對字詞)

   ![Imgur](https://i.imgur.com/4lPjWoM.png)

3. 根據不同字詞的domain，去資料庫找尋合適的回覆語句



## Recognition Domain

目前有定義 8 種 domain

1. chronic：慢性病
2. cold：感冒
3. custom：個人化
4. city：城市
5. steet：街道
6. location：地點
7. distance：距離
8. yesno：是非



## Get Started

> Run Server

```bash
cd AIBox-Server
python run.py
```


> Run Client

~~~python
# client.py
import requests
import json

while True:
    dic = json.loads(message.text)
    flag = dic['flag']
    sentence = input('請公威:')
    response_info = {'flag': flag, 'response': sentence}
    message = requests.post("http://127.0.0.1:5000/api/chatbot", json=response_info)
    print(message.text)
~~~

~~~bash
cd AIBox-Client
python client.py
~~~

