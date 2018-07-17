# time_transfer

> 將中文日期轉換成日期格式的 Python 模組



## Get Stated

```python
from time_transfer import chin2time
```



## API

chin2time.**chinweekday2int** (chin_weekday)

- Input：(string) 中文數字
- Output：(int) 數字



chin2time.**last_date_of_this_week** ()

- Output：(datetime.time) 這禮拜天的日期。e.g. 2018-07-15



chin2time.**day_transfer** (day)

- Input：(string) template的day。e.g. 今天、明天、後天
- Ouput：(string) 處理過後的日期



chin2time.**weekday_transfer** (day)

- Input：(string) template的day。e.g. 這禮拜一、下禮拜天、這星期三、這星期六
- Output：(string) 日期, (boolean) 是否有錯誤 e.g. 今天是禮拜六，使用者卻說這禮拜三



chin2time.**date_transfer** (day)

* Input：(string) template的day。e.g. 3月15日、4月5號
* Output：(string) 日期, (boolean) 是否有錯誤 e.g. 這月是否有此月此日、日期是否在今天日期以前



chin2time.**session_transfer** (session)

- Input：(string) template的session。e.g. 上午、早上、下午、晚上
- Output：(int) 0 or (int) 12。表示a.m.及p.m.



chin2time.**time_transfer** (time)

- Input：(string) template的time。e.g. 5點、3點10分、8點45分
- Output：(string) 幾點幾分幾秒。e.g. 3:10:00