"""
Chemical Safety Analyzer API - Version 2 (Gemini Only)
화학물질 안전성 분석 API - 간결한 프롬프트 + Nemo-jisanhak 포맷
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from chemical_analyzer import crawl_cameo_sequential
from simple_analyzer import analyze_simple
from safety_links import get_all_links_for_analysis
from dotenv import load_dotenv
import google.generativeai as genai
import sys
from io import StringIO
import json

# .env 파일 로드
load_dotenv()

app = FastAPI(title="Chemical Reactivity Analysis API - Gemini Version")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API Key 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("[OK] Gemini API configured")
else:
    print("[ERROR] Gemini API key not set. Please set GEMINI_API_KEY in .env file")
    sys.exit(1)


# Helper function to suppress Playwright output
async def crawl_with_suppressed_output(substances: List[str]) -> list:
    """Wrapper to suppress stdout/stderr during Playwright crawling"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        results = await crawl_cameo_sequential(substances)
        return results
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


# Request/Response 모델
class Product(BaseModel):
    productName: str
    casNumbers: List[str]


class AnalysisRequest(BaseModel):
    useAi: bool = True
    products: List[Product]


class SimpleResponse(BaseModel):
    risk_level: str
    message: str


class HybridAnalysisResponse(BaseModel):
    success: bool
    simple_response: SimpleResponse
    safety_links: Optional[dict] = None
    error: Optional[str] = None


# API 엔드포인트
@app.head("/health")
@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "version": "2.0-gemini-compact",
        "ai_provider": "Google Gemini"
    }


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "Chemical Reactivity Analysis API",
        "version": "2.0 (Compact)",
        "status": "running"
    }


