from datetime import datetime, date, timedelta

# 傳入中文數字
# return (int)數字
def chinweekday2int(chin_weekday):
    if chin_weekday == '一':
        return 1
    elif chin_weekday == '二':
        return 2
    elif chin_weekday == '三':
        return 3
    elif chin_weekday == '四':
        return 4
    elif chin_weekday == '五':
        return 5
    elif chin_weekday == '六':
        return 6
    elif chin_weekday=='日' or chin_weekday=='天':
        return 7

    
# return (datetime.date) 現在時間，這禮拜天的日期
def last_date_of_this_week():
    today = date.today()
    last_date = today
    
    count_day = 0
    while(last_date.weekday()!=6):
        last_date = today + timedelta(days=1)
        count_day = count_day + 1
        
    return last_date


# 傳入template的 day
# return (string) 日期
def day_transfer(day):
    today = date.today()
    
    if day == '今天':
        add_day = 0
        result_day = today + datetime.timedelta(days=add_day)
        return str(result_day)
    elif day == '明天':
        add_day = 1
        result_day = today + datetime.timedelta(days=add_day)
        return str(result_day)
    elif day == '後天':
        add_day = 2
        result_day = today + datetime.timedelta(days=add_day)
        return str(result_day)

    
# 傳入template的 day
# return (string)日期, (boolean) error
def weekday_transfer(day):
    error = False # 判斷是否有錯誤
    
    # 計算有幾個'下'
    count_next = 0
    for letter in day:
        if letter == '下':
            count_next = count_next + 1
            
    # 把不必要的字清掉，會剩禮拜“幾”的數字
    day = day.replace('下', '')
    day = day.replace('這', '')
    day = day.replace('禮拜', '')
    day = day.replace('星期', '')
    
    # 如果沒有講禮拜"幾"
    if day=='' or '今' in day or '明' in day or '後' in day:
        print('chin2time error:', day)
        error = True

        # 今天、明天、後天的情況
        if day != '':
            return day, error
        # 沒收到禮拜幾的情況
        else:
            return None, error
    else:
        target_weekday = chinweekday2int(day) - 1 # 目標的禮拜幾

        # 這禮拜
        if count_next == 0:
            this_weekday = date.today()
            today_weekday = date.today().weekday()
            
            # 判斷是否是在今天weekday之後的weekday
            if(target_weekday >= today_weekday):
                while(this_weekday.weekday() != target_weekday):
                    this_weekday = this_weekday + timedelta(days=1)
                return this_weekday, error
            else:
                print('這禮拜', target_weekday+1, '已經過了')
                error = True
                return None, error


        # 下禮拜
        elif count_next == 1:
            last_weekday = last_date_of_this_week()
            next_weekday = last_weekday + timedelta(days=1) # 下週的禮拜一
            while(next_weekday.weekday() != target_weekday):
                next_weekday = next_weekday + timedelta(days=1)
            return next_weekday, error
    

# 傳入template的 session
# return (int) 0(am) or 12(pm)
def session_transfer(session):
    if session=='上午' or session=='早上':
        return 0
    elif session=='下午' or session=='晚上':
        return 12
    
    
# 傳入template的 time
# return (str)幾點幾分幾秒
def time_transfer(session, time):
    split_list = []
    hour = ''
    minute = ''
    second = ''
    
    _str = ''
    for item in time:
        if item!='點' and item!='分':
            _str = _str + item
        else:
            split_list.append(_str)
            _str = ''
    
    list_len = len(split_list)
    # 只有幾點
    if list_len == 1:
        hour = int(split_list[0]) + int(session_transfer(session))
        minute = '00'
        second = '00'
    # 幾點幾分
    elif list_len == 2:
        hour = int(split_list[0]) + int(session_transfer(session))
        minute = split_list[1]
        second = '00'
    
    time_result = str(hour) + ':' + minute + ':'+ second
    
    return time_result