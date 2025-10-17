import requests
import json
import os
from typing import List, Dict
from datetime import datetime

class KakaoBusinessSender:
    """카카오 비즈니스 메시지 발송 시스템"""
    
    def __init__(self, app_key: str = None):
        # 카카오 비즈니스 API 설정
        self.app_key = app_key or os.getenv('KAKAO_API_KEY', 'YOUR_KAKAO_API_KEY_HERE')
        
        # Access Token (환경 변수에서 읽기)
        self.access_token = os.getenv('KAKAO_ACCESS_TOKEN', None)
        
        # API 엔드포인트
        self.auth_url = "https://kauth.kakao.com/oauth/token"
        self.message_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        self.friend_url = "https://kapi.kakao.com/v1/api/talk/friends"
        
    def get_access_token(self):
        """OAuth 액세스 토큰 획득"""
        # 환경 변수에서 Access Token 사용
        if self.access_token:
            print("✅ Access Token이 환경 변수에서 로드되었습니다")
            return True
        else:
            print("⚠️ Access Token이 설정되지 않았습니다")
            return False
    
    def send_message_to_me(self, message: str) -> bool:
        """나에게 메시지 보내기"""
        try:
            if not self.access_token:
                if not self.get_access_token():
                    print("❌ Access Token이 없습니다")
                    return False
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "template_object": json.dumps({
                    "object_type": "text",
                    "text": message,
                    "link": {
                        "web_url": "https://github.com",
                        "mobile_web_url": "https://github.com"
                    }
                }, ensure_ascii=False)
            }
            
            print("📱 카카오톡 메시지 발송 시도 중...")
            print(f"메시지 길이: {len(message)}자")
            
            # 실제 API 호출
            response = requests.post(self.message_url, headers=headers, data=data)
            
            if response.status_code == 200:
                print("✅ 카카오톡 메시지 발송 성공!")
                return True
            else:
                print(f"❌ 카카오톡 메시지 발송 실패: {response.status_code}")
                print(f"응답: {response.text}")
                return False
                    
        except Exception as e:
            print(f"카카오톡 발송 중 오류: {str(e)}")
            return False
    
    def send_to_subscribers(self, message: str, subscriber_list: List[str] = None) -> Dict:
        """구독자들에게 메시지 발송"""
        results = {
            "success_count": 0,
            "fail_count": 0,
            "total_count": 0
        }
        
        # 테스트 모드에서는 구독자 목록 시뮬레이션
        if not subscriber_list:
            subscriber_list = ["test_user_1", "test_user_2", "test_user_3"]
        
        results["total_count"] = len(subscriber_list)
        
        print(f"📢 {len(subscriber_list)}명의 구독자에게 메시지 발송 시작...")
        
        for i, subscriber in enumerate(subscriber_list, 1):
            print(f"  📱 {i}/{len(subscriber_list)} 발송 중: {subscriber}")
            
            # 실제로는 나에게 발송 (테스트용)
            if self.send_message_to_me(message):
                results["success_count"] += 1
            else:
                results["fail_count"] += 1
        
        print(f"✅ 발송 완료: 성공 {results['success_count']}명, 실패 {results['fail_count']}명")
        return results
    
    def test_connection(self) -> bool:
        """카카오 API 연결 테스트"""
        print("🔍 카카오 비즈니스 API 연결 테스트...")
        
        if self.app_key == 'YOUR_KAKAO_API_KEY_HERE':
            print("⚠️ 카카오 API 키가 설정되지 않았습니다")
            return False
        else:
            print("✅ 카카오 API 키가 설정되었습니다")
        
        if not self.access_token:
            print("⚠️ Access Token이 설정되지 않았습니다")
            print("💡 GitHub Secrets에 KAKAO_ACCESS_TOKEN을 등록하세요")
            return False
        else:
            print(f"✅ Access Token이 설정되었습니다: {self.access_token[:20]}...")
            return True

