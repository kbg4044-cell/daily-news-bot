# 📰 이중 뉴스봇 시스템

**2개의 독립적인 뉴스봇**이 매일 자동으로 카카오톡으로 뉴스를 전달합니다!

---

## 🎯 2개의 봇

### 1️⃣ **고용뉴스봇** 💼
- **실행 시간**: 매일 오전 9시
- **내용**: 채용/고용/취업 뉴스 10개
- **특징**: 
  - 중복 제거 강화 (URL + 제목 유사도)
  - AI 채용포인트 자동 생성
  - 산업별 카테고리 자동 분류

**포맷:**
```
💼 오늘의 고용/채용 뉴스 (12월 30일)
==============================

[조선]
"현대중공업, LNG선 10척 수주"
링크: https://news.naver.com/...
채용포인트: 대규모 수주로 신규 인력 채용 예상

[IT]
"네이버, AI 개발자 200명 채용"
링크: https://news.naver.com/...
채용포인트: AI 부문 확대로 대규모 채용 진행
```

---

### 2️⃣ **기업뉴스봇** 🏢
- **실행 시간**: 매일 오전 8시
- **내용**: 산업별 기업 동향 뉴스 14개 (7개 산업 × 2개)
- **산업**: IT/기술, 조선, 반도체, 제조/산업, 금융, 건설/부동산, 바이오/의료

**포맷:**
```
🏢 오늘의 산업 뉴스 (12월 30일)
==============================

💻 IT/기술
1. 네이버, AI 신사업 확대
   https://news.naver.com/...
2. 카카오, 클라우드 투자 강화
   https://news.naver.com/...

🚢 조선
1. 현대중공업, 수주 실적 호조
   https://news.naver.com/...
```

---

## 📂 프로젝트 구조

```
dual_news_bot/
├── employment_bot/              # 고용뉴스봇 (오전 9시)
│   ├── daily_employment_news.py
│   ├── naver_employment_collector.py  # 중복 제거 강화
│   ├── gemini_employment_editor.py
│   ├── kakao_sender.py
│   └── requirements.txt
│
├── corporate_bot/               # 기업뉴스봇 (오전 8시)
│   ├── daily_corporate_news.py
│   ├── naver_corporate_collector.py   # 산업별 수집
│   ├── gemini_corporate_editor.py
│   ├── kakao_sender.py
│   └── requirements.txt
│
└── .github/
    └── workflows/
        ├── employment-news.yml  # 오전 9시 실행
        └── corporate-news.yml   # 오전 8시 실행
```

---

## 🚀 설치 방법

### 1. GitHub 저장소 생성

```bash
# 새 저장소 생성
git init dual-news-bot
cd dual-news-bot

# 파일 복사
# (다운로드한 파일들을 여기에 복사)
```

### 2. GitHub Secrets 설정

`Settings` > `Secrets and variables` > `Actions`

| Secret 이름 | 설명 |
|------------|------|
| `NAVER_CLIENT_ID` | 네이버 API 클라이언트 ID |
| `NAVER_CLIENT_SECRET` | 네이버 API 시크릿 |
| `GEMINI_API_KEY` | Google Gemini API 키 |
| `KAKAO_REST_API_KEY` | 카카오 REST API 키 |
| `KAKAO_REFRESH_TOKEN` | 카카오 Refresh Token |

### 3. GitHub에 푸시

```bash
git add .
git commit -m "Initial commit: Dual news bot system"
git branch -M main
git remote add origin https://github.com/your-username/dual-news-bot.git
git push -u origin main
```

---

## ⏰ 실행 일정

| 봇 | 시간 (KST) | 내용 |
|----|-----------|------|
| 기업뉴스봇 🏢 | 오전 8시 | 산업별 기업 동향 14개 |
| 고용뉴스봇 💼 | 오전 9시 | 채용/고용 뉴스 10개 |

---

## 🔧 수동 실행

GitHub Actions 탭에서:
1. **Employment News Bot** 또는 **Corporate News Bot** 선택
2. **Run workflow** 클릭
3. 1-2분 대기
4. 카카오톡 확인

---

## 🎯 중복 제거 로직 (고용뉴스봇)

### 3단계 중복 제거:

