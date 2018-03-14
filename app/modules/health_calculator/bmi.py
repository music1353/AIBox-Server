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

