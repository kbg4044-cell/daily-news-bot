"""
카카오톡 메시지 발송 시스템
- Refresh Token 자동 갱신
- PC 없이 완전 자동 실행
"""

import os
import requests
import json
from datetime import datetime
from typing import Optional

class KakaoTokenManager:
    """카카오 토큰 자동 관리"""
    
    def __init__(self):
        self.rest_api_key = os.getenv('KAKAO_REST_API_KEY')
        self.refresh_token = os.getenv('KAKAO_REFRESH_TOKEN')
        self.access_token = None
        
        if not self.rest_api_key or not self.refresh_token:
            raise ValueError(
                "❌ KAKAO_REST_API_KEY 또는 KAKAO_REFRESH_TOKEN이 설정되지 않았습니다!\n"
                "GitHub Secrets에 두 값을 모두 추가해주세요."
            )
    
    def get_access_token(self) -> str:
        """
        Refresh Token으로 새로운 액세스 토큰 발급
        
        Returns:
            액세스 토큰
        """
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.rest_api_key,
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            tokens = response.json()
            
            self.access_token = tokens['access_token']
            
            # 새로운 Refresh Token이 발급되면 알림
            if 'refresh_token' in tokens:
                print("🔄 새로운 Refresh Token 발급됨!")
                print(f"   새 토큰: {tokens['refresh_token'][:20]}...")
                print("   ⚠️ GitHub Secrets의 KAKAO_REFRESH_TOKEN을 업데이트하세요!")
            
            print("✅ 액세스 토큰 발급 성공!")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 토큰 발급 실패: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   응답: {e.response.text}")
            raise

class KakaoMessageSender:
    """카카오톡 나에게 메시지 발송"""
    
    def __init__(self, token_manager: KakaoTokenManager):
        self.token_manager = token_manager
        self.access_token = None
    
    def send_message_to_me(self, message: str) -> bool:
        """
        나에게 카카오톡 메시지 발송
        
        Args:
            message: 발송할 메시지 (최대 1000자)
        
        Returns:
            성공 여부
        """
        # 토큰 발급
        if not self.access_token:
            self.access_token = self.token_manager.get_access_token()
        
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # 메시지 길이 체크
        if len(message) > 1000:
            print(f"⚠️ 메시지가 너무 깁니다 ({len(message)}자). 1000자로 자릅니다.")
            message = message[:997] + "..."
        
        # 카카오톡 메시지 템플릿
        template = {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://github.com",
                "mobile_web_url": "https://github.com"
            }
        }
        
        data = {
            "template_object": json.dumps(template)
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            print("✅ 카카오톡 메시지 발송 성공!")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 메시지 발송 실패: {str(e)}")
            
            # 토큰 만료 시 재시도
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    print("🔄 토큰이 만료되었습니다. 재발급 시도...")
                    self.access_token = self.token_manager.get_access_token()
                    return self.send_message_to_me(message)  # 재시도
                
                print(f"   응답: {e.response.text}")
            
            return False

def test_kakao_sender():
    """테스트 실행"""
    print("\n" + "="*70)
    print("🧪 카카오톡 메시지 발송 테스트")
    print("="*70 + "\n")
    
    try:
        # 토큰 관리자 초기화
        token_manager = KakaoTokenManager()
        print("✅ 토큰 관리자 초기화 완료\n")
        
        # 메시지 발송자 초기화
        sender = KakaoMessageSender(token_manager)
        print("✅ 메시지 발송자 초기화 완료\n")
        
        # 테스트 메시지
        test_message = f"""
📰 산업뉴스봇 테스트

✅ 자동 토큰 갱신 시스템 작동!
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 PC 없이 매일 오전 8시
   GitHub Actions 자동 발송!

💡 설정 완료! 손댈 필요 없음.
""".strip()
        
        # 메시지 발송
        print("📤 메시지 발송 중...\n")
        success = sender.send_message_to_me(test_message)
        
        if success:
            print("\n" + "="*70)
            print("🎉 테스트 성공! 카카오톡 확인!")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("❌ 테스트 실패. 위 에러 확인.")
            print("="*70)
        
        return success
        
    except Exception as e:
        print(f"\n❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_kakao_sender()
