import sys
import os
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 탐지 모듈 임포트
sys.path.append("..")  # 경로 맞춤
from detector.detector import detect_ad

visited = set()
results = []  # 팀장 양식 결과를 담을 리스트

def crawl(url, base_domain, depth=0, max_depth=2):
    # 1. 중복 방문 및 최대 깊이 제한
    if url in visited or depth > max_depth:
        return
    
    # 2. 같은 도메인만 탐색
    if urlparse(url).netloc != base_domain:
        return

    visited.add(url)
    print(f"[{depth}] 방문 중: {url}")

    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # 3. 댓글 및 텍스트 수집 (팀장 요청 JSON 형태 구성)
        comments = soup.find_all(class_="comment")
        for idx, comment in enumerate(comments):
            text = comment.get_text(strip=True)
            if text:
                # 탐지 함수 실행
                detection_res = detect_ad(text)
                
                # 팀장이 원했던 데이터 구조
                results.append({
                    "url": url,
                    "location": f"comment_section_idx_{idx}",
                    "text": text,
                    "category": detection_res.get("category", ""),
                    "risk_score": detection_res.get("risk_score", 0),
                    "evidence": detection_res.get("evidence", [])
                })

        # 4. 하위 링크 탐색 및 재귀 호출
        links = soup.find_all("a")
        for link in links:
            href = link.get("href")
            if href and not href.startswith("#") and not href.startswith("javascript:"):
                full_url = urljoin(url, href)
                crawl(full_url, base_domain, depth + 1, max_depth)

    except Exception as e:
        print(f"접속 에러 ({url}): {e}")

if __name__ == "__main__":
    start_url = "https://www.naver.com"
    initial_domain = urlparse(start_url).netloc
    
    crawl(start_url, base_domain=initial_domain, max_depth=2)
    
    # 수집 및 탐지 결과 확인
    import json
    print("\n=== 최종 수집 및 탐지 결과 JSON ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))