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


# 일단 탐지기가 잘 작동하는지 테스트
test_texts = [
    "좋은 정보 감사합니다!",
    "카지노 신규가입 5만원 지급!",
    "무직자도 당일 대출 가능합니다."
]

for text in test_texts:
    result = detect_ad(text)

    print(text)
    print("판정:", result)
    print()