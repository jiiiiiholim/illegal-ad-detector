import asyncio
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright

# 이미 방문한 URL을 기록하여 중복 방문을 방지합니다.
visited = set()
# 팀장이 요구한 최종 수집 결과 저장용 리스트
results = []

async def extract_page_data(page, current_url):
    """
    현재 페이지의 일반 텍스트, 숨겨진 CSS 요소, iframe 내부 텍스트를 수집합니다.
    """
    # 1. 눈에 보이는 일반 텍스트 및 숨겨진 텍스트(display:none 등) 수집
    elements = await page.query_selector_all("p, span, div, article, a, .comment")
    
    for idx, el in enumerate(elements):
        try:
            # text_content()는 CSS로 숨겨진 텍스트(display:none)까지 가져옵니다.
            text = (await el.text_content()).strip()
            if text and len(text) > 2:
                tag_name = await el.evaluate("el => el.tagName.toLowerCase()")
                is_visible = await el.is_visible()
                
                # 위치(location) 정보 구성
                visibility_tag = "visible" if is_visible else "hidden_css"
                location_info = f"DOM[{visibility_tag}] > {tag_name}:nth-of-type({idx+1})"
                
                # 팀장 지정 표준 JSON 규격에 맞추어 저장
                results.append({
                    "url": current_url,
                    "location": location_info,
                    "text": text,
                    "category": "",
                    "risk_score": 0,
                    "evidence": []
                })
        except Exception:
            continue

    # 2. iframe 내부 텍스트 침투 수집
    frames = page.frames
    for f_idx, frame in enumerate(frames):
        if frame == page.main_frame:
            continue  # 메인 프레임은 이미 수집했으므로 패스
        
        try:
            frame_elements = await frame.query_selector_all("p, span, div, a")
            for idx, f_el in enumerate(frame_elements):
                f_text = (await f_el.text_content()).strip()
                if f_text and len(f_text) > 2:
                    results.append({
                        "url": current_url,
                        "location": f"iframe[{f_idx}] > element[{idx}]",
                        "text": f_text,
                        "category": "",
                        "risk_score": 0,
                        "evidence": []
                    })
        except Exception:
            continue


async def crawl(page, url, base_domain, depth=0, max_depth=1):
    """
    재귀적으로 페이지를 방문하며 하위 링크를 추적하는 동적 크롤러 함수입니다.
    """
    # [안전장치] 중복 방문 방지 및 최대 탐색 깊이 제한
    if url in visited or depth > max_depth:
        return
    
    # [안전장치] 외부 타 사이트로 빠져나가지 않도록 같은 도메인만 탐색
    if urlparse(url).netloc != base_domain:
        return

    visited.add(url)
    print(f"[{depth}단계 탐색 중] {url}")

    try:
        # 동적 자바스크립트 렌더링이 완료될 때까지 대기
        await page.goto(url, wait_until="networkidle", timeout=10000)
        
        # 현재 페이지 데이터 수집 실행
        await extract_page_data(page, url)

        # 페이지 내부의 모든 하위 링크(<a> 태그) 수집
        link_elements = await page.query_selector_all("a")
        hrefs = []
        for l in link_elements:
            href = await l.get_attribute("href")
            if href and not href.startswith("#") and not href.startswith("javascript:"):
                full_url = urljoin(url, href)
                hrefs.append(full_url)

        # 발견한 하위 링크들로 재귀 탐색 진행
        for next_url in hrefs:
            await crawl(page, next_url, base_domain, depth + 1, max_depth)

    except Exception as e:
        print(f"[ERROR] 접속 실패 ({url}): {e}")


async def main():
    start_url = "http://127.0.0.1:5500/test_site/index.html"
    initial_domain = urlparse(start_url).netloc

    async with async_playwright() as p:
        # headless=True는 브라우저 창을 띄우지 않고 백그라운드에서 실행합니다.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("=== 동적 불법광고 탐지 크롤러 시작 ===")
        await crawl(page, start_url, base_domain=initial_domain, max_depth=1)
        await browser.close()

    import json
    print(f"\n=== 총 수집된 데이터 개수: {len(results)}개 ===")
    print(json.dumps(results[:3], indent=2, ensure_ascii=False))  # 샘플로 상위 3개 출력


if __name__ == "__main__":
    asyncio.run(main())