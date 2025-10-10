import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import time
import urllib.parse
try:
    from dateutil import parser
except ImportError:
    parser = None

class NaverNewsCollector:
    """네이버 뉴스 API 기반 뉴스 수집기"""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        # 네이버 API 인증 정보
        self.client_id = client_id or "i_ExQRquc2oFsTFDyLoz"
        self.client_secret = client_secret or "eJpNFD4w1Z"
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        # 대기업 키워드 리스트
        self.major_companies = [
            # 삼성그룹
            "삼성전자", "삼성바이오로직스", "삼성SDI", "삼성SDS", "삼성물산", "삼성생명", 
            "삼성화재", "삼성카드", "삼성증권", "삼성엔지니어링", "삼성디스플레이", "삼성바이오에피스",
            
            # LG그룹
            "LG전자", "LG화학", "LG에너지솔루션", "LG디스플레이", "LG이노텍", "LG생활건강",
            "LG유플러스", "LG CNS", "LG하우시스", "LG헬로비전",
            
            # SK그룹
            "SK하이닉스", "SK텔레콤", "SK이노베이션", "SK바이오팜", "SK바이오사이언스",
            "SK에코플랜트", "SK네트웍스", "SK케미칼", "SK가스", "SK머티리얼즈", "SK스퀘어",
            
            # 현대자동차그룹
            "현대자동차", "기아", "현대모비스", "현대글로비스", "현대건설", "현대제철",
            "현대엔지니어링", "현대일렉트릭", "현대로템", "현대위아", "현대중공업", "현대미포조선",
            
            # 롯데그룹
            "롯데케미칼", "롯데쇼핑", "롯데지주", "롯데칠성음료", "롯데웰푸드", "롯데정밀화학",
            "롯데렌탈", "롯데관광개발", "롯데하이마트", "롯데홀딩스", "롯데월드", "롯데푸드",
            
            # 포스코그룹
            "포스코홀딩스", "포스코", "포스코인터내셔널", "포스코케미칼", "포스코DX",
            "포스코이차전지소재", "포스코에너지", "포스코건설", "포스코플랜텍",
            
            # 한화그룹
            "한화솔루션", "한화오션", "한화에어로스페이스", "한화시스템", "한화생명",
            "한화손해보험", "한화투자증권", "한화호텔앤드리조트", "한화큐셀", "한화갤러리아",
            
            # 두산그룹
            "두산에너빌리티", "두산로보틱스", "두산퓨얼셀", "두산건설", "두산밥캣", "두산중공업",
            
            # GS그룹
            "GS건설", "GS리테일", "GS칼텍스", "GS홈쇼핑", "GS25", "GS EPS",
            
            # 금융지주/은행
            "KB금융지주", "신한지주", "하나금융지주", "우리금융지주", "NH농협금융지주",
            "KB국민은행", "신한은행", "하나은행", "우리은행", "NH농협은행", 
            "카카오뱅크", "토스뱅크", "케이뱅크", "미래에셋증권", "NH투자증권",
            
            # 보험
            "삼성생명", "한화생명", "교보생명", "미래에셋생명", "동양생명", "흥국생명",
            "삼성화재", "현대해상", "DB손해보험", "메리츠화재", "KB손해보험",
            
            # IT/게임/플랫폼
            "네이버", "카카오", "카카오페이", "엔씨소프트", "넷마블", "크래프톤", "NHN",
            "위메이드", "펄어비스", "컴투스", "데브시스터즈", "카카오게임즈", "스마일게이트",
            "넥슨", "웹젠", "엠게임", "한게임", "네오위즈", "컴투스홀딩스",
            
            # 통신
            "KT", "LG유플러스", "SK텔레콤", "SK브로드밴드", "KT스카이라이프",
            
            # 항공/물류
            "대한항공", "아시아나항공", "제주항공", "진에어", "티웨이항공", "에어부산",
            "CJ대한통운", "한진", "현대글로비스", "로지스밸리", "쿠팡", "마켓컬리",
            
            # 유통/백화점
            "신세계", "롯데쇼핑", "이마트", "홈플러스", "코스트코", "메가마트",
            "현대백화점", "갤러리아백화점", "AK플라자", "NC백화점",
            
            # 식품/생활용품
            "농심", "오뚜기", "CJ제일제당", "동원F&B", "빙그레", "매일홀딩스",
            "남양유업", "한국야쿠르트", "롯데칠성음료", "코카콜라", "웅진식품",
            "아모레퍼시픽", "LG생활건강", "애경산업", "유한킴벌리", "한국P&G",
            
            # 건설/부동산
            "현대건설", "GS건설", "대림산업", "두산건설", "태영건설", "HDC현대산업개발",
            "호반건설", "대우건설", "중흥건설", "코오롱글로벌", "한국토지신탁",
            
            # 화학/소재
            "LG화학", "한화솔루션", "SK케미칼", "금호석유화학", "효성화학", "효성티앤씨",
            "코오롱인더스트리", "태광산업", "후성", "OCI", "덕양산업", "SK이노베이션",
            
            # 철강/금속
            "포스코", "현대제철", "동국제강", "부국철강", "한국철강", "KG스틸",
            
            # 조선/해운
            "한국조선해양", "대우조선해양", "삼성중공업", "현대중공업", "한진해운", "HMM",
            
            # 에너지/공기업
            "한국전력", "한국가스공사", "한국석유공사", "한국수력원자력", "한국지역난방공사",
            "SK가스", "GS칼텍스", "S-Oil", "현대오일뱅크",
            
            # 바이오/제약
            "셀트리온", "삼성바이오로직스", "SK바이오팜", "한미약품", "대웅제약", "유한양행",
            "녹십자", "JW중외제약", "종근당", "동아에스티", "부광약품", "한국콜마",
            
            # 반도체/디스플레이
            "삼성전자", "SK하이닉스", "LG디스플레이", "삼성디스플레이", "DB하이텍", "실리콘웍스",
            
            # 기타 대기업
            "KAI", "한국항공우주산업", "두산밥캣", "볼보건설기계",
            "BGF리테일", "GS25", "CU", "세븐일레븐", "이마트24", "미니스톱"
        ]
        
        # 산업별 키워드 (각 산업별로 2개 뉴스씩)
        self.industry_keywords = {
            "조선": [
                # 조선 기업들
                "현대중공업", "대우조선해양", "삼성중공업", "한국조선해양", "현대미포조선",
                # 조선 관련 키워드
                "조선", "선박", "해양플랜트", "LNG선", "컨테이너선", "크루즈", "친환경선박", 
                "스마트십", "해운", "항만", "물류센터", "선박발주", "조선업", "선박수주"
            ],
            "반도체": [
                # 반도체 기업들
                "삼성전자", "SK하이닉스", "LG디스플레이", "삼성디스플레이", "DB하이텍", 
                "실리콘웍스", "SK실트론", "솔브레인", "머티리얼즈파크",
                # 반도체 관련 키워드
                "반도체", "메모리", "시스템반도체", "파운드리", "웨이퍼", "칩", "D램", "낸드플래시",
                "GPU", "CPU", "AP", "반도체공급망", "반도체투자", "반도체공장"
            ],
            "철강": [
                # 철강 기업들
                "포스코", "현대제철", "동국제강", "부국철강", "한국철강", "KG스틸", "세아베스틸",
                # 철강 관련 키워드
                "철강", "제철", "스테인리스", "철광석", "코크스", "고로", "전기로", "압연",
                "철강재", "강관", "선재", "철스크랩", "철강수출", "철강가격"
            ],
            "금융": [
                # 금융 기업들
                "KB금융지주", "신한지주", "하나금융지주", "우리금융지주", "NH농협금융지주",
                "카카오뱅크", "토스뱅크", "케이뱅크", "미래에셋증권", "NH투자증권", "KB증권",
                # 금융 관련 키워드
                "은행", "증권", "보험", "카드", "대출", "예금", "금리", "핀테크", "디지털뱅킹",
                "자산관리", "투자", "IPO", "펀드", "금융지주", "금융실적"
            ],
            "식품": [
                # 식품 기업들
                "농심", "오뚜기", "CJ제일제당", "동원F&B", "빙그레", "매일홀딩스",
                "남양유업", "한국야쿠르트", "롯데칠성음료", "웅진식품", "삼양식품",
                # 식품 관련 키워드
                "식품", "음료", "유제품", "라면", "과자", "냉동식품", "건강식품", "프랜차이즈",
                "외식", "배달", "식자재", "원료", "식품안전", "수출", "브랜드"
            ],
            "건설": [
                # 건설 기업들
                "현대건설", "GS건설", "대림산업", "두산건설", "태영건설", "HDC현대산업개발",
                "호반건설", "대우건설", "중흥건설", "코오롱글로벌", "한국토지신탁",
                # 건설 관련 키워드
                "건설", "건축", "토목", "아파트", "오피스텔", "재개발", "재건축", "분양",
                "인프라", "도로", "교량", "터널", "공항", "항만", "플랜트", "해외수주"
            ],
            "바이오": [
                # 바이오 기업들
                "셀트리온", "삼성바이오로직스", "SK바이오팜", "한미약품", "대웅제약", "유한양행",
                "녹십자", "JW중외제약", "종근당", "동아에스티", "부광약품", "한국콜마",
                # 바이오 관련 키워드
                "바이오", "제약", "신약", "의약품", "임상시험", "허가", "FDA", "식약처",
                "바이오시밀러", "항체", "백신", "치료제", "의료기기", "헬스케어", "디지털헬스"
            ]
        }
        
        # API 요청 헤더
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
    
    def search_news_by_keyword(self, keyword: str, display: int = 10) -> List[Dict]:
        """키워드로 뉴스 검색"""
        try:
            params = {
                "query": keyword,
                "display": display,
                "start": 1,
                "sort": "date"
            }
            
            response = requests.get(self.base_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for item in data.get('items', []):
                    title = self.clean_html_tags(item.get('title', ''))
                    description = self.clean_html_tags(item.get('description', ''))
                    pub_date = self.parse_pub_date(item.get('pubDate', ''))
                    
                    if self.is_recent_news(pub_date):
                        news_item = {
                            "title": title,
                            "description": description,
                            "link": item.get('link', ''),
                            "pubDate": pub_date.strftime("%Y-%m-%d %H:%M") if pub_date else "시간 미상",
                            "originallink": item.get('originallink', ''),
                            "keyword": keyword,
                            "importance_score": 0
                        }
                        news_items.append(news_item)
                
                return news_items
            else:
                print(f"API 요청 실패: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"뉴스 검색 중 오류 ({keyword}): {str(e)}")
            return []
    
    def clean_html_tags(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = clean_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        clean_text = clean_text.replace('&quot;', '"').replace('&#39;', "'")
        return clean_text.strip()
    
    def parse_pub_date(self, pub_date_str: str) -> datetime:
        """발행일 파싱"""
        try:
            from datetime import datetime
            import locale
            
            try:
                locale.setlocale(locale.LC_TIME, 'C')
            except:
                pass
                
            pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
            return pub_date.replace(tzinfo=None)
            
        except Exception as e:
            print(f"날짜 파싱 오류: {pub_date_str} - {str(e)}")
            return None
    
    def is_recent_news(self, pub_date: datetime, hours: int = 48) -> bool:
        """최근 뉴스인지 확인 (48시간으로 확장)"""
        if not pub_date:
            return False
        
        now = datetime.now()
        time_diff = now - pub_date
        return time_diff.total_seconds() <= (hours * 3600)
    
    def collect_news_by_industry(self, news_per_industry: int = 2) -> List[Dict]:
        """산업별로 뉴스 수집 (각 산업별 2개씩)"""
        all_news = []
        
        print("🏭 산업별 뉴스 수집 시작...")
        print(f"📊 목표: 7개 산업 × {news_per_industry}개 = 총 {7 * news_per_industry}개 뉴스")
        
        for industry, keywords in self.industry_keywords.items():
            print(f"\n🔍 {industry} 산업 뉴스 수집 중...")
            
            industry_news = []
            
            # 각 산업별로 상위 5개 키워드만 사용
            priority_keywords = keywords[:5]
            
            for keyword in priority_keywords:
                if len(industry_news) >= news_per_industry * 3:  # 여유분 확보
                    break
                    
                print(f"  🔎 '{keyword}' 검색 중...")
                news_items = self.search_news_by_keyword(keyword, display=5)
                
                for news in news_items:
                    news['industry'] = industry
                    news['category'] = industry  # 호환성을 위해
                
                industry_news.extend(news_items)
                time.sleep(0.1)  # API 제한 대응
            
            # 각 산업별로 최고 품질 뉴스만 선별
            if industry_news:
                top_industry_news = self.select_top_news_for_industry(
                    industry_news, industry, news_per_industry
                )
                all_news.extend(top_industry_news)
                print(f"  ✅ {industry}: {len(top_industry_news)}개 뉴스 선별")
            else:
                print(f"  ❌ {industry}: 뉴스를 찾을 수 없음")
        
        print(f"\n🎯 총 수집된 뉴스: {len(all_news)}개")
        return all_news
    
    def select_top_news_for_industry(self, news_list: List[Dict], industry: str, top_n: int) -> List[Dict]:
        """각 산업별로 최고 품질 뉴스 선별"""
        if not news_list:
            return []
        
        # 중요도 점수 계산
        for news in news_list:
            news['importance_score'] = self.calculate_industry_importance_score(news, industry)
        
        # 중복 제거 (제목 기준)
        unique_news = {}
        for news in news_list:
            title_key = news['title'][:40]
            if title_key not in unique_news or news['importance_score'] > unique_news[title_key]['importance_score']:
                unique_news[title_key] = news
        
        # 중요도 순 정렬 후 상위 선택
        sorted_news = sorted(unique_news.values(), key=lambda x: x['importance_score'], reverse=True)
        return sorted_news[:top_n]
    
    def calculate_industry_importance_score(self, news_item: Dict, industry: str) -> int:
        """산업별 뉴스 중요도 점수 계산 (세분화)"""
        title = news_item['title'].lower()
        description = news_item['description'].lower()
        content = title + " " + description
        
        score = 5  # 기본 점수
        
        # 산업별 고중요도 키워드
        industry_high_keywords = {
            "조선": ["수주", "발주", "인도", "계약", "실적", "매출", "투자"],
            "반도체": ["생산", "투자", "공급", "수요", "가격", "실적", "개발", "기술"],
            "철강": ["생산", "가격", "수출", "투자", "실적", "원료", "수요"],
            "금융": ["실적", "대출", "예금", "수익", "투자", "인수", "합병", "상장"],
            "식품": ["출시", "론칭", "매출", "수출", "브랜드", "인수", "투자"],
            "건설": ["수주", "분양", "개발", "투자", "매출", "해외", "프로젝트"],
            "바이오": ["승인", "허가", "임상", "개발", "투자", "수출", "계약", "기술이전"]
        }
        
        # 산업별 중요도 키워드 점수 추가
        high_keywords = industry_high_keywords.get(industry, [])
        for keyword in high_keywords:
            if keyword in content:
                score += 3
        
        # 기업명 포함 시 추가 점수
        for company in self.major_companies:
            if company.lower() in content:
                score += 2
                break
        
        # 숫자 포함 (실적, 금액 등) 시 추가 점수
        import re
        if re.search(r'\d+억|\d+조|\d+만|\d+%', content):
            score += 2
        
        # 중요 액션 키워드
        action_keywords = ["발표", "계획", "추진", "발주", "수주", "체결", "합의", "승인", "허가"]
        for keyword in action_keywords:
            if keyword in content:
                score += 1
        
        return score
    
    def get_balanced_news(self, news_list: List[Dict]) -> List[Dict]:
        """산업별 균형 조정 (각 산업 최대 2개)"""
        industry_count = {}
        balanced_news = []
        max_per_industry = 2
        
        # 중요도 순으로 정렬
        sorted_news = sorted(news_list, key=lambda x: x['importance_score'], reverse=True)
        
        for news in sorted_news:
            industry = news.get('industry', news.get('category', '기타'))
            current_count = industry_count.get(industry, 0)
            
            if current_count < max_per_industry:
                balanced_news.append(news)
                industry_count[industry] = current_count + 1
                
            # 14개 달성 시 종료 (7개 산업 × 2개)
            if len(balanced_news) >= 14:
                break
        
        return balanced_news
    
    def format_industry_distribution(self, news_list: List[Dict]) -> str:
        """산업별 분포 현황 출력"""
        industry_count = {}
        for news in news_list:
            industry = news.get('industry', news.get('category', '기타'))
            industry_count[industry] = industry_count.get(industry, 0) + 1
        
        result = "📊 산업별 뉴스 분포:\n"
        for industry, count in industry_count.items():
            result += f"  • {industry}: {count}개\n"
        
        return result
    
    # 호환성을 위한 기존 메소드명 유지
    def collect_all_news(self, news_per_keyword: int = 2) -> List[Dict]:
        """기존 호환성을 위한 메소드 (collect_news_by_industry 호출)"""
        return self.collect_news_by_industry(news_per_industry=2)
    
    def filter_and_rank_news(self, news_list: List[Dict], top_n: int = 14) -> List[Dict]:
        """기존 호환성을 위한 메소드 (get_balanced_news 호출)"""
        return self.get_balanced_news(news_list)

class NaverNewsFormatter:
    """네이버 뉴스를 카카오톡 메시지로 포맷팅"""
    
    @staticmethod
    def format_daily_news(news_list: List[Dict]) -> str:
        """일간 뉴스를 카카오톡 메시지 형태로 포맷팅"""
        today = datetime.now().strftime("%Y년 %m월 %d일")
        
        message = f"🏭 {today} 주요 산업 뉴스\n"
        message += "=" * 30 + "\n\n"
        
        # 산업별 이모지
        industry_emojis = {
            "조선": "🚢",
            "반도체": "💻", 
            "철강": "🏭",
            "금융": "💰",
            "식품": "🍜",
            "건설": "🏗️",
            "바이오": "🧬"
        }
        
        # 산업별로 그룹화
        industry_groups = {}
        for news in news_list:
            industry = news.get('industry', news.get('category', '기타'))
            if industry not in industry_groups:
                industry_groups[industry] = []
            industry_groups[industry].append(news)
        
        # 산업별로 출력
        for industry, industry_news in industry_groups.items():
            emoji = industry_emojis.get(industry, "📰")
            message += f"{emoji} {industry} 산업\n"
            message += "─" * 20 + "\n"
            
            for i, news in enumerate(industry_news, 1):
                # 중요도 표시
                if news['importance_score'] >= 12:
                    priority = "🔥 HOT"
                elif news['importance_score'] >= 9:
                    priority = "⭐ 주목"
                else:
                    priority = "📌 일반"
                
                message += f"{priority} {news['title']}\n"
                
                if news['description']:
                    summary = news['description'][:60] + "..." if len(news['description']) > 60 else news['description']
                    message += f"💬 {summary}\n"
                
                message += f"🕐 {news['pubDate']}\n"
                message += f"🔗 {news['link']}\n\n"
            
            message += "\n"
        
        # 인사이트 추가
        message += "💡 오늘의 산업 인사이트\n"
        message += "─" * 25 + "\n"
        
        # 가장 많은 뉴스가 나온 산업 분석
        industry_counts = {}
        for news in news_list:
            industry = news.get('industry', news.get('category', '기타'))
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        if industry_counts:
            most_active = max(industry_counts.items(), key=lambda x: x[1])
            insights = {
                "조선": "🚢 조선업계 동향이 활발합니다. 수주 실적을 주목하세요!",
                "반도체": "💻 반도체 시장 변화가 감지됩니다. 공급망을 체크하세요!",
                "철강": "🏭 철강업계 흐름 변화에 주의가 필요합니다.",
                "금융": "💰 금융시장 동향을 면밀히 살펴보세요.",
                "식품": "🍜 식품업계 새로운 트렌드가 나타나고 있습니다.",
                "건설": "🏗️ 건설업계 수주 동향을 확인하세요.",
                "바이오": "🧬 바이오 분야 기술 발전이 가속화되고 있습니다."
            }
            
            insight = insights.get(most_active[0], "📊 다양한 산업 분야의 균형잡힌 정보를 확인하세요.")
            message += f"{insight}\n\n"
        
        message += "─" * 30 + "\n"
        message += "📅 매일 오전 8시 발송\n"
        message += "🏭 7대 주요 산업 전문 정보\n" 
        message += "📞 문의: 비즈니스 채널 채팅"
        
        return message

# 테스트 실행 함수
def run_naver_news_test():
    """네이버 뉴스 API 테스트"""
    print("🚀 산업별 뉴스 수집 시스템 테스트 시작!")
    print("=" * 60)
    
    # 뉴스 수집기 초기화
    collector = NaverNewsCollector()
    
    # 산업별 뉴스 수집 (각 산업별 2개씩)
    all_news = collector.collect_news_by_industry(news_per_industry=2)
    
    if not all_news:
        print("❌ 뉴스를 수집할 수 없습니다. API 설정을 확인해주세요.")
        return
    
    # 산업별 균형 조정
    balanced_news = collector.get_balanced_news(all_news)
    print(f"\n🎯 최종 선별된 뉴스: {len(balanced_news)}개")
    
    # 산업별 분포 출력
    print(collector.format_industry_distribution(balanced_news))
    
    # 뉴스 품질 분석
    high_quality = [n for n in balanced_news if n['importance_score'] >= 10]
    medium_quality = [n for n in balanced_news if 7 <= n['importance_score'] < 10]
    normal_quality = [n for n in balanced_news if n['importance_score'] < 7]
    
    print(f"📈 뉴스 품질 분석:")
    print(f"  🔥 고품질 (10점 이상): {len(high_quality)}개")
    print(f"  ⭐ 중품질 (7-9점): {len(medium_quality)}개") 
    print(f"  📌 일반 (7점 미만): {len(normal_quality)}개")
    
    # 카카오톡 메시지 포맷팅
    formatter = NaverNewsFormatter()
    kakao_message = formatter.format_daily_news(balanced_news)
    
    print("\n📱 카카오톡 메시지 포맷 완료")
    print("=" * 80)
    print(kakao_message)
    print("=" * 80)
    
    # JSON 파일로 저장
    with open('/home/user/industry_news_data.json', 'w', encoding='utf-8') as f:
        json.dump(balanced_news, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 뉴스 데이터가 industry_news_data.json에 저장되었습니다.")
    print(f"📊 메시지 길이: {len(kakao_message)}자 (카카오톡 제한: 1000자)")
    
    return kakao_message, balanced_news

if __name__ == "__main__":
    run_naver_news_test()
