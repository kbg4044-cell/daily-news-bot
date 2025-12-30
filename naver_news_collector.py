#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 뉴스 수집기 - 고용/채용/취업 전문
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict

class NaverNewsCollector:
    """네이버 뉴스 API를 사용한 고용/채용 뉴스 수집기"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        # 고용/채용/취업 관련 키워드
        self.employment_keywords = [
            '채용', '신입사원', '경력직', '구인', '일자리',
            '취업', '고용', '인력', '직원모집', '리크루팅',
            '채용공고', '입사', '면접', '인재채용', '대규모채용',
            '청년채용', '공채', '수시채용', '헤드헌팅', '이직'
        ]
    
    def collect_employment_news(self, count: int = 20) -> List[Dict]:
        """
        고용/채용 관련 뉴스 수집
        
        Args:
            count: 수집할 뉴스 개수 (기본 20개)
            
        Returns:
            뉴스 리스트 (최신순)
        """
        
        all_news = []
        
        # 여러 키워드로 검색
        main_keywords = ['채용', '고용', '취업', '일자리', '신입사원']
        
        for keyword in main_keywords:
            try:
                news = self._search_news(keyword, display=10)
                all_news.extend(news)
            except Exception as e:
                print(f"⚠️ '{keyword}' 검색 실패: {e}")
                continue
        
        # 중복 제거 (링크 기준)
        unique_news = self._remove_duplicates(all_news)
        
        # 최신순 정렬
        sorted_news = sorted(
            unique_news,
            key=lambda x: x.get('pubDate', ''),
            reverse=True
        )
        
        # 날짜 필터링 (최근 3일 이내)
        filtered_news = self._filter_by_date(sorted_news, days=3)
        
        # 관련도 점수 계산 및 정렬
        scored_news = self._calculate_relevance_score(filtered_news)
        
        return scored_news[:count]
    
    def _search_news(self, query: str, display: int = 10) -> List[Dict]:
        """네이버 뉴스 API 검색"""
        
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        params = {
            'query': query,
            'display': display,
            'sort': 'date'  # 최신순
        }
        
        response = requests.get(
            self.base_url,
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        else:
            raise Exception(f"API 오류: {response.status_code}")
    
    def _remove_duplicates(self, news_list: List[Dict]) -> List[Dict]:
        """중복 뉴스 제거 (링크 기준)"""
        
        seen_links = set()
        unique_news = []
        
        for news in news_list:
            link = news.get('link', '')
            if link and link not in seen_links:
                seen_links.add(link)
                unique_news.append(news)
        
        return unique_news
    
    def _filter_by_date(self, news_list: List[Dict], days: int = 3) -> List[Dict]:
        """최근 N일 이내 뉴스만 필터링"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = []
        
        for news in news_list:
            pub_date_str = news.get('pubDate', '')
            
            try:
                # pubDate 형식: "Mon, 30 Dec 2024 09:00:00 +0900"
                pub_date = datetime.strptime(
                    pub_date_str,
                    '%a, %d %b %Y %H:%M:%S %z'
                )
                
                # 시간대 정보 제거하고 비교
                pub_date_naive = pub_date.replace(tzinfo=None)
                
                if pub_date_naive >= cutoff_date:
                    filtered.append(news)
                    
            except Exception:
                # 날짜 파싱 실패 시 포함
                filtered.append(news)
        
        return filtered
    
    def _calculate_relevance_score(self, news_list: List[Dict]) -> List[Dict]:
        """채용 관련도 점수 계산 및 정렬"""
        
        for news in news_list:
            score = 0
            title = news.get('title', '').lower()
            description = news.get('description', '').lower()
            content = f"{title} {description}"
            
            # 핵심 키워드 가중치
            high_priority = ['채용', '구인', '일자리', '신입']
            medium_priority = ['취업', '고용', '인력', '입사']
            
            for keyword in high_priority:
                score += content.count(keyword) * 3
            
            for keyword in medium_priority:
                score += content.count(keyword) * 2
            
            # 일반 키워드
            for keyword in self.employment_keywords:
                if keyword in content:
                    score += 1
            
            news['relevance_score'] = score
        
        # 관련도 점수 순으로 정렬
        return sorted(
            news_list,
            key=lambda x: x.get('relevance_score', 0),
            reverse=True
        )
