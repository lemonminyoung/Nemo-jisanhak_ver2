# 화학물질 안전성 분석 API - Version 2

> Gemini API만 사용하는 간소화된 버전 (Nemo 지산학 프로젝트)

## 🎯 주요 특징

- **CAMEO 데이터베이스 실시간 크롤링**: NOAA CAMEO에서 최신 화학 반응성 데이터 수집
- **규칙 기반 안전성 분석**: 100% 정확한 위험도 분류 (위험/주의/안전)
- **Gemini AI 요약**: 사용자 친화적인 한국어 안전 메시지 생성
- **한국어 지원**: 화학물질명 자동 번역 및 안전 링크 제공
- **Nemo 포맷 호환**: 백엔드 연동을 위한 표준화된 응답 구조

## 🚀 Version 2 개선사항

| 항목 | Version 1 | Version 2 |
|------|-----------|-----------|
| AI 모델 | HuggingFace + Gemini | Gemini만 |
| 외부 의존성 | Colab/HF Spaces 필요 | 없음 |
| 응답 속도 | 3-7분 | 2-5분 |
| 토큰 사용량 | 많음 | 60% 절감 |
| 유지보수 | 복잡 | 간단 |

## 📋 요구사항

- Python 3.11.9+
- Google Gemini API Key (무료)
- Playwright

## ⚙️ 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/lemonminyoung/Nemo-jisanhak_ver2.git
cd Nemo-jisanhak_ver2
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. 환경 변수 설정

`.env` 파일 생성:

```bash
GEMINI_API_KEY=your-api-key-here
```

### 4. 서버 실행

```bash
python backend_gemini_only.py
```

## 📡 API 사용법

### 화학물질 분석

```bash
POST /hybrid-analyze
Content-Type: application/json

{
  "substances": ["Bleach", "Ammonia"],
  "use_ai": true
}
```

### 응답 형식

```json
{
  "success": true,
  "simple_response": {
    "risk_level": "위험",
    "message": "2가지 위험한 조합이 발견되었어요..."
  },
  "safety_links": {
    "msds_links": [...],
    "general_resources": [...]
  }
}
```

## 🧪 테스트

```bash
python test_v2_gemini.py
```

## 📁 주요 파일

- `backend_gemini_only.py` - 메인 API 서버
- `chemical_analyzer.py` - CAMEO 크롤러
- `simple_analyzer.py` - 규칙 기반 분석
- `safety_links.py` - 안전 링크 생성 (한국어 번역)
- `requirements.txt` - Python 의존성

## 🌐 배포

Railway, Render, Docker 지원

---

**Version 2.0** - Gemini Only Edition
