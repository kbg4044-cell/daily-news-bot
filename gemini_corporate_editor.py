#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기업뉴스 AI 편집기
"""

import google.generativeai as genai
from typing import List, Dict
import re

class GeminiCorporateEditor:
    """Gemini AI 기업뉴스 편집기"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def format_corporate_news(self, categorized_news: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """기업뉴스 포맷팅"""
        
        formatted = {}
        
        for industry, news_list in categorized_news.items():
            formatted[industry] = []
            
            for news in news_list:
                formatted_item = {
                    'title': self._clean_html(news.get('title', '')),
                    'link': news.get('link', ''),
                    'description': self._clean_html(news.get('description', '')),
                    'pubDate': news.get('pubDate', '')
                }
                
                formatted[industry].append(formatted_item)
        
        return formatted
    
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
