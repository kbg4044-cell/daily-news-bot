#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini AI 뉴스 편집기 - 채용포인트 생성
"""

import google.generativeai as genai
from typing import List, Dict
import time

class GeminiNewsEditor:
    """Gemini AI를 사용한 뉴스 편집 및 채용포인트 생성"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def format_news_with_recruitment_point(self, news_list: List[Dict]) -> List[Dict]:
        """
        각 뉴스에 채용포인트 추가
        
        Args:
            news_list: 원본 뉴스 리스트
            
        Returns:
            채용포인트가 추가된 뉴스 리스트
        """
        
        formatted_news = []
        
        for i, news in enumerate(news_list, 1):
            try:
                print(f"  [{i}/{len(news_list)}] AI 분석 중...", end=" ")
                
                # 채용포인트 생성
                recruitment_point = self._generate_recruitment_point(news)
                
                # 원본 데이터에 채용포인트 추가
                formatted = {
                    'title': self._clean_html(news.get('title', '')),
                    'link': news.get('link', ''),
                    'description': self._clean_html(news.get('description', '')),
                    'pubDate': news.get('pubDate', ''),
                    'recruitment_point': recruitment_point
                }
                
                formatted_news.append(formatted)
                print("✓")
                
                # API 호출 제한 대응 (0.5초 대기)
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ 오류: {e}")
                # 실패 시 원본 데이터 사용 (채용포인트 없음)
                formatted_news.append({
                    'title': self._clean_html(news.get('title', '')),
                    'link': news.get('link', ''),
                    'description': self._clean_html(news.get('description', '')),
                    'pubDate': news.get('pubDate', ''),
                    'recruitment_point': ''
                })
        
        return formatted_news
    
    def _generate_recruitment_point(self, news: Dict) -> str:
        """
        뉴스 내용을 분석해 채용포인트 생성
        
        Returns:
            한 줄 채용포인트 (30자 이내)
        """
        
        title = self._clean_html(news.get('title', ''))
        description = self._clean_html(news.get('description', ''))
        
        prompt = f"""
다음 뉴스를 분석하여 채용/고용 관점에서 핵심 포인트를 한 줄로 요약하세요.

뉴스 제목: {title}
뉴스 내용: {description}

요구사항:
1. 채용/고용과 직접 관련된 인사이트 제공
2. 30자 이내로 작성
3. "~예상", "~전망" 등의 표현 사용
4. 구체적인 숫자가 있으면 포함

예시:
- "대규모 수주로 신규 인력 채용 예상"
- "실적 호조로 하반기 채용 규모 확대 전망"
- "디지털 전환으로 IT 인력 수요 증가"

채용포인트:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 100,
                }
            )
            
            point = response.text.strip()
            
            # 길이 제한
            if len(point) > 40:
                point = point[:37] + "..."
            
            return point
            
        except Exception as e:
            print(f"AI 생성 실패: {e}")
            return ""
    
    def _clean_html(self, text: str) -> str:
        """HTML 태그 및 특수문자 제거"""
        
        import re
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # HTML 엔티티 변환
        text = text.replace('&quot;', '"')
        text = text.replace('&apos;', "'")
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ')
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
