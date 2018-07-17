from datetime import datetime, date, timedelta

def chinweekday2int(chin_weekday):
    '''中文數字轉阿拉伯數字
    Args:
        (string)chin_weekday: 中文數字
    Returns:
        (int)阿拉伯數字
    '''
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

def last_date_of_this_week():
    '''這禮拜天的日期
    Returns:
        (datetime.date)這禮拜天的日期
    '''
    today = date.today()
    last_date = today
    
    count_day = 0
    while(last_date.weekday() != 6):
        last_date = last_date + timedelta(days=1)
        count_day = count_day + 1
        
    return last_date

def day_transfer(day):
    '''今天、明天等字詞轉為日期
    Args:
        (string)template的day
    Rrturns:
        (string)日期
    '''
    today = date.today()
    
    if day == '今天':
        add_day = 0
        result_day = today + timedelta(days=add_day)
        return str(result_day)
    elif day == '明天':
        add_day = 1
        result_day = today + timedelta(days=add_day)
        return str(result_day)
    elif day == '後天':
        add_day = 2
        result_day = today + timedelta(days=add_day)
        return str(result_day)

def weekday_transfer(day):
    '''這禮拜、下禮拜等字詞轉日期
    Args:
        (string)template的day
    Returns:
        (string)日期
        (boolean)error: 若篩選完後還有字詞或是少了禮拜"幾", 則會error=True
    '''
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
    # FIXME
    if day == '':
        print('weekday_transfer error:', day)
        error = True
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

def date_transfer(day):
    '''中文幾月幾日轉日期格式的日期
    Args:
        (string)template的day
    Returns:
        (string)日期
        (boolean)error: 如果沒有此月此日或是日期在今天之前, error==false
    '''
    
    error = False
    
    # 處理成[月, 日]格式
    split_list = day.split('月')
    date_list = []
    for item in split_list:
        item = item.replace('月', '')
        item = item.replace('日', '')
        item = item.replace('號', '')
        date_list.append(item)

    # 檢查是否少了日或月
    if len(date_list)<2 or date_list[1]=='':
        error = True
        return None, error
        
    today = datetime.today()
    year = date.today().year
    month = date_list[0]
    day = date_list[1]
    date_str = str(year)+'/'+str(month)+'/'+str(day)

    # 檢查這月是否有此月此日
    try:
        remind_date = datetime.strptime(date_str, '%Y/%m/%d')
        
        # 檢查日期是否在今天日期以前
        if remind_date > today:
            return str(remind_date.date()), error
        else:
            print('date_transfer error')
            error = True
            return None, error
    except Exception as err:
        error = True
        return None, error

def session_transfer(session):
    '''上午、下午等字詞轉進位時間
    Args:
        (string)template的session
    Returns:
        (int)0 or 12
    '''
    if session=='上午' or session=='早上':
        return 0
    elif session=='下午' or session=='晚上':
        return 12
    
def time_transfer(session, time):
    '''幾點幾分轉時間
    Args:
        (string)template的time
    Returns:
        (string)時間格式的 時:分:秒
    '''
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