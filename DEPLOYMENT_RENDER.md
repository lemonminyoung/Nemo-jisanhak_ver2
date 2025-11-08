# Render.com 배포 가이드

## 🚀 빠른 배포 (3분)

### 1단계: Render 계정 생성

https://render.com 에서 무료 계정 생성 (GitHub 연동)

### 2단계: 새 Web Service 생성

1. Render 대시보드에서 **"New +"** 클릭
2. **"Web Service"** 선택
3. GitHub 저장소 연결: `lemonminyoung/Nemo-jisanhak_ver2`

### 3단계: 배포 설정

자동으로 `render.yaml` 파일이 감지됩니다:

```yaml
name: chemical-analyzer-v2
env: docker
region: oregon
plan: free
```

**Environment Variables 설정:**

| Key | Value | 설명 |
|-----|-------|------|
| `GEMINI_API_KEY` | `your-api-key` | Google Gemini API 키 |
| `PORT` | `8000` | 자동 설정됨 |

### 4단계: 배포 시작

**"Create Web Service"** 클릭!

배포 시간: 약 5-10분 (Playwright 설치 포함)

## 🔧 배포 확인

### Health Check

배포 완료 후:

```bash
curl https://chemical-analyzer-v2.onrender.com/health
```

응답:
```json
{
  "status": "healthy",
  "version": "2.0-gemini-compact",
  "ai_provider": "Google Gemini"
}
```

### API 테스트

```bash
curl -X POST https://chemical-analyzer-v2.onrender.com/hybrid-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "substances": ["Bleach", "Ammonia"],
    "use_ai": true
  }'
```

## ⚠️ 중요 사항

### 1. Free Tier 제한

- **Sleep 모드**: 15분 비활성 후 자동 종료
- **첫 요청**: Cold start로 30-60초 소요
- **월간 사용량**: 750시간 무료

### 2. Timeout 설정

Render.com Free Tier는 **HTTP timeout 30초** 제한이 있습니다.

**문제**: CAMEO 크롤링은 2-5분 소요

**해결 방법**:
1. Frontend에서 timeout을 300초 이상으로 설정
2. 또는 **Paid Plan** 사용 ($7/월부터)

### 3. 환경 변수 업데이트

Render 대시보드에서:
1. 서비스 선택
2. **"Environment"** 탭
3. 변수 수정 후 **"Save Changes"**
4. 자동으로 재배포됨

## 📊 모니터링

### 로그 확인

Render 대시보드 → **"Logs"** 탭

```
[V2] Analyzing 2 substances...
[V2] Step 1: CAMEO crawling...
[V2] CAMEO found 1 pairs
[V2] Step 2: Rule-based classification...
[V2] Step 3: Gemini AI analysis...
[Gemini] OK (245 chars)
```

### 메트릭 확인

- **Response Time**: Health check는 <1초
- **API 요청**: 2-5분 (CAMEO 크롤링 포함)
- **메모리 사용량**: ~500MB (Playwright 포함)

## 🔄 재배포

### 자동 배포

`master` 브랜치에 push하면 자동으로 재배포:

```bash
git add .
git commit -m "Update feature"
git push origin master
```

### 수동 배포

Render 대시보드 → **"Manual Deploy"** → **"Deploy latest commit"**

## ❌ 문제 해결

### 1. 배포 실패: "Playwright install failed"

**원인**: Docker 이미지 문제

**해결**: `Dockerfile`에서 Playwright 이미지 버전 확인
```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy
```

### 2. API Timeout

**원인**: Free tier 30초 제한

**해결**:
- Paid Plan으로 업그레이드
- 또는 Frontend에서 긴 timeout 설정 (300초+)

### 3. Gemini API 오류

**원인**: API 키 미설정 또는 잘못됨

**해결**:
1. Render 대시보드 → Environment 확인
2. `GEMINI_API_KEY` 값 재설정
3. https://aistudio.google.com/app/apikey 에서 키 재발급

### 4. CAMEO 크롤링 실패

**원인**: CAMEO 웹사이트 다운 또는 변경

**해결**:
- 로그 확인: `[V2] CAMEO found 0 pairs`
- CAMEO 웹사이트 접속 확인: https://cameochemicals.noaa.gov/

## 💰 비용

### Free Tier
- **월 750시간** 무료
- 15분 후 sleep
- HTTP timeout 30초

### Starter Plan ($7/월)
- Sleep 없음
- HTTP timeout 무제한 ✅
- 더 빠른 빌드

## 🌐 커스텀 도메인

Render 대시보드 → **"Settings"** → **"Custom Domain"**

예시: `api.nemo-jisanhak.com`

## 📝 배포 체크리스트

- [ ] GitHub 저장소 연결
- [ ] `GEMINI_API_KEY` 환경 변수 설정
- [ ] `render.yaml` 파일 확인
- [ ] Health check 성공 확인
- [ ] API 테스트 성공
- [ ] Frontend에서 timeout 설정 (300초+)
- [ ] 로그 모니터링 설정

## 🔗 유용한 링크

- [Render 대시보드](https://dashboard.render.com/)
- [Render 문서](https://render.com/docs)
- [Gemini API 키 발급](https://aistudio.google.com/app/apikey)
- [CAMEO 웹사이트](https://cameochemicals.noaa.gov/)

---

**배포 성공 후 API URL**: `https://chemical-analyzer-v2.onrender.com`
