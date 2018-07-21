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

   | API Method | API URL                         | Desc                                       | Req Params    | Resp Result                                                  |
   | ---------- | ------------------------------- | ------------------------------------------ | ------------- | ------------------------------------------------------------ |
   | POST       | URL/androidUser/login           | 手機端的登入                               | user_nickname |                                                              |
   | POST       | URL/androidUser/logout          | 手機端的登出                               |               |                                                              |
   | POST       | URL/androidUser/checkLogin      | 手機端檢查登入狀態                         |               | 正在登入中的user_nickname                                    |
   | GET        | URL/androidUser/getProfile      | 取得用戶的個人資訊                         |               | nickname, gender, age, height, weight, bmi_value(值), bmi(狀況) |
   | GET        | URL/androidUser/getHealth       | 取得用戶的生活習慣(健康狀況)               |               | smoking, excercise, heart_problem, stroke, high_blood, high_cholesterol, diabetes, bmi_value, bmi |
   | GET        | URL/androidUser/getNeed         | 取得用戶需要攝取的水量(c.c.)及卡路里(大卡) |               | needwater, needcarlorie                                      |
   | GET        | URL/androidUser/getConversation | 取得用戶的對話紀錄                         |               | [{question, response, date}, ...] *(無資料則回空list)*       |
   | GET        | URL/androidUser/getRemind       | 取得用戶的提醒資料                         |               | [{remind_time, dosomething}, ...]  *(無資料則回空list)*      |
   | POST       | URL/androidUser/concernLock     | 讓concern模組知道現在是對誰做關心          | user_nickname |                                                              |
   | POST       | URL/androidUser/concernRelease  | 讓concern模組知道現在是對誰解除關心狀態    | user_nickname |                                                              |

   

2. androidAPI

   > 手機端的一般API，提供非登入就可使用功能

   | API Method | API URL                     | Desc                                    | Req Params                         | Resp Result                                                  |
   | ---------- | --------------------------- | --------------------------------------- | ---------------------------------- | ------------------------------------------------------------ |
   | GET        | URL/android/getRemind       | 取得未登入(user_nickname為空)的提醒資料 |                                    | [{remind_time, dosomething}, ...] *(無資料則回空list)*       |
   | GET        | URL/android/getAllLocation  | 取得所有查詢的地點                      |                                    | [{location, region, number, unit, date}, ...] *(無資料則回空list)* |
   | GET        | URL/android/getLastLocation | 取得最後一個(最新)查詢的地點            |                                    | [{location, region, number, unit, date}, ...] *(無資料則回空list)* |
   | GET        | URL/android/getWeather      | 取得某城市的天氣狀況                    | city (e.g. 臺北市、新北市、臺南市) | {Wx, MaxT, MinT, CI, PoP}                                    |

   * 詳細資料格式

     * getWeather

       ~~~
       {
           "status": "200",
           "result": {	
               "Wx": 天氣現象,
               "MaxT": 最高溫度(C),
               "MinT": 最低溫度(C),
               "CI": 舒適度,
               "PoP": 降雨機率（%）
           },
           "msg": ""
       }
       ~~~

       範例 (result 部分)：

       ~~~json
       {
           "msg": "取得某城市的天氣狀況成功",
           "result": {
               "CI": "舒適至易中暑",
               "MaxT": "34",
               "MinT": "27",
               "PoP": "60",
               "Wx": "多雲時陰短暫陣雨或雷雨"
           },
           "status": "200"
       }
       ~~~

       