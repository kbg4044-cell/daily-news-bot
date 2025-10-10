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
        
        # 산업/취업/기업 중심 검색 키워드
        self.search_keywords = {
            "취업/고용": ["채용", "취업", "일자리", "고용", "구인", "신입사원", "경력직"],
            "기업동향": ["기업실적", "IPO", "상장", "M&A", "인수합병", "CEO", "대표이사"],
            "IT/기술": ["스타트업", "벤처투자", "AI", "인공지능", "IT", "테크", "플랫폼"],
            "제조/산업": ["반도체", "자동차", "조선", "철강", "화학", "제조업", "공장"],
            "부동산/건설": ["부동산", "건설", "아파트", "인프라", "토지", "분양"]
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
                "display": display,  # 최대 100개
                "start": 1,
                "sort": "date"  # 날짜순 정렬 (최신순)
            }
            
            response = requests.get(self.base_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for item in data.get('items', []):
                    # HTML 태그 제거
                    title = self.clean_html_tags(item.get('title', ''))
                    description = self.clean_html_tags(item.get('description', ''))
                    
                    # 발행일 파싱
                    pub_date = self.parse_pub_date(item.get('pubDate', ''))
                    
                    # 24시간 이내 뉴스만 필터링
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
        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', text)
        # HTML 엔티티 디코딩
        clean_text = clean_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        clean_text = clean_text.replace('&quot;', '"').replace('&#39;', "'")
        return clean_text.strip()
    
    def parse_pub_date(self, pub_date_str: str) -> datetime:
        """발행일 파싱"""
        try:
            # 네이버 API 날짜 형식: "Mon, 09 Oct 2023 14:30:00 +0900"
            from datetime import datetime
            import locale
            
            # 영어 로케일 설정 (날짜 파싱을 위해)
            try:
                locale.setlocale(locale.LC_TIME, 'C')
            except:
                pass
                
            # 날짜 파싱
            pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
            # 시간대를 로컬 시간으로 변환
            return pub_date.replace(tzinfo=None)
            
        except Exception as e:
            print(f"날짜 파싱 오류: {pub_date_str} - {str(e)}")
            return None
    
    def is_recent_news(self, pub_date: datetime, hours: int = 24) -> bool:
        """최근 뉴스인지 확인"""
        if not pub_date:
            return False
        
        now = datetime.now()
        time_diff = now - pub_date
        return time_diff.total_seconds() <= (hours * 3600)
    
    def collect_all_news(self, news_per_keyword: int = 2) -> List[Dict]:
        """고품질 뉴스만 선별 수집 (최대 25개 제한)"""
        all_news = []
        total_limit = 25  # 전체 뉴스 수집 제한
        
        print("🚀 네이버 뉴스 API로 고품질 뉴스 수집 시작...")
        
        for category, keywords in self.search_keywords.items():
            if len(all_news) >= total_limit:
                break
                
            print(f"📂 {category} 카테고리 뉴스 수집 중...")
            
            # 각 카테고리에서 첫 2개 키워드만 사용 (고품질 키워드 우선)
            priority_keywords = keywords[:2]
            
            for keyword in priority_keywords:
                if len(all_news) >= total_limit:
                    break
                    
                print(f"  🔍 '{keyword}' 검색 중...")
                news_items = self.search_news_by_keyword(keyword, news_per_keyword)
                
                # 카테고리 정보 추가
                for news in news_items:
                    news['category'] = category
                
                all_news.extend(news_items)
                
                # API 호출 제한을 위한 대기 (초당 10회 제한)
                time.sleep(0.1)
        
        # 전체 제한 적용
        all_news = all_news[:total_limit]
        
        print(f"📊 총 {len(all_news)}개 뉴스 수집 완료 (기존 60-70개에서 감소)")
        print(f"  → 최적화: 토큰 절약을 위해 수집량 60% 축소")
        
        # 날짜 필터링 적용 (전날 + 당일 뉴스만)
        filtered_news = self.filter_by_date(all_news)
        
        return filtered_news
    
    def calculate_importance_score(self, news_item: Dict) -> int:
        """뉴스 중요도 점수 계산"""
        title = news_item['title'].lower()
        description = news_item['description'].lower()
        content = title + " " + description
        
        score = 0
        
        # 카테고리별 기본 점수
        category_scores = {
            "취업/고용": 5,
            "기업동향": 4,
            "IT/기술": 3,
            "제조/산업": 3,
            "부동산/건설": 2
        }
        score += category_scores.get(news_item['category'], 1)
        
        # 고중요도 키워드
        high_priority = [
            "대기업", "채용공고", "신입사원", "IPO", "상장", "M&A",
            "실적발표", "매출", "영업이익", "스타트업", "투자유치",
            "반도체", "자동차", "부동산정책"
        ]
        
        for keyword in high_priority:
            if keyword in content:
                score += 2
        
        # 중요도 키워드
        medium_priority = [
            "채용", "취업", "기업", "투자", "산업", "기술",
            "정책", "시장", "성장", "확대", "개발"
        ]
        
        for keyword in medium_priority:
            if keyword in content:
                score += 1
        
        return score
    
    def balance_categories(self, news_list: List[Dict]) -> List[Dict]:
        """카테고리 균형 조정 - 한 카테고리에서 최대 3개까지만 선택"""
        category_count = {}
        balanced_news = []
        max_per_category = 3
        
        # 중요도 순으로 정렬
        sorted_news = sorted(news_list, key=lambda x: x['importance_score'], reverse=True)
        
        for news in sorted_news:
            category = news['category']
            current_count = category_count.get(category, 0)
            
            if current_count < max_per_category:
                balanced_news.append(news)
                category_count[category] = current_count + 1
        
        return balanced_news
    
    def parse_naver_date(self, pub_date_str: str) -> datetime.date:
        """네이버 API pubDate 파싱 (ex: '2025-10-10 13:34' 또는 'Thu, 10 Oct 2025 13:34:00 +0900')"""
        try:
            # 간단한 형식부터 시도 (2025-10-10 13:34)
            if len(pub_date_str.split(' ')) == 2 and '-' in pub_date_str:
                date_part = pub_date_str.split(' ')[0]  # '2025-10-10'
                return datetime.strptime(date_part, '%Y-%m-%d').date()
            
            # dateutil 사용 가능한 경우
            if parser:
                parsed_date = parser.parse(pub_date_str)
                return parsed_date.date()
            
            # 실패 시 오늘 날짜 반환
            return datetime.now().date()
            
        except Exception as e:
            # 파싱 실패 시 오늘 날짜로 처리
            return datetime.now().date()
    
    def filter_by_date(self, news_list: List[Dict]) -> List[Dict]:
        """전날과 당일 뉴스만 필터링"""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        print(f"\n📅 날짜 필터링 적용 중...")
        print(f"  → 대상 날짜: 어제({yesterday}) + 오늘({today})")
        
        today_news = []
        yesterday_news = []
        old_news = []
        
        for news in news_list:
            pub_date = self.parse_naver_date(news['pubDate'])
            
            if pub_date == today:
                today_news.append(news)
            elif pub_date == yesterday:
                yesterday_news.append(news)
            else:
                old_news.append(news)
        
        # 최신 뉴스만 선별
        filtered_news = today_news + yesterday_news
        
        print(f"  → 오늘({today}) 뉴스: {len(today_news)}개")
        print(f"  → 어제({yesterday}) 뉴스: {len(yesterday_news)}개")
        print(f"  → 그 이전 뉴스: {len(old_news)}개 (제외됨)")
        print(f"✅ 필터링 후: {len(filtered_news)}개 뉴스 (최신 뉴스만)")
        
        return filtered_news
    
    def filter_and_rank_news(self, news_list: List[Dict], top_n: int = 5) -> List[Dict]:
        """엄격한 기준으로 고품질 뉴스 5개만 선별"""
        print(f"\n📊 뉴스 선별 기준 적용 중...")
        
        # 1단계: 중요도 점수 계산
        for news in news_list:
            news['importance_score'] = self.calculate_importance_score(news)
        
        # 2단계: 최소 점수 필터링 (전체 뉴스 양 감소)
        min_score = 6  # 기존 5에서 6으로 상향 조정
        filtered_news = [news for news in news_list if news['importance_score'] >= min_score]
        print(f"  → 최소 점수 {min_score}점 이상: {len(filtered_news)}개 뉴스 선별")
        
        # 3단계: 중복 제거 (제목 기준)
        unique_news = {}
        for news in filtered_news:
            title_key = news['title'][:30]  # 제목 앞 30자로 중복 체크
            if title_key not in unique_news or news['importance_score'] > unique_news[title_key]['importance_score']:
                unique_news[title_key] = news
        print(f"  → 중복 제거 후: {len(unique_news)}개 뉴스")
        
        # 4단계: 카테고리 균형 조정 (5개 중 최대 3개가 같은 카테고리)
        category_balanced = self.balance_categories(list(unique_news.values()))
        print(f"  → 카테고리 균형 조정 후: {len(category_balanced)}개 뉴스")
        
        # 5단계: 중요도 순 정렬 후 top_n 선택
        sorted_news = sorted(category_balanced, key=lambda x: x['importance_score'], reverse=True)
        final_news = sorted_news[:top_n]
        
        print(f"\n✅ 최종 선별된 고품질 뉴스: {len(final_news)}개")
        for i, news in enumerate(final_news, 1):
            print(f"    {i}. [{news['category']}] {news['title'][:40]}... (점수: {news['importance_score']})")
        
        return final_news

class NaverNewsFormatter:
    """네이버 뉴스를 카카오톡 메시지로 포맷팅"""
    
    @staticmethod
    def format_daily_news(news_list: List[Dict]) -> str:
        """일간 뉴스를 카카오톡 메시지 형태로 포맷팅"""
        today = datetime.now().strftime("%Y년 %m월 %d일")
        
        message = f"🏭 {today} 산업·취업 뉴스\n"
        message += "=" * 28 + "\n\n"
        
        # 카테고리별 이모지
        category_emojis = {
            "취업/고용": "👔",
            "기업동향": "🏢", 
            "IT/기술": "💻",
            "제조/산업": "🏭",
            "부동산/건설": "🏗️"
        }
        
        for i, news in enumerate(news_list, 1):
            # 중요도에 따른 이모지
            if news['importance_score'] >= 8:
                priority_emoji = "🔥"
            elif news['importance_score'] >= 5:  
                priority_emoji = "⭐"
            else:
                priority_emoji = "📌"
            
            # 카테고리 이모지
            cat_emoji = category_emojis.get(news['category'], "📰")
            
            message += f"{priority_emoji} {i}. {news['title']}\n"
            message += f"   {cat_emoji} {news['category']} | {news['pubDate']}\n"
            
            if news['description']:
                # 요약문이 너무 길면 자르기
                summary = news['description'][:80] + "..." if len(news['description']) > 80 else news['description']
                message += f"   💬 {summary}\n"
            
            message += f"   🔗 {news['link']}\n\n"
        
        # 인사이트 추가
        message += "─" * 28 + "\n"
        message += "💡 오늘의 산업 인사이트\n\n"
        
        # 카테고리 분석
        categories = [news['category'] for news in news_list]
        most_frequent = max(set(categories), key=categories.count) if categories else "일반"
        
        insights = {
            "취업/고용": "🔍 채용 시장이 활발합니다. 새로운 기회를 놓치지 마세요!",
            "기업동향": "📈 기업 실적 시즌입니다. 투자 기회를 살펴보세요.",
            "IT/기술": "💻 기술 혁신이 가속화되고 있습니다. 트렌드를 주목하세요!",
            "제조/산업": "🏭 제조업 동향 변화가 감지됩니다. 공급망을 체크하세요.",
            "부동산/건설": "🏗️ 부동산 정책 변화에 주의가 필요합니다."
        }
        
        insight = insights.get(most_frequent, "📊 다양한 산업 분야의 균형잡힌 정보를 확인하세요.")
        message += f"{insight}\n\n"
        
        message += "─" * 28 + "\n"
        message += "📅 매일 오전 8시 발송\n"
        message += "💼 산업·취업·기업 정보 전문\n"
        message += "📞 문의: 비즈니스 채널 채팅"
        
        return message

# 테스트 실행 함수
def run_naver_news_test():
    """네이버 뉴스 API 테스트"""
    print("🚀 네이버 뉴스 API 테스트 시작!")
    print("=" * 50)
    
    # 뉴스 수집기 초기화
    collector = NaverNewsCollector()
    
    # 뉴스 수집
    all_news = collector.collect_all_news(news_per_keyword=2)
    
    if not all_news:
        print("❌ 뉴스를 수집할 수 없습니다. API 설정을 확인해주세요.")
        return
    
    # 상위 5개 뉴스 선별
    top_news = collector.filter_and_rank_news(all_news, top_n=5)
    print(f"🎯 상위 {len(top_news)}개 뉴스 선별 완료")
    
    # 카테고리 분포 출력
    categories = [news['category'] for news in top_news]
    category_count = {}
    for cat in categories:
        category_count[cat] = category_count.get(cat, 0) + 1
    print(f"📊 카테고리 분포: {category_count}")
    
    # 카카오톡 메시지 포맷팅
    formatter = NaverNewsFormatter()
    kakao_message = formatter.format_daily_news(top_news)
    
    print("\n📱 카카오톡 메시지 포맷 완료")
    print("=" * 60)
    print(kakao_message)
    print("=" * 60)
    
    # JSON 파일로 저장
    with open('/home/user/naver_news_data.json', 'w', encoding='utf-8') as f:
        json.dump(top_news, f, ensure_ascii=False, indent=2)
    
    print("\n💾 뉴스 데이터가 naver_news_data.json에 저장되었습니다.")
    
    return kakao_message, top_news

if __name__ == "__main__":
    run_naver_news_test()