def cal_water(kg):
    '''計算一天要喝多少cc的水
    Args:
        kg: 體重
    Returns:
        需要多少cc水量
    '''

    return str(int(kg)*30)

def cal_BMR(gender, kg, cm, age):
    '''計算一天的基礎代謝率, 也就是需要多少大卡熱量
    Args:
        gender: 性別
        kg: 體重
        cm: 身高
        age: 年齡
    Returns:
        一天需要多少大卡熱量
    '''

    if gender == 'man':
        return str(int(66+(13.7*int(kg))+(5*int(cm))-(6.8*int(age))))
    else:
        return str(int(655+(9.6*int(kg))+(1.7*int(cm))-(4.7*int(age))))