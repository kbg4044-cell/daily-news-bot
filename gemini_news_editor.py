import requests
import json
from typing import List, Dict
import time
from datetime import datetime
from naver_news_collector import NaverNewsCollector

class GeminiNewsEditor:
    """Google Gemini API를 활용한 뉴스 편집기"""
    
    def __init__(self, api_key: str = None):
        # Google Gemini API 설정
        self.api_key = api_key or "YOUR_GEMINI_API_KEY"  # 실제 API 키로 교체 필요
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # 뉴스 편집용 프롬프트 템플릿 (극도로 간소화)
        self.edit_prompt_template = """
{description}

70자 요약:
"""

        # 인사이트 생성용 프롬프트 (간소화)
        self.insight_prompt_template = """
오늘 뉴스 요약:
{news_summary}

위 내용을 2줄로 요약해주세요:
📊 [핵심 트렌드]
💡 [실용 조언]
"""

        # 제미나이 특화 설정
        self.generation_config = {
            "temperature": 0.3,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 100,
        }

    def edit_news_summary(self, news_item: Dict) -> str:
        """Gemini로 뉴스 요약문 재편집"""
        try:
            # 프롬프트 생성
            prompt = self.edit_prompt_template.format(
                title=news_item['title'],
                category=news_item['category'],
                description=news_item['description']
            )
            
            # Gemini API 호출
            response = self.call_gemini_api(prompt)
            
            if response:
                # 편집된 요약문 정리
                edited_summary = response.strip()
                # 불필요한 텍스트 제거
                edited_summary = edited_summary.replace("편집된 요약문:", "").strip()
                edited_summary = edited_summary.replace("편집된 요약:", "").strip()
                
                return edited_summary[:70] + "..." if len(edited_summary) > 70 else edited_summary
            else:
                # API 실패 시 원본 요약문 사용 (70자 제한)
                original = news_item['description']
                return original[:70] + "..." if len(original) > 70 else original
                
        except Exception as e:
            print(f"Gemini 편집 중 오류: {str(e)}")
            # 오류 발생 시 원본 사용
            original = news_item['description']
            return original[:70] + "..." if len(original) > 70 else original
    
    def generate_daily_insight(self, news_list: List[Dict]) -> str:
        """Gemini로 일간 인사이트 생성"""
        try:
            # 뉴스 요약 생성
            news_summary = ""
            for i, news in enumerate(news_list, 1):
                news_summary += f"{i}. [{news['category']}] {news['title'][:40]}...\n"
            
            # 프롬프트 생성
            prompt = self.insight_prompt_template.format(news_summary=news_summary)
            
            # Gemini API 호출
            response = self.call_gemini_api(prompt)
            
            if response:
                return response.strip()
            else:
                # 기본 인사이트 반환
                return self.get_default_insight(news_list)
                
        except Exception as e:
            print(f"인사이트 생성 중 오류: {str(e)}")
            return self.get_default_insight(news_list)
    
    def call_gemini_api(self, prompt: str) -> str:
        """Google Gemini API 호출"""
        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": self.generation_config
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    candidate = data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        content = candidate['content']['parts'][0]['text']
                        return content
                    else:
                        print(f"Gemini API 응답 구조 오류: {data}")
                        return None
                else:
                    print(f"Gemini API 응답에 candidates가 없습니다: {data}")
                    return None
            else:
                print(f"Gemini API 오류: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Gemini API 호출 중 오류: {str(e)}")
            return None
    
    def get_default_insight(self, news_list: List[Dict]) -> str:
        """Gemini 실패 시 기본 인사이트"""
        categories = [news['category'] for news in news_list]
        most_frequent = max(set(categories), key=categories.count) if categories else "일반"
        
        default_insights = {
            "취업/고용": "📊 채용 시장 활성화 신호 감지\n💡 이력서 업데이트하고 기회 탐색하세요",
            "기업동향": "📊 기업 실적 시즌 본격화\n💡 관심 기업 동향 면밀히 모니터링하세요",
            "IT/기술": "📊 기술 혁신 가속화 트렌드\n💡 새로운 스킬 학습으로 경쟁력 확보하세요",
            "제조/산업": "📊 제조업 구조 변화 진행 중\n💡 공급망 다변화 동향 주의깊게 관찰하세요",
            "부동산/건설": "📊 부동산 정책 변화 예고\n💡 시장 동향 분석으로 투자 전략 재점검하세요"
        }
        
        return default_insights.get(most_frequent, "📊 산업 전반 변화 가속화\n💡 트렌드 변화에 민첩하게 대응하세요")