1. **URL 중복 제거**
   - 원본 URL + 정규화된 URL (파라미터 제거)
   - 같은 기사를 다른 URL로 올린 경우 제거

2. **제목 유사도 제거**
   - 핵심 키워드 추출하여 시그니처 생성
   - 같은 내용이지만 제목이 다른 기사 제거

3. **날짜 필터링**
   - 최근 2일 이내 뉴스만
   - 오래된 뉴스 자동 제외

---

## 🤖 AI 기능

### 고용뉴스봇:
- 각 뉴스에 대한 **채용포인트** 자동 생성
- 30자 이내로 핵심 인사이트 제공
- 구직자 관점에서 분석

### 기업뉴스봇:
- HTML 태그 제거 및 텍스트 정리
- 산업별 카테고리 자동 분류

---

## ⚙️ 설정 변경

### 실행 시간 변경

**고용뉴스봇** (`.github/workflows/employment-news.yml`):
```yaml
schedule:
  - cron: '0 0 * * *'  # 오전 9시 (KST)
  # - cron: '0 1 * * *'  # 오전 10시로 변경
```

**기업뉴스봇** (`.github/workflows/corporate-news.yml`):
```yaml
schedule:
  - cron: '0 23 * * *'  # 오전 8시 (KST)
  # - cron: '0 22 * * *'  # 오전 7시로 변경
```

### 뉴스 개수 변경

**고용뉴스봇** (`employment_bot/daily_employment_news.py`):
```python
raw_news = collector.collect_unique_news(count=30)  # 수집 개수
formatted_news = editor.format_news_with_recruitment_point(raw_news[:10])  # 발송 개수
```

**기업뉴스봇** (`corporate_bot/naver_corporate_collector.py`):
```python
result[industry] = filtered_news[:2]  # 산업별 2개
# result[industry] = filtered_news[:3]  # 산업별 3개로 변경
```

---

## 📝 로컬 테스트

### 고용뉴스봇 테스트:
```bash
cd employment_bot

export NAVER_CLIENT_ID="your_id"
export NAVER_CLIENT_SECRET="your_secret"
export GEMINI_API_KEY="your_key"
export KAKAO_REST_API_KEY="your_key"
export KAKAO_REFRESH_TOKEN="your_token"

python daily_employment_news.py
```

### 기업뉴스봇 테스트:
```bash
cd corporate_bot

# (환경 변수 동일)

python daily_corporate_news.py
```

---

## 🆘 문제 해결

### Q1: 중복 뉴스가 계속 나와요
**A:** `naver_employment_collector.py`의 중복 제거 로직이 강화되었습니다. 
- URL 중복 제거
- 제목 유사도 제거
- 날짜 필터링

여전히 중복이 발생하면 날짜 필터를 더 좁게 조정:
```python
filtered = self._filter_by_date(unique_by_title, days=1)  # 1일로 변경
```

### Q2: 2개 봇이 모두 실행되나요?
**A:** 네! 독립적으로 실행됩니다:
- 오전 8시: 기업뉴스봇
- 오전 9시: 고용뉴스봇

### Q3: 한 개 봇만 사용하고 싶어요
**A:** 해당 워크플로우 파일을 삭제하세요:
- 고용뉴스봇만: `corporate-news.yml` 삭제
- 기업뉴스봇만: `employment-news.yml` 삭제

---

## 📊 비교표

| 항목 | 고용뉴스봇 💼 | 기업뉴스봇 🏢 |
|------|-------------|-------------|
| 실행 시간 | 오전 9시 | 오전 8시 |
| 뉴스 개수 | 10개 | 14개 |
| 키워드 | 채용/고용/취업 | 산업/기업 동향 |
| AI 기능 | 채용포인트 생성 | 텍스트 정리 |
| 중복 제거 | 3단계 강화 | 기본 제거 |
| 포맷 | 카테고리+링크+포인트 | 산업별 목록 |

---

## 🎉 완성!

이제 매일 아침:
- **8시**: 산업 뉴스 14개 📊
- **9시**: 고용 뉴스 10개 💼

자동으로 카카오톡으로 받아보세요!

---

**Made with ❤️ for Job Seekers & Industry Watchers**
