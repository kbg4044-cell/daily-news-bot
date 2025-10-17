# 🚀 Daily News Bot 배포 가이드

## 📦 배포 파일 목록

### **GitHub Repository에 업로드할 파일들**

```
your-news-bot/
├── daily_news_bot.py              # ✅ 메인 실행 파일
├── naver_news_collector.py        # ✅ 뉴스 수집 시스템  
├── gemini_news_editor.py          # ✅ AI 편집 시스템
├── kakao_business_sender.py       # ✅ 카카오톡 발송 시스템
├── requirements.txt               # ✅ Python 라이브러리 목록
├── README.md                      # ✅ 사용 설명서
└── .github/workflows/
    └── daily-news-bot.yml         # ✅ GitHub Actions 설정파일 (이름 변경 필요!)
```

## 🔧 단계별 배포 방법

### **1단계: GitHub Repository 생성**
1. GitHub 계정 로그인
2. **New Repository** 클릭
3. Repository 이름: `daily-news-bot` (또는 원하는 이름)
4. **Public**으로 설정 (GitHub Actions 무료 사용)
5. **Create Repository** 클릭

### **2단계: 파일 업로드**

#### **방법 A: 웹에서 직접 업로드**
1. **Add file** → **Upload files** 클릭
2. 아래 파일들을 드래그 앤 드롭:
   - `daily_news_bot.py`
   - `naver_news_collector.py`
   - `gemini_news_editor.py`
   - `kakao_business_sender.py`
   - `requirements.txt`
   - `README.md`

3. **폴더 생성**: 
   - `.github/workflows/` 폴더 생성
   - `github_actions_workflow.yml` 파일을 **`daily-news-bot.yml`**로 이름 변경하여 업로드

#### **방법 B: Git 명령어로 업로드** (선택사항)
```bash
git clone https://github.com/your-username/daily-news-bot.git
cd daily-news-bot

# 파일들 복사
cp /path/to/files/* .
mkdir -p .github/workflows
cp github_actions_workflow.yml .github/workflows/daily-news-bot.yml

git add .
git commit -m "Initial commit: Daily News Bot"
git push origin main
```

### **3단계: GitHub Secrets 설정**
1. Repository → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭하여 아래 4개 추가:

```bash
# 이미 준비된 API 키들
NAVER_CLIENT_ID
Value: i_ExQRquc2oFsTFDyLoz

NAVER_CLIENT_SECRET  
Value: eJpNFD4w1Z

GEMINI_API_KEY
Value: your API Key

# 나중에 받을 카카오 API 키
KAKAO_API_KEY
Value: YOUR_KAKAO_API_KEY_HERE  (일단 이렇게 설정)
```

### **4단계: 첫 실행 테스트**
1. Repository → **Actions** 탭
2. **Daily News Bot** 워크플로우 클릭
3. **Run workflow** 버튼 클릭
4. **Run workflow** 확인

### **5단계: 실행 결과 확인**
- ✅ **성공 시**: 초록색 체크마크 표시
- ❌ **실패 시**: 빨간색 X 표시 → 로그 클릭하여 오류 확인

## 📱 카카오 API 키 발급 방법

### **카카오 개발자센터 설정**
1. **카카오 개발자센터 접속**: https://developers.kakao.com/
2. **로그인** → **내 애플리케이션** → **애플리케이션 추가하기**
3. **앱 이름**: "Daily News Bot" 입력
4. **사업자명**: 개인 또는 사업자명 입력

### **API 설정**
1. **생성된 앱** 클릭
2. **제품 설정** → **카카오톡 메시지** → **활성화**
3. **앱 키** → **JavaScript 키** 복사

### **GitHub Secrets 업데이트**
1. Repository → Settings → Secrets → Actions
2. **KAKAO_API_KEY** 클릭 → **Update**
3. 복사한 JavaScript 키 입력 → **Update secret**

## ⏰ 자동 실행 확인

### **스케줄 설정**
- **실행 시간**: 매일 오전 8시 (한국시간)
- **UTC 기준**: 매일 23시 (9시간 차이)
- **설정 파일**: `.github/workflows/daily-news-bot.yml`

### **실행 상태 모니터링**
```bash
# GitHub에서 확인
Repository → Actions → Daily News Bot → 최근 실행 기록

# 성공률 확인  
- 초록색 체크: 성공
- 빨간색 X: 실패 (로그 확인 필요)
```

## 🔍 문제 해결

### **일반적인 오류들**

#### **1. "Secrets 설정 오류"**
```bash
오류: secrets.NAVER_CLIENT_ID가 비어있음
해결: GitHub Secrets에서 API 키 다시 확인 및 설정
```

#### **2. "파일 경로 오류"**  
```bash
오류: ModuleNotFoundError: No module named 'naver_news_collector'
해결: 모든 .py 파일이 루트 디렉토리에 있는지 확인
```

#### **3. "카카오 API 연결 실패"**
```bash
상태: ⚠️ 테스트 모드
해결: 실제 카카오 API 키 발급 후 Secrets 업데이트
```

#### **4. "Gemini API 토큰 초과"**
```bash
상태: 정상 (폴백 메커니즘으로 스마트 자르기 작동)
확인: 메시지가 정상적으로 생성되는지 확인
```

### **로그 확인 방법**
1. Actions → 실패한 워크플로우 클릭
2. **send-daily-news** 클릭
3. 각 단계별 로그 펼쳐서 오류 메시지 확인

## 📊 성공 지표

### **시스템이 정상 작동하는 신호**
- ✅ GitHub Actions 초록색 체크마크
- ✅ 뉴스 5개 수집 완료
- ✅ 메시지 길이 1000자 이내
- ✅ 발송 성공률 100%

### **일일 실행 로그 예시**
```
🎉 Daily News Bot 실행 완료!
============================================================
📊 최종 결과:
   - 수집된 뉴스: 5개
   - 발송 성공: 1명 (테스트 모드)
   - 발송 실패: 0명
   - 메시지 길이: 870자
============================================================
```

## 🎯 다음 단계

### **카카오 API 키 받은 후**
1. GitHub Secrets → KAKAO_API_KEY 업데이트
2. 테스트 실행으로 실제 카카오톡 발송 확인
3. 구독자 관리 시스템 고도화

### **서비스 확장**
1. **비즈니스 채널** 생성 및 승인
2. **구독자 DB** 구축  
3. **결제 시스템** 연동
4. **웹 대시보드** 개발

---

## 🎉 **축하합니다!**

이제 **완전 자동화된 뉴스 구독 서비스**가 준비되었습니다!

### **현재 상태**
- ✅ **뉴스 수집**: 네이버 API로 실시간 수집
- ✅ **AI 편집**: Gemini로 자동 요약 (폴백 포함)
- ✅ **자동 발송**: 매일 오전 8시 정시 실행
- ⚠️ **카카오 발송**: API 키만 있으면 즉시 실제 발송 가능

### **카카오 API 키만 받으면**
- 📱 실제 카카오톡으로 뉴스 발송 시작
- 👥 구독자들에게 서비스 제공 가능
- 💰 수익 창출 시작

**모든 시스템이 완성되었습니다! 🚀**
