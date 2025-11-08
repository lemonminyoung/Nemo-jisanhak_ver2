# UptimeRobot 설정 가이드

Render.com Free Tier의 Sleep 모드를 방지하기 위해 UptimeRobot으로 주기적으로 Health Check 요청을 보냅니다.

## 🎯 목적

- Render.com Free Tier는 **15분 비활성 시 자동 Sleep**
- UptimeRobot이 **5분마다 핑**을 보내서 서버를 깨워둠
- **완전 무료** (50개 모니터까지)

## 📝 설정 단계

### 1단계: UptimeRobot 계정 생성

1. https://uptimerobot.com/ 접속
2. **"Free Sign Up"** 클릭
3. 이메일 인증 완료

### 2단계: 새 모니터 생성

1. 대시보드에서 **"+ Add New Monitor"** 클릭
2. 다음 정보 입력:

**Monitor Type:**
```
HTTP(s)
```

**Friendly Name:**
```
Chemical Analyzer V2 - Health Check
```

**URL (or IP):**
```
https://chemical-analyzer-v2.onrender.com/health
```

**Monitoring Interval:**
```
5 minutes (무료 플랜 최소값)
```

**Monitor Timeout:**
```
30 seconds
```

**HTTP Method:**
```
HEAD (더 빠름) 또는 GET
```

### 3단계: Alert 설정 (선택사항)

**Alert Contacts:**
- 이메일 추가 (서버 다운 시 알림)

**Alert When:**
- ✅ Monitor goes down
- ✅ Monitor goes up

### 4단계: 저장

**"Create Monitor"** 클릭!

## ✅ 확인

### 대시보드에서 확인

- **Status**: Up (녹색)
- **Uptime**: 99.9%+
- **Response Time**: 100-500ms

### 로그 확인

UptimeRobot → **"Logs"** 탭:
```
2025-01-08 10:00 - Up (200 OK) - 245ms
2025-01-08 10:05 - Up (200 OK) - 198ms
2025-01-08 10:10 - Up (200 OK) - 234ms
```

## 🔧 백엔드 설정 (이미 완료됨)

`backend_gemini_only.py`에 HEAD 메서드 지원이 이미 추가되어 있습니다:

```python
@app.head("/health")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0-gemini-compact",
        "ai_provider": "Google Gemini"
    }
```

HEAD 메서드는:
- ✅ 응답 본문 없이 헤더만 반환 (더 빠름)
- ✅ 대역폭 절약
- ✅ UptimeRobot에 최적화

## 📊 예상 효과

### Sleep 방지
- **이전**: 15분 후 Sleep → 첫 요청 시 30-60초 대기
- **현재**: 항상 깨어있음 → 즉시 응답 ✅

### 트래픽 사용량
- **요청 빈도**: 5분마다 = 하루 288회
- **요청 크기**: HEAD 메서드 = ~500 bytes
- **월간 트래픽**: ~4MB (무시할 수준)

## ⚠️ 주의사항

### 1. URL 확인
Render 배포 완료 후 실제 URL로 변경:
```
https://your-actual-render-url.onrender.com/health
```

### 2. Monitoring Interval
- **5분**: Sleep 방지 (권장) ✅
- **1분**: 과도한 요청 (불필요)
- **10분+**: Sleep 가능성 있음 ❌

### 3. 무료 플랜 제한
- **모니터 개수**: 50개까지
- **Interval**: 5분 최소
- **Alert**: 무제한

## 🎁 추가 기능

### 1. Status Page (선택)

UptimeRobot에서 공개 상태 페이지 생성 가능:
```
https://stats.uptimerobot.com/your-page
```

사용자가 API 상태를 실시간으로 확인 가능!

### 2. 여러 엔드포인트 모니터링

추가 모니터 생성 가능:
- `/health` - 서버 상태
- `/` - 루트 엔드포인트

### 3. Slack/Discord 알림

UptimeRobot → Alert Contacts → Webhook 추가

## 🔍 문제 해결

### "Monitor is Down"

**원인:**
1. Render 서버가 실제로 다운됨
2. 배포 중
3. Cold start (첫 배포 시)

**해결:**
1. Render 대시보드 로그 확인
2. 직접 브라우저에서 URL 접속 테스트
3. 5-10분 대기 후 자동 복구 확인

### "Response Time Too High"

**원인:** Cold start (Sleep에서 깨어남)

**정상 범위:**
- 정상: 100-500ms
- Cold start: 5-30초 (첫 요청만)

**해결:** 5분 간격이면 대부분 방지됨

## 📈 최적 설정 요약

| 설정 | 값 | 이유 |
|------|-----|------|
| Monitor Type | HTTP(s) | 표준 |
| HTTP Method | HEAD | 더 빠르고 효율적 |
| Interval | 5분 | Sleep 방지 + 무료 |
| Timeout | 30초 | Cold start 대응 |
| Alert | 이메일 | 다운 시 알림 |

## ✅ 체크리스트

- [ ] UptimeRobot 계정 생성
- [ ] Render 배포 완료 후 URL 확인
- [ ] 모니터 생성 (5분 간격)
- [ ] HTTP Method를 HEAD로 설정
- [ ] Alert 이메일 설정
- [ ] 대시보드에서 "Up" 상태 확인
- [ ] 15분 후에도 빠른 응답 확인

## 🔗 유용한 링크

- [UptimeRobot 대시보드](https://uptimerobot.com/dashboard)
- [UptimeRobot 문서](https://uptimerobot.com/api/)
- [Render 대시보드](https://dashboard.render.com/)

---

**설정 완료 후**: 서버가 항상 깨어있어 즉시 응답! ⚡
