def cal_pressure(diastolic, systolic):
    '''計算血壓狀況
    Args:
        diastolic: 舒張壓
        systolic: 收縮壓
    Returns:
        正常、高、低
    '''

    if diastolic<60 or systolic<90:
        return '低'
    elif diastolic>89 or systolic>139:
        return '高'
    else:
        return '正常'