class GeminiEnhancedNewsService:
    """Gemini 편집 기능이 추가된 뉴스 서비스"""
    
    def __init__(self, gemini_api_key: str = None):
        self.naver_collector = NaverNewsCollector()
        self.gemini_editor = GeminiNewsEditor(gemini_api_key)
        
    def collect_and_edit_news(self, news_count: int = 5) -> List[Dict]:
        """뉴스 수집 및 Gemini 편집"""
        print("🚀 네이버 API로 뉴스 수집 + Gemini 편집 시작...")
        
        # 1. 네이버 API로 뉴스 수집
        all_news = self.naver_collector.collect_all_news(news_per_keyword=2)
        
        if not all_news:
            print("❌ 뉴스 수집 실패")
            return []
        
        # 2. 상위 뉴스 선별
        top_news = self.naver_collector.filter_and_rank_news(all_news, news_count)
        
        print(f"🤖 Gemini로 {len(top_news)}개 뉴스 편집 시작...")
        
        # 3. Gemini로 각 뉴스 편집
        edited_news = []
        for i, news in enumerate(top_news, 1):
            print(f"  ✏️  {i}/{len(top_news)} 편집 중: {news['title'][:30]}...")
            
            # Gemini로 요약문 재편집
            edited_summary = self.gemini_editor.edit_news_summary(news)
            
            # 편집된 내용으로 업데이트
            news['original_description'] = news['description']  # 원본 저장
            news['description'] = edited_summary  # 편집본으로 교체
            news['edited_by'] = 'Gemini'  # 편집 정보 추가
            
            edited_news.append(news)
            
            # API 호출 제한을 위한 대기 (Gemini는 비교적 관대함)
            time.sleep(0.3)
        
        print("✅ Gemini 편집 완료!")
        return edited_news
    
    def create_enhanced_message(self, edited_news: List[Dict]) -> str:
        """Gemini 편집된 뉴스로 향상된 메시지 생성"""
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
        
        for i, news in enumerate(edited_news, 1):
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
            message += f"   💬 {news['description']}\n"  # Gemini 편집된 요약문
            message += f"   🔗 {news['link']}\n\n"
        
        # Gemini 생성 인사이트 추가
        message += "─" * 28 + "\n"
        message += "💡 오늘의 산업 인사이트\n\n"
        
        print("🤖 Gemini로 일간 인사이트 생성 중...")
        insight = self.gemini_editor.generate_daily_insight(edited_news)
        message += f"{insight}\n\n"
        
        message += "─" * 28 + "\n"
        message += "📅 매일 오전 8시 발송\n"
        message += "💼 산업·취업·기업 정보 전문\n"
        message += "📞 문의: 비즈니스 채널 채팅"
        
        return message

# 테스트 함수 (Gemini API 키 없이도 테스트 가능)
def test_gemini_news_service():
    """Gemini 뉴스 서비스 테스트 (시뮬레이션)"""
    print("🧪 Gemini 뉴스 편집 서비스 테스트 (시뮬레이션 모드)")
    print("=" * 60)
    
    # Gemini API 키 없이 테스트 (시뮬레이션 모드)
    service = GeminiEnhancedNewsService()
    
    # 1. 네이버 뉴스 수집
    all_news = service.naver_collector.collect_all_news(news_per_keyword=2)
    
    if not all_news:
        print("❌ 뉴스 수집 실패")
        return
    
    # 2. 상위 5개 선별
    top_news = service.naver_collector.filter_and_rank_news(all_news, 5)
    
    # 3. Gemini 편집 시뮬레이션
    print("🤖 Gemini 편집 시뮬레이션...")
    for i, news in enumerate(top_news, 1):
        print(f"  ✏️  {i}/5 시뮬레이션 편집: {news['title'][:30]}...")
        
        # 시뮬레이션: 더 읽기 쉽게 요약문 다듬기
        original = news['description']
        news['original_description'] = original
        
        # 간단한 편집 시뮬레이션 (실제로는 Gemini가 수행)
        if len(original) > 70:
            news['description'] = original[:65] + "..."
        news['edited_by'] = 'Simulation'
    
    # 4. 향상된 메시지 생성
    message = service.create_enhanced_message(top_news)
    
    print("📱 Gemini 편집 메시지 생성 완료!")
    print("=" * 60)
    print(message)
    print("=" * 60)
    
    # 5. 편집 비교 결과 출력
    print("\n📝 편집 비교 (첫 번째 뉴스)")
    print(f"원본: {top_news[0]['original_description'][:50]}...")
    print(f"편집: {top_news[0]['description']}")
    
    # 6. 결과 저장
    with open('/home/user/gemini_news_data.json', 'w', encoding='utf-8') as f:
        json.dump(top_news, f, ensure_ascii=False, indent=2)
    
    print("\n💾 Gemini 편집 뉴스 데이터가 gemini_news_data.json에 저장되었습니다.")
    
    return message, top_news

if __name__ == "__main__":
    test_gemini_news_service()