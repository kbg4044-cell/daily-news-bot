#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용뉴스 AI 편집기
"""

import google.generativeai as genai
from typing import List, Dict
import time
import re

class GeminiEmploymentEditor:
    """Gemini AI 고용뉴스 편집기"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def format_news_with_recruitment_point(self, news_list: List[Dict]) -> List[Dict]:
        """채용포인트 생성"""
        
        formatted_news = []
        
        for i, news in enumerate(news_list, 1):
            try:
                print(f"  [{i}/{len(news_list)}] AI 분석...", end=" ")
                
                recruitment_point = self._generate_recruitment_point(news)
                
                formatted = {
                    'title': self._clean_html(news.get('title', '')),
                    'link': news.get('link', ''),
                    'description': self._clean_html(news.get('description', '')),
                    'pubDate': news.get('pubDate', ''),
                    'recruitment_point': recruitment_point
                }
                
                formatted_news.append(formatted)
                print("✓")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ {e}")
                formatted_news.append({
                    'title': self._clean_html(news.get('title', '')),
                    'link': news.get('link', ''),
                    'description': self._clean_html(news.get('description', '')),
                    'pubDate': news.get('pubDate', ''),
                    'recruitment_point': ''
                })
        
        return formatted_news
    
    def _generate_recruitment_point(self, news: Dict) -> str:
        """채용포인트 생성"""
        
        title = self._clean_html(news.get('title', ''))
        description = self._clean_html(news.get('description', ''))
        
        prompt = f"""
다음 채용/고용 뉴스를 분석하여 구직자 관점에서 핵심 포인트를 한 줄로 요약하세요.

제목: {title}
내용: {description}

요구사항:
1. 30자 이내로 작성
2. 채용 규모, 직무, 시기 등 구체적 정보 포함
3. "~예상", "~전망", "~진행" 등의 표현 사용

예시:
- "상반기 신입사원 200명 채용 예정"
- "디지털 전환으로 개발자 수요 급증"
- "공장 증설로 생산직 대규모 채용"

채용포인트:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 80,
                }
            )
            
            point = response.text.strip()
            
            if len(point) > 35:
                point = point[:32] + "..."
            
            return point
            
        except Exception as e:
            return ""
    
    def _clean_html(self, text: str) -> str:
        """HTML 정리"""
        
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&quot;', '"')
        text = text.replace('&apos;', "'")
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
