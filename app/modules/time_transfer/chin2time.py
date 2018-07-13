from datetime import datetime, date, timedelta

# 取得今天日期
# return 今天日期 e.g. 2018-07-14
def today_date():
    return date.today()


# 傳入template的 day
# return (int)天數
def day_transfer(day):
    if day == '今天':
        return 0
    elif day == '明天':
        return 1
    elif day == '後天':
        return 2
    

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