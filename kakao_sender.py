#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카카오톡 메시지 발송 시스템 (자동 토큰 갱신)
"""

import requests
import json
from typing import Optional

class KakaoSender:
    """카카오톡 나에게 보내기 + 자동 토큰 갱신"""
    
    def __init__(self, rest_api_key: str, refresh_token: str):
        self.rest_api_key = rest_api_key
        self.refresh_token = refresh_token
        self.access_token = None
        
        # 토큰 엔드포인트
        self.token_url = "https://kauth.kakao.com/oauth/token"
        self.message_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    def send_message(self, message: str) -> bool:
        """
        카카오톡 메시지 발송
        
        Args:
            message: 발송할 메시지 내용
            
        Returns:
            성공 여부
        """
        
        # 1. 액세스 토큰 발급/갱신
        if not self._refresh_access_token():
            print("❌ 액세스 토큰 발급 실패")
            return False
        
        print(f"✓ 액세스 토큰 발급 성공")
        
        # 2. 메시지 발송
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
                        "web_url": "https://www.naver.com",
                        "mobile_web_url": "https://www.naver.com"
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
                error_data = response.json()
                print(f"❌ 발송 실패: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ 발송 오류: {e}")
            return False
    
    def _refresh_access_token(self) -> bool:
        """Refresh Token으로 새 Access Token 발급"""
        
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
                
                # Refresh Token도 갱신되었다면 업데이트
                new_refresh_token = token_data.get('refresh_token')
                if new_refresh_token:
                    self.refresh_token = new_refresh_token
                    print("✓ Refresh Token도 갱신됨")
                
                return True
            else:
                error_data = response.json()
                print(f"❌ 토큰 발급 실패: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ 토큰 발급 오류: {e}")
            return False
