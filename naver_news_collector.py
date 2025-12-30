"""
네이버 뉴스 수집기 - 산업별 버전
- 7개 주요 산업별 수집
- 100+ 대기업 키워드
- 중요도 점수 기반 선별
"""

import os
import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from html import unescape

class NaverNewsCollector:
    """네이버 뉴스 API 수집기"""
    
    def __init__(self):
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        if not self.client_id or not self.client_secret:
            raise ValueError("❌ 네이버 API 키가 설정되지 않았습니다!")
        
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        # 대기업 키워드 (100+개)
        self.major_companies = [
            # 삼성그룹
            '삼성전자', '삼성디스플레이', '삼성SDI', '삼성바이오로직스', '삼성물산',
            '삼성생명', '삼성화재', '삼성증권', '삼성카드', '삼성웰스토리',
            
            # SK그룹
            'SK하이닉스', 'SK이노베이션', 'SK텔레콤', 'SK브로드밴드', 'SKC',
            'SK네트웍스', 'SK에너지', 'SK케미칼', 'SK바이오팜', 'SK바이오사이언스',
            
            # 현대자동차그룹
            '현대자동차', '기아', '현대모비스', '현대제철', '현대건설',
            '현대엔지니어링', '현대위아', '현대글로비스', '현대로템', '현대오토에버',
            
            # LG그룹
            'LG전자', 'LG화학', 'LG에너지솔루션', 'LG디스플레이', 'LG유플러스',
            'LG생활건강', 'LG하우시스', 'LG이노텍', 'LG CNS', 'LG헬로비전',
            
            # 롯데그룹
            '롯데케미칼', '롯데쇼핑', '롯데칠성', '롯데제과', '롯데푸드',
            '롯데웰푸드', '롯데건설', '롯데렌탈', '롯데정보통신', '호텔롯데',
            
            # 포스코그룹
            '포스코', '포스코인터내셔널', '포스코DX', '포스코케미칼', '포스코에너지',
            
            # 한화그룹
            '한화솔루션', '한화에어로스페이스', '한화오션', '한화시스템', '한화생명',
            '한화손해보험', '한화투자증권', '한화호텔앤드리조트',
            
            # 금융권
            'KB금융', '신한금융', '하나금융', '우리금융', 'NH농협',
            '카카오뱅크', '토스뱅크', '케이뱅크', '미래에셋증권', '삼성증권',
            
            # 통신/IT
            '네이버', '카카오', '엔씨소프트', '넷마블', '크래프톤',
            '쿠팡', '배달의민족', '당근마켓', '토스', '라인',
            
            # 유통/식품
            '신세계', '현대백화점', 'GS리테일', '이마트', '홈플러스',
            '농심', 'CJ제일제당', '오뚜기', '삼양식품', '빙그레',
            '매일유업', '동원F&B', '대상', '사조',
            
            # 건설/부동산
            'GS건설', '대우건설', '대림산업', 'DL이앤씨', 'HDC현대산업개발',
            '중흥건설', '코오롱글로벌', '태영건설',
            
            # 화학/소재
            '한화솔루션', 'LG화학', '롯데케미칼', '금호석유화학', '효성화학',
            'OCI', '코오롱인더스트리', '휴비스',
            
            # 항공/물류
            '대한항공', '아시아나항공', '진에어', '티웨이항공', '제주항공',
            'CJ대한통운', '한진', '현대글로비스',
            
            # 조선
            '한국조선해양', '삼성중공업', '대우조선해양', 'HD현대중공업', 'HD한국조선해양',
            
            # 바이오/제약
            '셀트리온', '삼성바이오로직스', 'SK바이오팜', '유한양행', '녹십자',
            '대웅제약', '한미약품', '종근당', '일동제약', '동아에스티'
        ]
        
        # 산업별 키워드
        self.industry_keywords = {
            '조선': [
                '조선', '선박', '해양플랜트', 'LNG선', '컨테이너선',
                '수주', '발주', '인도', '건조', '한국조선해양', '삼성중공업',
                '대우조선해양', 'HD현대중공업', 'HD한국조선해양'
            ],
            '반도체': [
                '반도체', '칩', '웨이퍼', 'D램', '낸드', 'NAND', 'SSD',
                '파운드리', '삼성전자', 'SK하이닉스', '메모리', '시스템반도체',
                '반도체장비', '반도체소재'
            ],
            '철강': [
                '철강', '강판', '열연', '냉연', '후판', '스테인리스',
                '포스코', '현대제철', '동국제강', '고로', '제철소'
            ],
            '금융': [
                '은행', '증권', '보험', '자산운용', '카드', 'KB금융', '신한금융',
                '하나금융', '우리금융', '카카오뱅크', '토스', 'IPO', '상장',
                '대출', '예금', '펀드'
            ],
            '식품': [
                '식품', '음료', '유통', '라면', '과자', '음료수',
                '농심', 'CJ제일제당', '오뚜기', '롯데제과', '빙그레',
                '매일유업', '삼양식품', '신제품', '출시'
            ],
            '건설': [
                '건설', '아파트', '분양', '재개발', '재건축', '주택',
                '현대건설', 'GS건설', '대우건설', '대림산업', 'DL이앤씨',
                '수주', '착공', '입주'
            ],
            '바이오': [
                '바이오', '제약', '신약', '임상', '의약품', '백신',
                '셀트리온', '삼성바이오로직스', 'SK바이오팜', '유한양행',
                '승인', '허가', '개발', '기술이전'
            ]
        }
        
        # 산업별 고중요도 키워드
        self.industry_high_keywords = {
            '조선': ['수주', '발주', '인도', '계약', '실적', '매출', '투자'],
            '반도체': ['생산', '투자', '공급', '수요', '가격', '실적', '개발', '기술'],
            '철강': ['생산', '가격', '수출', '투자', '실적', '원료', '수요'],
            '금융': ['실적', '대출', '예금', '수익', '투자', '인수', '합병', '상장'],
            '식품': ['출시', '론칭', '매출', '수출', '브랜드', '인수', '투자'],
            '건설': ['수주', '분양', '개발', '투자', '매출', '해외', '프로젝트'],
            '바이오': ['승인', '허가', '임상', '개발', '투자', '수출', '계약', '기술이전']
        }
    
    def clean_html_tags(self, text: str) -> str:
        """HTML 태그 제거"""
        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(text)
        return text.strip()
    
    def parse_pub_date(self, pub_date: str) -> Optional[datetime]:
        """발행일 파싱"""
        try:
            return datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
        except:
            return None
    
    def is_recent_news(self, pub_date: str, hours: int = 48) -> bool:
        """최근 뉴스 여부 확인"""
        parsed_date = self.parse_pub_date(pub_date)
        if not parsed_date:
            return True
        
        now = datetime.now(parsed_date.tzinfo)
        return (now - parsed_date).total_seconds() <= hours * 3600
    
    def search_news_by_keyword(self, keyword: str, display: int = 20) -> List[Dict]:
        """키워드로 뉴스 검색"""
        params = {
            'query': keyword,
            'display': display,
            'sort': 'date'
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            news_list = []
            for item in data.get('items', []):
                if not self.is_recent_news(item.get('pubDate', '')):
                    continue
                
                news_list.append({
                    'title': self.clean_html_tags(item.get('title', '')),
                    'description': self.clean_html_tags(item.get('description', '')),
                    'link': item.get('link', ''),
                    'pub_date': item.get('pubDate', ''),
                    'keyword': keyword
                })
            
            return news_list
            
        except Exception as e:
            print(f"⚠️ 검색 실패 ({keyword}): {str(e)}")
            return []
    
    def calculate_industry_importance_score(self, news_item: Dict, industry: str) -> int:
        """산업별 중요도 점수 계산"""
        score = 5  # 기본 점수
        
        content = (news_item.get('title', '') + ' ' + news_item.get('description', '')).lower()
        
        # 산업별 고중요도 키워드
        high_keywords = self.industry_high_keywords.get(industry, [])
        for keyword in high_keywords:
            if keyword.lower() in content:
                score += 3
        
        # 대기업 키워드
        for company in self.major_companies:
            if company in content:
                score += 2
                break
        
        # 숫자 포함 (실적, 금액 등)
        if re.search(r'\d+', content):
            score += 1
        
        # 액션 키워드
        action_keywords = ['발표', '출시', '계약', '투자', '인수', '합병', '승인']
        for keyword in action_keywords:
            if keyword in content:
                score += 1
                break
        
        return score
    
    def select_top_news_for_industry(self, news_list: List[Dict], industry: str, top_n: int = 2) -> List[Dict]:
        """산업별 상위 뉴스 선별"""
        # 점수 계산
        for news in news_list:
            news['importance_score'] = self.calculate_industry_importance_score(news, industry)
            news['industry'] = industry
        
        # 중복 제거 (제목 앞 40자 기준)
        unique_news = {}
        for news in news_list:
            title_key = news['title'][:40]
            if title_key not in unique_news or news['importance_score'] > unique_news[title_key]['importance_score']:
                unique_news[title_key] = news
        
        # 점수 순 정렬
        sorted_news = sorted(unique_news.values(), key=lambda x: x['importance_score'], reverse=True)
        
        return sorted_news[:top_n]
    
    def collect_news_by_industry(self, news_per_industry: int = 2) -> List[Dict]:
        """
        산업별 뉴스 수집
        
        Args:
            news_per_industry: 산업당 수집할 뉴스 개수
        
        Returns:
            수집된 뉴스 리스트
        """
        all_news = []
        
        for industry, keywords in self.industry_keywords.items():
            print(f"\n🔍 [{industry}] 수집 중...")
            industry_news = []
            
            # 각 키워드로 검색
            for keyword in keywords[:5]:  # 상위 5개 키워드만
                news_list = self.search_news_by_keyword(keyword, display=10)
                industry_news.extend(news_list)
            
            if industry_news:
                # 상위 뉴스 선별
                top_news = self.select_top_news_for_industry(industry_news, industry, news_per_industry)
                all_news.extend(top_news)
                print(f"   ✅ {len(top_news)}개 선별 완료")
            else:
                print(f"   ⚠️ 뉴스 없음")
        
        return all_news

class NaverNewsFormatter:
    """뉴스 포맷터"""
    
    @staticmethod
    def format_daily_news(news_list: List[Dict]) -> str:
        """일간 뉴스 포맷팅 (카카오톡용)"""
        # 산업 이모지
        industry_emoji = {
            '조선': '🚢',
            '반도체': '💾',
            '철강': '🏭',
            '금융': '💰',
            '식품': '🍜',
            '건설': '🏗️',
            '바이오': '💊'
        }
        
        today = datetime.now().strftime('%m월 %d일')
        message = f"📰 산업뉴스 ({today})\n"
        message += "━" * 25 + "\n\n"
        
        for idx, news in enumerate(news_list[:10], 1):
            industry = news.get('industry', '기타')
            emoji = industry_emoji.get(industry, '📌')
            title = news.get('title', '제목없음')
            
            if len(title) > 35:
                title = title[:32] + "..."
            
            message += f"{emoji} {title}\n"
        
        message += "\n━" * 25 + "\n"
        message += "⏰ 매일 오전 8시 발송\n"
        message += f"📊 총 {len(news_list)}개 뉴스"
        
        return message

def test_collector():
    """테스트 실행"""
    print("\n" + "="*70)
    print("🧪 네이버 뉴스 수집기 테스트")
    print("="*70)
    
    collector = NaverNewsCollector()
    news_list = collector.collect_news_by_industry(news_per_industry=2)
    
    print(f"\n📊 총 수집: {len(news_list)}개")
    
    # 포맷팅
    message = NaverNewsFormatter.format_daily_news(news_list)
    print("\n" + "="*70)
    print("📝 카카오톡 메시지 미리보기:")
    print("="*70)
    print(message)
    print(f"\n메시지 길이: {len(message)}자")

if __name__ == "__main__":
    test_collector()
