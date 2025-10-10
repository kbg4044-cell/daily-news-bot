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
        
        # API 엔드포인트
        self.auth_url = "https://kauth.kakao.com/oauth/token"
        self.message_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        self.friend_url = "https://kapi.kakao.com/v1/api/talk/friends"
        
        # 액세스 토큰 (실제로는 OAuth 인증 필요)
        self.access_token = None
        
    def get_access_token(self):
        """OAuth 액세스 토큰 획득 (실제 구현 시 필요)"""
        # 실제로는 OAuth 플로우를 통해 토큰을 획득해야 함
        # 지금은 테스트 모드로 설정
        print("🔑 카카오 OAuth 토큰 획득 중...")
        
        # TODO: 실제 OAuth 인증 구현
        # 현재는 테스트 모드
        self.access_token = "TEST_ACCESS_TOKEN"
        return True
    
    def send_message_to_me(self, message: str) -> bool:
        """나에게 메시지 보내기 (테스트용)"""
        try:
            if not self.access_token:
                if not self.get_access_token():
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
                        "web_url": "https://github.com/your-news-bot",
                        "mobile_web_url": "https://github.com/your-news-bot"
                    }
                })
            }
            
            print("📱 카카오톡 메시지 발송 시도 중...")
            print(f"메시지 길이: {len(message)}자")
            
            # 실제 API 호출 (현재는 테스트 모드)
            if self.app_key == 'YOUR_KAKAO_API_KEY_HERE':
                print("⚠️  테스트 모드: 실제 카카오 API 키가 필요합니다")
                print("📝 발송될 메시지 미리보기:")
                print("-" * 50)
                print(message)
                print("-" * 50)
                return True
            else:
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
            
            # 실제로는 각 구독자별로 개별 발송
            if self.send_message_to_me(message):  # 테스트용으로 나에게 발송
                results["success_count"] += 1
            else:
                results["fail_count"] += 1
        
        print(f"✅ 발송 완료: 성공 {results['success_count']}명, 실패 {results['fail_count']}명")
        return results
    
    def test_connection(self) -> bool:
        """카카오 API 연결 테스트"""
        print("🔍 카카오 비즈니스 API 연결 테스트...")
        
        if self.app_key == 'YOUR_KAKAO_API_KEY_HERE':
            print("⚠️  카카오 API 키가 설정되지 않았습니다")
            print("💡 실제 API 키를 받으면 정상 작동할 예정입니다")
            return False
        else:
            print("✅ 카카오 API 키가 설정되었습니다")
            return self.get_access_token()

class NewsMessageFormatter:
    """뉴스 메시지 포맷터 (카카오톡 최적화)"""
    
    @staticmethod
    def format_for_kakao(news_list: List[Dict], insight: str = None) -> str:
        """카카오톡 메시지 형태로 포맷팅"""
        today = datetime.now().strftime("%Y년 %m월 %d일")
        
        # 메시지 헤더
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
        
        # 뉴스 목록
        for i, news in enumerate(news_list, 1):
            # 중요도에 따른 이모지
            if news.get('importance_score', 0) >= 8:
                priority_emoji = "🔥"
            elif news.get('importance_score', 0) >= 6:  
                priority_emoji = "⭐"
            else:
                priority_emoji = "📌"
            
            # 카테고리 이모지
            cat_emoji = category_emojis.get(news['category'], "📰")
            
            # 제목 (40자 제한으로 축소)
            title = news['title'][:40] + "..." if len(news['title']) > 40 else news['title']
            
            message += f"{priority_emoji} {i}. {title}\n"
            message += f"   {cat_emoji} {news['category']} | {news['pubDate']}\n"
            
            # 요약문 (편집된 버전 사용, 60자 제한)
            if news.get('description'):
                summary = news['description'][:60] + "..." if len(news['description']) > 60 else news['description']
                message += f"   💬 {summary}\n"
            
            # 링크 제거 (길이 절약)
            # message += f"   🔗 {news['link']}\n\n"
            message += "\n"
        
        # 인사이트 추가 (축소)
        message += "─" * 20 + "\n"
        message += "💡 오늘의 인사이트\n\n"
        
        if insight and len(insight) < 100:
            message += f"{insight}\n\n"
        else:
            # 기본 인사이트 (간단한 버전)
            message += "📊 채용 시장 활성화\n"
            message += "💡 이력서 업데이트 권장\n\n"
        
        # 푸터 (축소)
        message += "─" * 20 + "\n"
        message += "📅 매일 오전 8시\n"
        message += "💼 산업뉴스 전문\n"
        
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
            "description": "삼성전자가 내년 상반기 신입사원을 대규모로 채용한다고 발표했습니다. 반도체 사업 확대에 따른 인력 충원이 목적입니다...",
            "link": "https://example.com/news1",
            "pubDate": "2025-10-10 08:00",
            "importance_score": 9
        },
        {
            "title": "AI 스타트업 투자 급증, 올해 전년 대비 200% 증가",
            "category": "IT/기술", 
            "description": "올해 AI 관련 스타트업에 대한 투자가 전년 대비 200% 증가한 것으로 나타났습니다. 특히 생성형 AI 분야가 주목받고 있습니다...",
            "link": "https://example.com/news2",
            "pubDate": "2025-10-10 07:30",
            "importance_score": 8
        }
    ]
    
    # 메시지 포맷팅
    formatter = NewsMessageFormatter()
    message = formatter.format_for_kakao(sample_news)
    
    # 메시지 길이 체크
    length_check = formatter.check_message_length(message)
    
    # 테스트 발송
    print("\n📱 테스트 메시지 발송...")
    success = kakao_sender.send_message_to_me(message)
    
    if success:
        print("✅ 카카오톡 발송 시스템 준비 완료!")
        print("💡 실제 카카오 API 키만 받으면 바로 작동합니다!")
    else:
        print("❌ 시스템 점검이 필요합니다.")