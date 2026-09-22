import requests
from bs4 import BeautifulSoup
import sys
import os

# detector 폴더를 불러올 수 있도록 경로 추가
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from detector.detector import detect_ad


url = "http://127.0.0.1:5500/test_site/index.html"

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

comments = soup.find_all(class_="comment")


print("=== 불법 광고 탐지 결과 ===")

for comment in comments:

    text = comment.get_text(strip=True)

    result = detect_ad(text)

    print()
    print("내용:", text)
    print("판정:", result)