@app.post("/hybrid-analyze", response_model=HybridAnalysisResponse)
async def hybrid_analyze_endpoint(request: AnalysisRequest):
    """
    하이브리드 분석 (규칙 기반 + Gemini AI 요약)

    Nemo v1 호환 포맷 (products + casNumbers)
    """
    try:
        # products에서 화학물질명 추출
        substances = []
        for product in request.products:
            # CAS Number가 있으면 첫 번째 CAS로 검색
            if product.casNumbers and len(product.casNumbers) > 0:
                substances.append(product.casNumbers[0])
            # CAS가 없으면 제품명으로 검색
            elif product.productName:
                substances.append(product.productName)

        if len(substances) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 products are required"
            )

        print(f"[V2] Analyzing {len(substances)} products...")
        print(f"[V2] Substances: {substances}")

        # 1. CAMEO 크롤링
        print("[V2] Step 1: CAMEO crawling...")
        cameo_results = await crawl_with_suppressed_output(substances)

        if not cameo_results:
            raise HTTPException(
                status_code=404,
                detail="No reactivity data found from CAMEO"
            )

        print(f"[V2] CAMEO found {len(cameo_results)} pairs")

        # 2. 규칙 기반 분석
        print("[V2] Step 2: Rule-based classification...")
        analysis_result = analyze_simple(cameo_results)
        print(f"[V2] Classification: {analysis_result['summary']['overall_status']}")

        # 3. Gemini AI 요약 (간결한 프롬프트)
        ai_message = None

        if request.useAi:
            print("[V2] Step 3: Gemini AI analysis...")
            gemini_response = analyze_with_gemini_compact(analysis_result)

            if gemini_response.get("success"):
                ai_message = gemini_response.get("message", "")
                print("[V2] Gemini analysis complete")
            else:
                print(f"[V2] Gemini failed: {gemini_response.get('error')}")
                ai_message = analysis_result['summary']['message']
        else:
            ai_message = analysis_result['summary']['message']

        # 4. 안전 링크 생성
        safety_links = get_all_links_for_analysis(
            analysis_result['dangerous_pairs'],
            analysis_result['caution_pairs']
        )

        # Nemo-jisanhak 포맷으로 응답
        return HybridAnalysisResponse(
            success=True,
            simple_response=SimpleResponse(
                risk_level=analysis_result['summary']['overall_status'],
                message=ai_message
            ),
            safety_links=safety_links
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[V2] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def analyze_with_gemini_compact(analysis_result: dict, retries: int = 2) -> dict:
    """
    Gemini API로 화학 안전성 분석 결과를 간결하게 요약
    토큰 절약을 위한 최소 프롬프트
    """
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "error": "Gemini API key not configured"
        }

    summary = analysis_result.get("summary", {})
    overall_status = summary.get("overall_status", "알 수 없음")
    dangerous_count = summary.get("dangerous_count", 0)
    caution_count = summary.get("caution_count", 0)
    dangerous_pairs = analysis_result.get("dangerous_pairs", [])
    caution_pairs = analysis_result.get("caution_pairs", [])

    for attempt in range(1, retries + 1):
        try:
            print(f"[Gemini] Attempt {attempt}/{retries}")

            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            # 위험 정보만 간단히
            danger_info = []
            for pair in dangerous_pairs[:3]:
                danger_info.append({
                    "물질1": pair.get("chemical_1", ""),
                    "물질2": pair.get("chemical_2", ""),
                    "위험": pair.get("hazards", [])[:2]  # 상위 2개만
                })

            caution_info = []
            for pair in caution_pairs[:2]:
                caution_info.append({
                    "물질1": pair.get("chemical_1", ""),
                    "물질2": pair.get("chemical_2", ""),
                    "위험": pair.get("hazards", [])[:1]  # 상위 1개만
                })

            # 친근한 프롬프트 (사용자 UI용 - 이모지 절대 금지)
            prompt = f"""상태: {overall_status}
위험: {dangerous_count}개, 주의: {caution_count}개

위험 조합: {json.dumps(danger_info, ensure_ascii=False)}
주의 조합: {json.dumps(caution_info, ensure_ascii=False)}

IMPORTANT: 절대 이모지를 사용하지 마세요. 순수 텍스트만 사용하세요.

자연스럽고 친근한 한국어로 3-5줄 요약:

위험: "{dangerous_count}가지 위험한 조합이 발견되었어요.\\n\\n[각 조합의 위험성을 쉽게 설명]\\n\\n이 제품들을 함께 사용하면 위험할 수 있으니 주의해주세요."

주의: "{caution_count}가지 주의가 필요한 조합이 있어요.\\n\\n[주의사항 설명]\\n\\n사용 시 주의가 필요해요."

안전: "분석 결과 이 제품들은 함께 사용해도 안전해요!"

답변 (텍스트만):"""

            # Gemini 호출
            response = model.generate_content(prompt)

            # 응답 파싱
            message = None

            if hasattr(response, "text") and response.text:
                message = response.text.strip()
            elif hasattr(response, "candidates") and response.candidates:
                first_candidate = response.candidates[0]
                if hasattr(first_candidate, "content") and first_candidate.content.parts:
                    parts = first_candidate.content.parts
                    message = "\n".join(
                        p.text.strip() for p in parts if hasattr(p, "text")
                    ).strip()

            if not message and str(response):
                message = str(response).strip()

            # 검증
            if message and len(message) > 10:
                print(f"[Gemini] OK ({len(message)} chars)")
                return {
                    "success": True,
                    "message": message
                }
            else:
                print(f"[Gemini] Empty response")
                if attempt < retries:
                    continue
                else:
                    return {
                        "success": False,
                        "error": "Empty response"
                    }

        except Exception as e:
            print(f"[Gemini] Error: {e}")
            if attempt < retries:
                continue
            else:
                return {
                    "success": False,
                    "error": str(e)
                }


# 개발 서버 실행
if __name__ == "__main__":
    import uvicorn

    print("="*70)
    print("Chemical Safety Analyzer - Version 2 (Compact + Nemo Format)")
    print("="*70)

    if GEMINI_API_KEY:
        print("[OK] Gemini API configured")
    else:
        print("[ERROR] Gemini API key not set!")
        sys.exit(1)

    print("\nStarting server on http://0.0.0.0:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("="*70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
