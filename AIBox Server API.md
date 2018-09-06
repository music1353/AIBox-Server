# AIBox Server API

> 使用Flask搭建AIBox Server後端，並提供API接口

- URL = https://localhost:5000/api/

- Response Format

  `status`：狀態碼

  `result`：回傳的資料

  `msg`：訊息

- Status Code

  | Status Code | Description |
  | ----------- | ----------- |
  | 200         | 請求成功    |
  | 404         | 請求失敗    |



1. androidUserAPI

   > 手機端的用戶API，主要提供個人化相關的服務

   | API Method | API URL                            | Desc                                       | Req Params          | Resp Result                                                  |
   | ---------- | ---------------------------------- | ------------------------------------------ | ------------------- | ------------------------------------------------------------ |
   | POST       | URL/androidUser/login              | 手機端的登入                               | user_nickname       |                                                              |
   | POST       | URL/androidUser/logout             | 手機端的登出                               |                     |                                                              |
   | POST       | URL/androidUser/checkLogin         | 手機端檢查登入狀態                         |                     | 正在登入中的user_nickname                                    |
   | GET        | URL/androidUser/getProfile         | 取得用戶的個人資訊                         |                     | nickname, gender, age, height, weight, bmi_value(值), bmi(狀況) |
   | GET        | URL/androidUser/getHealth          | 取得用戶的生活習慣(健康狀況)               |                     | smoking, excercise, heart_problem, stroke, high_blood, high_cholesterol, diabetes, bmi_value, bmi |
   | GET        | URL/androidUser/getNeed            | 取得用戶需要攝取的水量(c.c.)及卡路里(大卡) |                     | needwater, needcarlorie                                      |
   | GET        | URL/androidUser/getConversation    | 取得用戶的對話紀錄                         |                     | [{question, response, date}, ...] *(無資料則回空list)*       |
   | GET        | URL/androidUser/getRemind          | 取得用戶的提醒資料                         |                     | [{remind_time, dosomething}, ...]  *(無資料則回空list)*      |
   | POST       | URL/androidUser/concernLock        | 讓concern模組知道現在是對誰做關心          | user_nickname       |                                                              |
   | POST       | URL/androidUser/concernRelease     | 讓concern模組知道現在是對誰解除關心狀態    | user_nickname       |                                                              |
   | GET        | URL/androidUser/locationLockStatus | 查看location lock的狀態                    |                     | lock_status *(Boolean. True表示使用者詢問了地點資訊)*        |
   | POST       | URL/androidUser/locationRelease    | 釋放location Lock的狀態                    |                     |                                                              |
   | GET        | URL/androidUser/dailyConcern       | 取得使用者的daily concern資訊              |                     | [{date,  diastolic.  systolic}]                              |
   | POST       | URL/androidUser/setECP             | 設置緊急聯絡人的名字及電話號碼             | ec_person, ec_phone |                                                              |
   | GET        | URL/androidUser/getECP             | 取得使用者的ECP                            |                     |                                                              |
   | POST       | URL/androidUser/deleteECP          | 刪除使用者的緊急聯絡人                     | ec_person           |                                                              |

2. androidAPI

   > 手機端的一般API，提供非登入就可使用功能

   | API Method | API URL                     | Desc                                    | Req Params                         | Resp Result                                                  |
   | ---------- | --------------------------- | --------------------------------------- | ---------------------------------- | ------------------------------------------------------------ |
   | GET        | URL/android/getRemind       | 取得未登入(user_nickname為空)的提醒資料 |                                    | [{remind_time, dosomething}, ...] *(無資料則回空list)*       |
   | GET        | URL/android/getAllLocation  | 取得所有查詢的地點                      |                                    | [{location, region, number, unit, date}, ...] *(無資料則回空list)* |
   | GET        | URL/android/getLastLocation | 取得最後一個(最新)查詢的地點            |                                    | [{location, region, number, unit, date}, ...] *(無資料則回空list)* |
   | GET        | URL/android/getWeather      | 取得某城市的天氣狀況                    | city (e.g. 臺北市、新北市、臺南市) | Wx, MaxT, MinT, CI, PoP, info*(app背景)*                     |
   | GET        | URL/android/getHospital     | 取得醫院的資訊                          | hospital                           | 機構名稱, 拼音機構名稱, 權屬別, 型態別, 縣市鄉鎮, 電話, 地址, 診療科別, 醫院評價, 西醫生, 中醫師, 牙醫師, 藥師, 藥劑生, 護理師, 護士, 助產士, 助產師, 醫事檢驗師, 醫事檢驗生, 物理治療師, 職能治療師, 醫事放射師, 醫事放射士, 物理治療生, 呼吸治療師, 職能治療生, 諮商心理師, 臨床心理師, 營養師, 語言治療師, 牙體技術師, 聽力師, 牙體技術生 |
   | GET        | URL/android/getECPhone      | 取得緊急聯絡人電話                      |                                    | phone                                                        |
   | GET        | URL/android/getActivity     | 取得活動資訊                            |                                    | title, disc, latitude, longitude                             |

   - 詳細資料格式

     - getWeather

       ```
       {
           "status": "200",
           "result": {	
               "Wx": 天氣現象,
               "MaxT": 最高溫度(C),
               "MinT": 最低溫度(C),
               "CI": 舒適度,
               "PoP": 降雨機率（%）,
               "info": 簡單的天氣狀態(rainy, sunny, cloudy)
           },
           "msg": ""
       }
       ```

       範例 (result 部分)：

       ```json
       {
           "msg": "取得某城市的天氣狀況成功",
           "result": {
               "CI": "舒適至易中暑",
               "MaxT": "34",
               "MinT": "27",
               "PoP": "60",
               "Wx": "多雲時陰短暫陣雨或雷雨",
               "info": "rainy"
           },
           "status": "200"
       }
       ```

     - getHospital

       ~~~json
       {
           "msg": "取得醫院資訊成功",
           "result": {
               "中醫師": "1",
               "助產士": "",
               "助產師": "",
               "呼吸治療師": "",
               "地址": "臺東縣台東市開封街449號",
               "型態別": "中醫一般診所",
               "拼音機構名稱": "lao-pi-zhong-yi-zhen-suo",
               "機構名稱": "老皮中醫診所",
               "權屬別": "私立中醫診所",
               "營養師": "",
               "牙醫師": "",
               "牙體技術師": "",
               "牙體技術生": "",
               "物理治療師": "",
               "物理治療生": "",
               "縣市鄉鎮": "臺東縣台東市",
               "職能治療師": "",
               "職能治療生": "",
               "聽力師": "",
               "臨床心理師": "",
               "藥劑生": "",
               "藥師": "",
               "西醫生": "",
               "診療科別": "",
               "語言治療師": "",
               "諮商心理師": "",
               "護士": "",
               "護理師": "",
               "醫事放射士": "",
               "醫事放射師": "",
               "醫事檢驗師": "",
               "醫事檢驗生": "",
               "醫院評價": "0",
               "電話": "0989000628"
           },
           "status": "200"
       }
       ~~~
