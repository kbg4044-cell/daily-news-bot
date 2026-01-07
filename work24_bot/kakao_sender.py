#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카카오톡 발송 시스템
"""

import requests
import json

class KakaoSender:
    """카카오톡 나에게 보내기"""
    
    def __init__(self, rest_api_key: str, refresh_token: str):
        self.rest_api_key = rest_api_key
        self.refresh_token = refresh_token
        self.access_token = None
        
        self.token_url = "https://kauth.kakao.com/oauth/token"
        self.message_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    def send_message(self, message: str) -> bool:
        """메시지 발송"""
        
        if not self._refresh_access_token():
            print("❌ 액세스 토큰 발급 실패")
            return False
        
        print(f"✓ 액세스 토큰 발급 성공")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "template_object": json.dumps({
                    "object_type": "text",
                    "text": message,
                    "link": {
                        "web_url": "https://www.work24.go.kr",
                        "mobile_web_url": "https://www.work24.go.kr"
                    }
                })
            }
            
            response = requests.post(
                self.message_url,
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ 카카오톡 발송 성공")
                return True
            else:
                print(f"❌ 발송 실패: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ 발송 오류: {e}")
            return False
    
    def _refresh_access_token(self) -> bool:
        """액세스 토큰 발급"""
        
        try:
            data = {
                "grant_type": "refresh_token",
                "client_id": self.rest_api_key,
                "refresh_token": self.refresh_token
            }
            
            response = requests.post(
                self.token_url,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                
                new_refresh_token = token_data.get('refresh_token')
                if new_refresh_token:
                    self.refresh_token = new_refresh_token
                
                return True
            else:
                print(f"❌ 토큰 발급 실패: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ 토큰 발급 오류: {e}")
            return False
