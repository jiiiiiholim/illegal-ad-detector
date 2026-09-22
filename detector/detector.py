gambling_keywords = ["카지노", "도박", "토토", "배팅"]
loan_keywords = ["대출", "무직자", "즉시 승인", "당일 대출"]


def detect_ad(text):

    for keyword in gambling_keywords:
        if keyword in text:
            return "도박 광고 의심"

    for keyword in loan_keywords:
        if keyword in text:
            return "불법 금융 광고 의심"

    return "정상"