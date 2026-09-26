import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# detector.py의 탐지 함수 임포트 (파일명/함수명에 맞춰 확인)
try:
    from detector.detector import detect_illegal_ads
except ImportError:
    # detector 함수가 없을 경우를 대비한 덤머 함수
    def detect_illegal_ads(html, url):
        return None

results = []
visited = set()

def crawl(url, base_domain, depth=0, max_depth=2):
    if url in visited or depth > max_depth:
        return
    if urlparse(url).netloc != base_domain:
        return

    visited.add(url)
    print(f"[{depth}] 방문 중: {url}")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            html_content = response.text

            # 1. detector로 불법 광고 탐지
            detected_data = detect_illegal_ads(html_content, url)
            if detected_data:
                results.append(detected_data)

            # 2. 하위 링크 추출 및 재귀 탐색
            soup = BeautifulSoup(html_content, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if not href.startswith("#") and not href.startswith("javascript:"):
                    full_url = urljoin(url, href)
                    crawl(full_url, base_domain, depth + 1, max_depth)

    except Exception as e:
        print(f"접속 에러 ({url}): {e}")


# --- 프론트엔드/백엔드 연동용 함수 ---
def run_scanner(target_url: str):
    global results, visited
    results.clear()
    visited.clear()

    initial_domain = urlparse(target_url).netloc
    crawl(target_url, initial_domain, depth=0, max_depth=2)
    return results


# --- 단독 실행 테스트용 ---
if __name__ == "__main__":
    start_url = "http://127.0.0.1:5500/test_site/index.html"

    print(f"=== {start_url} 스캔 시작 ===")
    final_results = run_scanner(start_url)

    print("\n=== 최종 수집 및 탐지 결과 JSON ===")
    print(json.dumps(final_results, indent=2, ensure_ascii=False))