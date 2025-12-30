#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용뉴스 수집기 - 중복 제거 초강화 버전
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
import re

class NaverEmploymentCollector:
    """고용뉴스 전문 수집기 (중복 제거 초강화)"""
    
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
        
        # 2단계: 제목 핵심 키워드 기반 중복 제거 (강화!)
        unique_by_title = self._remove_duplicates_by_title_v2(unique_by_url)
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
            link = news.get('link', '')
            
            # URL 정규화 (파라미터 제거)
            normalized_link = link.split('?')[0]
            
            if normalized_link and normalized_link not in seen_urls:
                seen_urls.add(normalized_link)
                unique_news.append(news)
        
        return unique_news
    
    def _remove_duplicates_by_title_v2(self, news_list: List[Dict]) -> List[Dict]:
        """
        제목 기반 중복 제거 - 강화 버전
        핵심 키워드 추출 방식 개선
        """
        
        seen_signatures = set()
        unique_news = []
        
        for news in news_list:
            title = self._clean_title(news.get('title', ''))
            
            # 핵심 키워드 시그니처 생성 (개선!)
            signature = self._create_enhanced_signature(title)
            
            if signature and signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_news.append(news)
            else:
                # 디버그: 중복 제거된 항목 출력
                print(f"    🔄 중복 제거: {title[:30]}...")
        
        return unique_news
    
    def _create_enhanced_signature(self, title: str) -> str:
        """
        향상된 시그니처 생성
        
        핵심 아이디어:
        1. 숫자 추출 (예: 820명, 200명)
        2. 회사명 추출 (예: 서울교통공사, 현대중공업)
        3. 핵심 단어 추출 (채용, 수주, 투자)
        """
        
        # HTML 태그 제거
        title = re.sub(r'<[^>]+>', '', title)
        title = title.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')
        
        # 1. 숫자 추출 (채용 인원, 금액 등)
        numbers = re.findall(r'\d+(?:만|명|억|조)?', title)
        
        # 2. 회사명 추출 (주요 기업명 패턴)
        companies = []
        company_keywords = [
            '현대', '삼성', '엘지', 'LG', 'SK', '포스코', '한화',
            '네이버', '카카오', '쿠팡', '배민', '토스',
            '교통공사', '전력공사', '수자원공사', '도로공사',
            '건설', '중공업', '전자', '화학', '금융', '은행'
        ]
        
        for keyword in company_keywords:
            if keyword in title:
                companies.append(keyword)
        
        # 3. 핵심 행위 추출
        actions = []
        action_keywords = ['채용', '모집', '선발', '입사', '구인', '수주', '투자', '확대', '증원']
        
        for keyword in action_keywords:
            if keyword in title:
                actions.append(keyword)
        
        # 시그니처 생성: 회사명 + 숫자 + 행위
        signature_parts = []
        
        if companies:
            signature_parts.extend(sorted(companies)[:2])  # 상위 2개
        
        if numbers:
            signature_parts.extend(sorted(numbers)[:2])  # 상위 2개
        
        if actions:
            signature_parts.extend(sorted(actions)[:2])  # 상위 2개
        
        # 최종 시그니처
        signature = '_'.join(signature_parts)
        
        return signature.lower()
    
    def _clean_title(self, title: str) -> str:
        """제목 정리"""
        
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
