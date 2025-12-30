#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기업뉴스 수집기 - 산업별 수집
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict

class NaverCorporateCollector:
    """산업별 기업뉴스 수집기"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        # 산업별 키워드
        self.industries = {
            'IT/기술': [
                '네이버 AI', '카카오 신사업', 'SK텔레콤', 'LG전자',
                '삼성전자 갤럭시', '소프트웨어', '클라우드'
            ],
            '조선': [
                '현대중공업', '삼성중공업', '한화오션',
                'LNG선', '컨테이너선', '친환경선박'
            ],
            '반도체': [
                '삼성전자 반도체', 'SK하이닉스', '메모리반도체',
                'HBM', '파운드리', '시스템반도체'
            ],
            '제조/산업': [
                '현대차', '기아', 'LG화학', 'SK이노베이션',
                '포스코', '배터리', '전기차'
            ],
            '금융': [
                '은행 실적', '증권사', '보험', '핀테크',
                'KB금융', '신한금융', '카카오뱅크'
            ],
            '건설/부동산': [
                '현대건설', 'GS건설', '아파트 분양',
                '재건축', '부동산시장', '주택공급'
            ],
            '바이오/의료': [
                '삼성바이오로직스', '셀트리온', '신약개발',
                '의료기기', '바이오시밀러'
            ]
        }
    
    def collect_by_industry(self) -> Dict[str, List[Dict]]:
        """산업별로 뉴스 수집 (각 2개)"""
        
        result = {}
        
        for industry, keywords in self.industries.items():
            print(f"  {industry}:", end=" ")
            
            industry_news = []
            
            for keyword in keywords:
                try:
                    news = self._search_news(keyword, display=3)
                    industry_news.extend(news)
                except Exception:
                    continue
            
            # 중복 제거
            unique_news = self._remove_duplicates(industry_news)
            
            # 날짜 필터링
            filtered_news = self._filter_by_date(unique_news, days=3)
            
            # 상위 2개 선택
            result[industry] = filtered_news[:2]
            
            print(f"{len(result[industry])}개")
        
        return result
    
    def _search_news(self, query: str, display: int = 3) -> List[Dict]:
        """네이버 뉴스 API 검색"""
        
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        params = {
            'query': query,
            'display': display,
            'sort': 'date'
        }
        
        response = requests.get(
            self.base_url,
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            return []
    
    def _remove_duplicates(self, news_list: List[Dict]) -> List[Dict]:
        """중복 제거"""
        
        seen_links = set()
        unique_news = []
        
        for news in news_list:
            link = news.get('link', '').split('?')[0]
            
            if link and link not in seen_links:
                seen_links.add(link)
                unique_news.append(news)
        
        return unique_news
    
    def _filter_by_date(self, news_list: List[Dict], days: int = 3) -> List[Dict]:
        """최근 N일 이내"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = []
        
        for news in news_list:
            pub_date_str = news.get('pubDate', '')
            
            try:
                pub_date = datetime.strptime(
                    pub_date_str,
                    '%a, %d %b %Y %H:%M:%S %z'
                )
                
                pub_date_naive = pub_date.replace(tzinfo=None)
                
                if pub_date_naive >= cutoff_date:
                    filtered.append(news)
                    
            except Exception:
                filtered.append(news)
        
        return filtered
