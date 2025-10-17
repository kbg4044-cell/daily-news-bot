#!/usr/bin/env python3
"""
카카오 Access Token 발급 - 최종 버전
"""

import requests
import json

REST_API_KEY = "53066b9b217b7a74302bb3624e1c631f"
AUTH_CODE = "VqAKtW-V9Qh7njTqgzbxU0cydD45WCSIxLhj9hZagGIWk0OtaBQ8VAAAAAQKFwvXAAABmfFDqIQp9hBbJybEWQ"

print("🔄 Access Token 발급 중...")
print("=" * 60)

token_url = "https://kauth.kakao.com/oauth/token"
data = {
    "grant_type": "authorization_code",
    "client_id": REST_API_KEY,
    "redirect_uri": "https://localhost",
    "code": AUTH_CODE
}

try:
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        
        print("\n✅ Access Token 발급 성공!")
        print("=" * 60)
        print("\n📋 GitHub Secrets에 등록할 값:\n")
        
        print("1. KAKAO_API_KEY")
        print(f"   {REST_API_KEY}\n")
        
        print("2. KAKAO_ACCESS_TOKEN")
        print(f"   {tokens['access_token']}\n")
        
        if 'refresh_token' in tokens:
            print("3. KAKAO_REFRESH_TOKEN (선택)")
            print(f"   {tokens['refresh_token']}\n")
        
        print("=" * 60)
        print("\n💡 유효기간:")
        if 'expires_in' in tokens:
            hours = tokens['expires_in'] / 3600
            print(f"   Access Token: {hours:.1f}시간")
        if 'refresh_token_expires_in' in tokens:
            days = tokens['refresh_token_expires_in'] / 86400
            print(f"   Refresh Token: {days:.0f}일")
        
        # 테스트 발송
        print("\n📱 테스트 메시지를 발송해볼까요? (y/n): ", end="")
        test = input().strip().lower()
        
        if test == 'y':
            print("\n발송 중...")
            
            headers = {
                "Authorization": f"Bearer {tokens['access_token']}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            template = {
                "object_type": "text",
                "text": "🎉 Daily News Bot 연동 성공!\n\n카카오톡 메시지 발송이 정상 작동합니다.\n\n이제 GitHub Actions를 실행하면 자동으로 뉴스가 발송됩니다!",
                "link": {
                    "web_url": "https://github.com",
                    "mobile_web_url": "https://github.com"
                }
            }
            
            msg_data = {
                "template_object": json.dumps(template, ensure_ascii=False)
            }
            
            msg_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
            test_resp = requests.post(msg_url, headers=headers, data=msg_data)
            
            if test_resp.status_code == 200:
                print("✅ 카카오톡을 확인하세요! 메시지가 도착했을 겁니다!")
            else:
                print(f"❌ 발송 실패: {test_resp.status_code}")
                print(test_resp.text)
        
        print("\n" + "=" * 60)
        print("🎯 다음 단계:")
        print("1. GitHub Repository → Settings → Secrets")
        print("2. KAKAO_API_KEY 수정 (위 값 복사)")
        print("3. KAKAO_ACCESS_TOKEN 새로 추가 (위 값 복사)")
        print("4. GitHub Actions 실행!")
        print("=" * 60)
        
    else:
        print(f"\n❌ 토큰 발급 실패: {response.status_code}")
        print(f"응답: {response.text}")
        
        if "invalid_grant" in response.text:
            print("\n💡 인증 코드가 만료되었습니다!")
            print("   다시 아래 URL을 열어서 새 코드를 받으세요:")
            print(f"   https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri=https://localhost&response_type=code")
        
except Exception as e:
    print(f"\n❌ 오류: {str(e)}")
    print("\n💡 requests 라이브러리 설치:")
    print("   pip install requests")
