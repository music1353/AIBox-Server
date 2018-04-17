def cal(gender, kg, cm):
    if kg==0 and cm==0:
        return 'null'
    
    if cm==0:
        if gender=='man':
            cm = float(173)
        elif gender=='woman':
            cm = float(160)
    
    if kg==0:
        if gender=='man':
            kg = 67.9
        elif gender=='woman':
            kg = 55.6
    
    kg = float(kg)
    cm = float(cm)
    
    m = cm/100
    bmi = kg/(m*m)
    
    return round(bmi, 2)

def result(bmi):
    if bmi < 18.5:
        return "過輕"
    elif 18.5 <= bmi and bmi < 24:
        return "正常"
    elif bmi >= 24:
        return "過重"
