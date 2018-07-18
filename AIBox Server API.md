# AIBox Server API

> 使用Flask搭建AIBox Server後端，並提供API接口

* URL = https://localhost:5000/api/

* Response Format

  `status`：狀態碼

  `result`：回傳的資料

  `msg`：訊息

* Status Code

  | Status Code | Description |
  | ----------- | ----------- |
  | 200         | 請求成功    |
  | 404         | 請求失敗    |



1. androidUserAPI

   > 手機端的用戶API，主要提供個人化相關的服務

   | API Method | API URL                         | Desc                         | Req Params    | Resp Result                                                  |
   | ---------- | ------------------------------- | ---------------------------- | ------------- | ------------------------------------------------------------ |
   | POST       | URL/androidUser/login           | 手機端的登入                 | user_nickname |                                                              |
   | POST       | URL/androidUser/logout          | 手機端的登出                 |               |                                                              |
   | POST       | URL/androidUser/checkLogin      | 手機端檢查登入狀態           |               | 正在登入中的user_nickname                                    |
   | GET        | URL/androidUser/getProfile      | 取得用戶的個人資訊           |               | nickname, gender, age, height, weight, bmi_value(值), bmi(狀況) |
   | GET        | URL/androidUser/getHealth       | 取得用戶的生活習慣(健康狀況) |               | smoking, excercise, heart_problem, stroke, high_blood, high_cholesterol, diabetes, bmi_value, bmi |
   | GET        | URL/androidUser/getNeedWater    | 取得用戶需要攝取的水量(c.c.) |               | 需要的水量 needwater                                         |
   | GET        | URL/androidUser/getNeedCalorie  | 取得用戶需要攝取的熱量(大卡) |               | 需要的熱量 needcarlorie                                      |
   | GET        | URL/androidUser/getConversation | 取得用戶的對話紀錄           |               | [{question, response, date}, ...] *(無資料則回空list)*       |
   | GET        | URL/androidUser/getRemind       | 取得用戶的提醒資料           |               | [{remind_time, dosomething}, ...]  *(無資料則回空list)*      |

   

2. androidAPI

   > 手機端的一般API，提供非登入就可使用功能

   | API Method | API URL                     | Desc                                    | Req Params                   | Resp Result                                                  |
   | ---------- | --------------------------- | --------------------------------------- | ---------------------------- | ------------------------------------------------------------ |
   | GET        | URL/android/getRemind       | 取得未登入(user_nickname為空)的提醒資料 |                              | [{remind_time, dosomething}, ...] *(無資料則回空list)*       |
   | GET        | URL/android/getAllLocation  | 取得所有查詢的地點                      |                              | [{location, region, number, unit, date}, ...] *(無資料則回空list)* |
   | GET        | URL/android/getLastLocation | 取得最後一個(最新)查詢的地點            |                              | [{location, region, number, unit, date}, ...] *(無資料則回空list)* |
   | GET        | URL/android/getWeather      | 取得某城市的天氣狀況                    | city (e.g. 台北、新竹、台南) | [{desc, temperature, felt_air_temp, humidity, rainfall, specials: [{title,  status, desc, at}] }] |

   * 詳細資料格式

     * getWeather

       ~~~
       {
           "status": "200",
           "result": {	
               "desc": 敘述,
               "temperature": 溫度,
               "felt_air_temp": 體感溫度,
               "humidity": 濕度,
               "rainfall": 雨量,
               "specials"(特別預報): [
                   {
                       "title": 特別預報標題,
                       "status": 特別預報狀態,
                       "desc": 特別預報敘述,
                       "at": 特別預報發布時間
                   }
               ]
           }
           ,
           "msg": ""
       }
       ~~~

       範例 (result 部分)：

       ~~~json
       HTTP/1.1 200 OK
       {
           "desc": "午後短暫雷陣雨",
           "temperature": "27",
           "felt_air_temp": "25",
           "humidity": "92",
           "rainfall": "5.0",
           "specials": [
               {
                   "title": "大雨特報",
                   "status": "大雨",
                   "desc": "西南風增強，易有短時強降雨，今（１１）日臺南市、高雄市及屏東縣有局部大雨或豪雨發生的機率，中部以北地區、宜蘭地區及花蓮山區有局部大雨發生的機率，請注意雷擊及強陣風；連日降雨，亦請注意坍方、落石，民眾應避免進入山區及河川活動。",
                   "at": "2016-07-11 12:05:00"
               }
           ]
       }
       ~~~

       