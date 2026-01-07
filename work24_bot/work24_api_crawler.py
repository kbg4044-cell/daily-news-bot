#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 크롤러 - 대안 방식 (requests + BeautifulSoup)
Selenium 대신 API 직접 호출
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List
import time
import json

class Work24APICrawler:
    """고용24 API 기반 크롤러 (Selenium 불필요)"""
    
    def __init__(self):
        self.base_url = "https://www.work24.go.kr"
        self.search_url = f"{self.base_url}/wk/a/b/1200/retriveDtlEmpSrchList.do"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Referer': 'https://www.work24.go.kr'
        })
    
    def collect_jobs(self, max_jobs: int = 15) -> Dict[str, List[str]]:
        """
        고용24 채용공고 수집 (API 기반)
        
        Returns:
            카테고리별 채용공고 딕셔너리
        """
        
        categorized_jobs = {
            "대기업": [],
            "중견기업": [],
            "외국계": [],
            "강소기업": []
        }
        
        try:
            # 검색 파라미터 (기업 규모 필터 포함)
            params = {
                'pageIndex': 1,
                'pageUnit': 50,
                'empTpCd': '',  # 고용형태
                'dtyCd': '',    # 직무
                'enterPriseScaleCd': '1,2,3,4',  # 1:대기업, 2:중견, 3:외국계, 4:강소
                'sortType': 'LATEST'  # 최신순
            }
            
            print(f"  고용24 검색 중...")
            
            # API 호출
            response = self.session.get(self.search_url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"  ⚠️ HTTP {response.status_code}")
                return categorized_jobs
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 채용공고 목록 찾기
            job_items = soup.select('table.table-list tbody tr, ul.job-list li')
            
            print(f"  채용공고 발견: {len(job_items)}개")
            
            today = datetime.now().strftime("%y.%m.%d")
            count = 0
            
            for item in job_items:
                if count >= max_jobs:
                    break
                
                try:
                    # 날짜 확인
                    date_el = item.select_one('.date, .reg-date')
                    if not date_el:
                        continue
                    
                    reg_date = date_el.get_text(strip=True)
                    
                    # 당일 공고만
                    if today not in reg_date:
                        continue
                    
                    # 기업명
                    company_el = item.select_one('.cp_name, .company-name')
                    if not company_el:
                        continue
                    
                    company = company_el.get_text(strip=True)
                    
                    # 제목 및 링크
                    title_el = item.select_one('a.title, a.job-title')
                    if not title_el:
                        continue
                    
                    title = title_el.get_text(strip=True)
                    job_link = title_el.get('href', '')
                    
                    # 절대 URL로 변환
                    if job_link and not job_link.startswith('http'):
                        job_link = f"{self.base_url}{job_link}"
                    
                    # 카테고리 라벨
                    labels = [l.get_text(strip=True) for l in item.select('.tbl_label, .badge')]
                    
                    # 카테고리 매칭
                    category = None
                    if any('대기업' in l for l in labels):
                        category = "대기업"
                    elif any('중견' in l for l in labels):
                        category = "중견기업"
                    elif any('외국계' in l for l in labels):
                        category = "외국계"
                    elif any('강소' in l for l in labels):
                        category = "강소기업"
                    
                    if not category:
                        continue
                    
                    # 포맷팅
                    job_info = f"🏢 {company}\n📌 {title}\n🔗 {job_link}"
                    
                    categorized_jobs[category].append(job_info)
                    count += 1
                    
                    print(f"    ✓ [{category}] {company} - {title[:20]}...")
                    
                    # 서버 부담 줄이기
                    time.sleep(0.5)
                    
                except Exception as e:
                    continue
            
            print(f"  수집 완료: 총 {count}개")
            
        except Exception as e:
            print(f"  크롤링 오류: {e}")
        
        return categorized_jobs
