#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용뉴스 수집기 - 중복 제거 강화
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
import hashlib

class NaverEmploymentCollector:
    """고용뉴스 전문 수집기 (중복 제거 강화)"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        self.employment_keywords = [
            '채용', '신입사원', '경력직', '구인', '일자리',
            '취업', '고용', '인력', '직원모집', '리크루팅',
            '입사', '면접', '인재채용', '대규모채용', '청년채용'
        ]
    
    def collect_unique_news(self, count: int = 30) -> List[Dict]:
        """
        중복 제거된 고용뉴스 수집
        
        Args:
            count: 수집할 개수
            
        Returns:
            중복이 제거된 뉴스 리스트
        """
        
        all_news = []
        
        # 핵심 키워드로 검색
        main_keywords = ['채용 공고', '신입 채용', '대규모 채용', '일자리', '취업']
        
        for keyword in main_keywords:
            try:
                news = self._search_news(keyword, display=15)
                all_news.extend(news)
            except Exception as e:
                print(f"⚠️ '{keyword}' 검색 실패: {e}")
                continue
        
        print(f"  수집: {len(all_news)}개")
        
        # 1단계: URL 기반 중복 제거
        unique_by_url = self._remove_duplicates_by_url(all_news)
        print(f"  URL 중복 제거 후: {len(unique_by_url)}개")
        
        # 2단계: 제목 유사도 기반 중복 제거
        unique_by_title = self._remove_duplicates_by_title(unique_by_url)
        print(f"  제목 중복 제거 후: {len(unique_by_title)}개")
        
        # 3단계: 날짜 필터링
        filtered = self._filter_by_date(unique_by_title, days=2)
        print(f"  날짜 필터링 후: {len(filtered)}개")
        
        # 4단계: 관련도 점수 계산
        scored = self._calculate_relevance_score(filtered)
        
        return scored[:count]
    
    def _search_news(self, query: str, display: int = 10) -> List[Dict]:
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
            raise Exception(f"API 오류: {response.status_code}")
    
    def _remove_duplicates_by_url(self, news_list: List[Dict]) -> List[Dict]:
        """URL 기반 중복 제거"""
        
        seen_urls = set()
        unique_news = []
        
        for news in news_list:
            # 원본 URL과 정규화된 URL 모두 체크
            link = news.get('link', '')
            
            # URL 정규화 (파라미터 제거)
            normalized_link = link.split('?')[0]
            
            if normalized_link and normalized_link not in seen_urls:
                seen_urls.add(normalized_link)
                unique_news.append(news)
        
        return unique_news
    
    def _remove_duplicates_by_title(self, news_list: List[Dict]) -> List[Dict]:
        """제목 유사도 기반 중복 제거"""
        
        seen_signatures = set()
        unique_news = []
        
        for news in news_list:
            title = self._clean_title(news.get('title', ''))
            
            # 제목 시그니처 생성 (핵심 단어만 추출)
            signature = self._create_title_signature(title)
            
            if signature and signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_news.append(news)
        
        return unique_news
    
    def _create_title_signature(self, title: str) -> str:
        """제목에서 핵심 단어로 시그니처 생성"""
        
        import re
        
        # HTML 태그 제거
        title = re.sub(r'<[^>]+>', '', title)
        
        # 특수문자 제거
        title = re.sub(r'[^\w\s]', '', title)
        
        # 공백 정규화
        title = ' '.join(title.split())
        
        # 핵심 단어만 추출 (3글자 이상)
        words = [w for w in title.split() if len(w) >= 3]
        
        # 상위 5개 단어로 시그니처
        signature = ' '.join(sorted(words[:5]))
        
        return signature.lower()
    
    def _clean_title(self, title: str) -> str:
        """제목 정리"""
        
        import re
        
        # HTML 태그 제거
        title = re.sub(r'<[^>]+>', '', title)
        
        # HTML 엔티티 변환
        title = title.replace('&quot;', '"')
        title = title.replace('&apos;', "'")
        title = title.replace('&amp;', '&')
        
        return title.strip()
    
    def _filter_by_date(self, news_list: List[Dict], days: int = 2) -> List[Dict]:
        """최근 N일 이내 뉴스만"""
        
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
                # 날짜 파싱 실패 시 포함
                filtered.append(news)
        
        return filtered
    
    def _calculate_relevance_score(self, news_list: List[Dict]) -> List[Dict]:
        """관련도 점수 계산"""
        
        for news in news_list:
            score = 0
            title = news.get('title', '').lower()
            description = news.get('description', '').lower()
            content = f"{title} {description}"
            
            # 핵심 키워드 가중치
            high_priority = ['채용 공고', '신입 채용', '대규모 채용', '인재 영입']
            medium_priority = ['채용', '구인', '일자리', '입사']
            
            for keyword in high_priority:
                if keyword in content:
                    score += 5
            
            for keyword in medium_priority:
                score += content.count(keyword) * 2
            
            for keyword in self.employment_keywords:
                if keyword in content:
                    score += 1
            
            news['relevance_score'] = score
        
        return sorted(
            news_list,
            key=lambda x: x.get('relevance_score', 0),
            reverse=True
        )
