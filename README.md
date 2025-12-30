# 📰 산업뉴스봇 (완전판)

매일 오전 8시, 7개 주요 산업의 핵심 뉴스를 카카오톡으로 자동 발송하는 봇입니다.

## ✨ 주요 기능

- 🏭 **7개 산업 커버**: 조선, 반도체, 철강, 금융, 식품, 건설, 바이오
- 🤖 **Gemini AI 편집**: 자동 요약 및 인사이트 생성
- 📱 **카카오톡 발송**: 나에게 메시지 (자동 토큰 갱신)
- ⏰ **완전 자동화**: PC 없이 GitHub Actions에서 실행
- 🔄 **토큰 자동 갱신**: Refresh Token으로 영구 작동

## 📦 파일 구조

```
daily-news-bot/
├── daily_news_bot.py           # 메인 실행 파일
├── naver_news_collector.py     # 네이버 뉴스 수집
├── gemini_news_editor.py       # Gemini AI 편집
├── kakao_sender.py             # 카카오 발송 (자동 갱신)
├── requirements.txt            # 의존성
├── get_kakao_token.py          # 카카오 토큰 발급 스크립트
├── README.md                   # 이 문서
└── .github/
    └── workflows/
        └── daily-news-bot.yml  # GitHub Actions 워크플로우
```

## 🚀 설치 가이드

### 1단계: 카카오 개발자센터 설정

#### 1-1. 앱 생성
1. https://developers.kakao.com 접속
2. 로그인 > "내 애플리케이션" 클릭
3. "애플리케이션 추가하기"
4. 앱 이름: `산업뉴스봇`

#### 1-2. 플랫폼 설정
1. 생성된 앱 > 좌측 "플랫폼" 클릭
2. "Web 플랫폼 등록"
3. 사이트 도메인: `https://localhost`

#### 1-3. 카카오 로그인 활성화
1. 좌측 "카카오 로그인" 클릭
2. 활성화 설정 **ON**
3. Redirect URI: `https://localhost` 등록

#### 1-4. 동의항목 설정
1. "카카오 로그인" > "동의항목"
2. "카카오톡 메시지 전송" > **필수 동의**

#### 1-5. REST API 키 확인
1. 좌측 "앱 키" 클릭
2. **REST API 키** 복사 📋

---

### 2단계: Refresh Token 발급

로컬 PC에서 `get_kakao_token.py` 실행:

```bash
# 필요한 패키지 설치
pip install requests

# 토큰 발급 스크립트 실행
python get_kakao_token.py
```

**안내에 따라 진행:**
1. REST API 키 입력
2. 브라우저에서 로그인
3. 리다이렉트 URL 복사
4. **REST API 키**와 **Refresh Token** 확인

---

### 3단계: GitHub 저장소 설정

#### 3-1. 저장소 생성
1. GitHub에서 새 Public Repository 생성
2. 이름: `daily-news-bot`

#### 3-2. 파일 업로드
다음 파일들을 업로드:
- `daily_news_bot.py`
- `naver_news_collector.py`
- `gemini_news_editor.py`
- `kakao_sender.py`
- `requirements.txt`
- `.github/workflows/daily-news-bot.yml`

#### 3-3. GitHub Secrets 설정
`Settings` > `Secrets and variables` > `Actions` > `New repository secret`

**추가할 5개 Secret:**

| Name | Value |
|------|-------|
| `NAVER_CLIENT_ID` | 네이버 Client ID |
| `NAVER_CLIENT_SECRET` | 네이버 Client Secret |
| `GEMINI_API_KEY` | Gemini API 키 |
| `KAKAO_REST_API_KEY` | 카카오 REST API 키 |
| `KAKAO_REFRESH_TOKEN` | 카카오 Refresh Token |

---

### 4단계: 테스트 실행

1. GitHub 저장소 > `Actions` 탭
2. "Daily News Bot" 워크플로우 선택
3. `Run workflow` 버튼 클릭
4. 실행 완료 후 카카오톡 확인! 📱

---

## 🔧 API 키 발급 가이드

### 네이버 뉴스 API
1. https://developers.naver.com/apps/#/register
2. 애플리케이션 이름: `산업뉴스봇`
3. 사용 API: **검색**
4. Client ID, Client Secret 복사

### Gemini API
1. https://aistudio.google.com/app/apikey
2. "Create API Key" 클릭
3. API 키 복사

---

## ⏰ 자동 실행

- **시간**: 매일 오전 8시 (한국시간)
- **플랫폼**: GitHub Actions (무료)
- **PC 필요**: ❌ 불필요
- **토큰 갱신**: ✅ 자동

---

## 🎯 주요 특징

### 1. 산업별 수집
- 7개 산업별로 2개씩 총 14개 뉴스
- 100+ 대기업 키워드 기반
- 중요도 점수 자동 계산

### 2. AI 편집
- Gemini 2.0 Flash 사용
- 자동 요약 및 인사이트
- API 오류 시 원본 사용

### 3. 카카오 발송
- 나에게 메시지
- Refresh Token 자동 갱신
- 메시지 길이 자동 조정 (최대 1000자)

### 4. 완전 자동화
- PC 꺼져있어도 작동
- 토큰 만료 걱정 없음
- 오류 시 자동 복구

---

## 📊 비즈니스 모델

### 구독 서비스
- **가격**: 월 10,000원 (6개월 50,000원)
- **목표**: 1,000명 구독자
- **연 매출**: 약 1억원

### 확장 계획
- 단체 카톡방 발송
- 카테고리 커스터마이징
- 프리미엄 인사이트

---

## 🐛 문제 해결

### 뉴스 수집 실패
- 네이버 API 키 확인
- API 호출 한도 확인 (25,000회/일)

### AI 편집 실패
- Gemini API 키 확인
- API 할당량 확인 (무료: 1,500회/일)

### 카카오 발송 실패
- REST API 키 확인
- Refresh Token 확인
- 동의항목 설정 확인

### GitHub Actions 실패
- Secrets 설정 확인
- 워크플로우 파일 확인
- Actions 로그 확인

---

## 📝 라이선스

MIT License

---

## 👨‍💻 개발자

**문의**: GitHub Issues

---

## 🎉 완료!

이제 매일 오전 8시마다 자동으로 뉴스가 도착합니다!

**PC는 꺼두셔도 됩니다! 🚀**