class NewsMessageFormatter:
    """뉴스 메시지 포맷터 (카카오톡 최적화)"""
    
    @staticmethod
    def format_for_kakao(news_list: List[Dict], insight: str = None) -> str:
        """카카오톡 메시지 형태로 포맷팅 (길이 제한 강화)"""
        
        # 🔧 안전장치 1: 5개 초과 시 강제로 자르기
        if len(news_list) > 5:
            print(f"⚠️ 뉴스 {len(news_list)}개 감지 → 5개로 강제 제한")
            news_list = news_list[:5]
        
        today = datetime.now().strftime("%m월 %d일")  # 간소화
        
        # 메시지 헤더 (더 짧게)
        message = f"🏭 {today} 산업뉴스\n"
        message += "=" * 20 + "\n\n"
        
        # 카테고리별 이모지
        category_emojis = {
            "취업/고용": "👔", "기업동향": "🏢", "IT/기술": "💻",
            "제조/산업": "🏭", "부동산/건설": "🏗️", "조선": "🚢",
            "반도체": "💾", "철강": "⚙️", "금융": "💰",
            "식품": "🍜", "건설": "🏗️", "바이오": "🧬"
        }
        
        # 뉴스 목록 (매우 간결하게)
        for i, news in enumerate(news_list, 1):
            # 중요도 이모지
            if news.get('importance_score', 0) >= 8:
                priority_emoji = "🔥"
            elif news.get('importance_score', 0) >= 6:  
                priority_emoji = "⭐"
            else:
                priority_emoji = "📌"
            
            # 카테고리 이모지
            cat_emoji = category_emojis.get(news['category'], "📰")
            
            # 제목 (30자로 축소)
            title = news['title'][:30] + "..." if len(news['title']) > 30 else news['title']
            
            message += f"{priority_emoji} {title}\n"
            message += f"{cat_emoji} {news['category']}\n"
            
            # 요약문 (45자로 축소)
            if news.get('description'):
                summary = news['description'][:45] + "..." if len(news['description']) > 45 else news['description']
                message += f"{summary}\n"
            
            message += "\n"
        
        # 인사이트 (매우 간결하게)
        message += "─" * 15 + "\n"
        message += "💡 인사이트\n"
        
        if insight and len(insight) < 80:
            # 인사이트도 80자로 제한
            message += f"{insight[:80]}\n"
        else:
            message += "산업 트렌드 주목\n"
        
        message += "\n📅 매일 오전 8시"
        
        # 🔧 안전장치 2: 최종 길이 체크 (950자로 제한)
        if len(message) > 950:
            print(f"⚠️ 메시지 {len(message)}자 → 950자로 강제 축소")
            message = message[:947] + "..."
        
        return message
    
    @staticmethod
    def check_message_length(message: str) -> Dict:
        """카카오톡 메시지 길이 체크"""
        max_length = 1000  # 카카오톡 메시지 최대 길이
        
        result = {
            "length": len(message),
            "max_length": max_length,
            "is_valid": len(message) <= max_length,
            "overflow": max(0, len(message) - max_length)
        }
        
        if not result["is_valid"]:
            print(f"⚠️  메시지가 너무 깁니다: {result['length']}/{max_length}자")
            print(f"   초과: {result['overflow']}자")
        else:
            print(f"✅ 메시지 길이 적정: {result['length']}/{max_length}자")
        
        return result

# 테스트 코드
if __name__ == "__main__":
    print("🧪 카카오 비즈니스 발송 시스템 테스트\n")
    
    # 카카오 발송 시스템 초기화
    kakao_sender = KakaoBusinessSender()
    
    # 연결 테스트
    kakao_sender.test_connection()
    
    # 샘플 뉴스 데이터
    sample_news = [
        {
            "title": "삼성전자, 2025년 신입사원 대규모 채용 발표",
            "category": "취업/고용",
            "description": "삼성전자가 내년 상반기 신입사원을 대규모로 채용한다고 발표했습니다.",
            "link": "https://example.com/news1",
            "pubDate": "10-14 08:00",
            "importance_score": 9
        },
        {
            "title": "AI 스타트업 투자 급증, 올해 전년 대비 200% 증가",
            "category": "IT/기술", 
            "description": "올해 AI 관련 스타트업에 대한 투자가 전년 대비 200% 증가했습니다.",
            "link": "https://example.com/news2",
            "pubDate": "10-14 07:30",
            "importance_score": 8
        }
    ]
    
    # 메시지 포맷팅
    formatter = NewsMessageFormatter()
    message = formatter.format_for_kakao(sample_news)
    
    # 메시지 길이 체크
    length_check = formatter.check_message_length(message)
    
    # 메시지 미리보기
    print("\n📱 생성된 메시지:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    print("\n✅ 카카오톡 발송 시스템 준비 완료!")
    print("💡 실제 발송을 위해서는 GitHub Secrets에 다음을 등록하세요:")
    print("   - KAKAO_API_KEY: REST API 키")
    print("   - KAKAO_ACCESS_TOKEN: OAuth Access Token")
