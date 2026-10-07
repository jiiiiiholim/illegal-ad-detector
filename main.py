from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crawler.playwright_crawler import run_scanner

# 1. FastAPI 앱 생성 (uvicorn이 찾는 'app' 변수)
app = FastAPI(title="공공 웹사이트 불법광고 탐지 API")

# 2. CORS 허용 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "Illegal Ad Detector API Server is Running!"}

@app.post("/api/scan")
def scan_website(request: ScanRequest):
    results = run_scanner(request.url)
    return {
        "status": "success",
        "target_url": request.url,
        "count": len(results),
        "results": results
    }