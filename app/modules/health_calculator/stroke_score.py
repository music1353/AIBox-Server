# high_cholesterol: 高膽固醇
# diabetes: 糖尿病
# stroke: 中風

def result(chronic_score, exercise, bmi_result):
    score = chronic_score

    if exercise < 3:
        score += 1
    if bmi_result == "過重":
        score += 1

    if score >= 3:
        return "高風險群"
    elif 1 < score and score < 3:
        return "注意"
    elif score <= 1:
        return "低風險群"