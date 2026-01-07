#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 채용공고 크롤러
"""

import time
import datetime
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class Work24Crawler:
    """고용24 채용공고 크롤러"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
    
    def collect_jobs(self, max_jobs: int = 15) -> Dict[str, List[str]]:
        """
        고용24에서 채용공고 수집
        
        Returns:
            카테고리별 채용공고 딕셔너리
        """
        
        if not self.driver:
            self.setup_driver()
        
        categorized_jobs = {
            "대기업": [],
            "중견기업": [],
            "외국계": [],
            "강소기업": []
        }
        
        try:
            # 1. 고용24 접속
            url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do"
            self.driver.get(url)
            
            wait = WebDriverWait(self.driver, 15)
            
            # 2. 추가 검색조건 열기
            try:
                expand_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-search-open, a.btn-more"))
                )
                self.driver.execute_script("arguments[0].click();", expand_btn)
                time.sleep(1)
            except:
                print("  추가 검색조건 버튼 없음 (이미 열려있음)")
            
            # 3. 기업 규모 필터 체크
            filter_labels = ["대기업", "중견기업", "외국계기업", "강소기업", "벤처기업", "상장기업", "우수기업", "일반기업"]
            
            for label in filter_labels:
                try:
                    checkbox = self.driver.find_element(
                        By.XPATH, 
                        f"//label[contains(text(), '{label}')]/input[@type='checkbox']"
                    )
                    if not checkbox.is_selected():
                        self.driver.execute_script("arguments[0].click();", checkbox)
                except:
                    pass
            
            time.sleep(1)
            
            # 4. 검색 버튼 클릭
            search_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn-search, button[type='submit']")
            self.driver.execute_script("arguments[0].click();", search_btn)
            
            time.sleep(2)
            
            # 5. 결과 수집
            today = datetime.datetime.now().strftime("%y.%m.%d")
            main_window = self.driver.current_window_handle
            
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr, ul.job-list li")
            
            print(f"  채용공고 발견: {len(rows)}개")
            
            count = 0
            for row in rows:
                if count >= max_jobs:
                    break
                
                try:
                    # 날짜 확인
                    date_el = row.find_element(By.CSS_SELECTOR, ".date, .reg-date")
                    reg_date = date_el.text.strip()
                    
                    if today not in reg_date:
                        continue
                    
                    # 기업명 및 제목
                    company = row.find_element(By.CSS_SELECTOR, ".cp_name, .company-name").text.strip()
                    title_el = row.find_element(By.CSS_SELECTOR, "a.title, a.job-title")
                    title = title_el.text.strip()
                    
                    # 카테고리 라벨
                    labels = [l.text.strip() for l in row.find_elements(By.CSS_SELECTOR, ".tbl_label, .badge")]
                    
                    # 카테고리 매칭
                    category = None
                    if any("대기업" in l for l in labels):
                        category = "대기업"
                    elif any("중견" in l for l in labels):
                        category = "중견기업"
                    elif any("외국계" in l for l in labels):
                        category = "외국계"
                    elif any("강소" in l for l in labels):
                        category = "강소기업"
                    
                    if not category:
                        continue
                    
                    # 링크 추출
                    job_link = title_el.get_attribute("href")
                    
                    # 포맷팅
                    job_info = f"🏢 {company}\n📌 {title}\n🔗 {job_link}"
                    
                    categorized_jobs[category].append(job_info)
                    count += 1
                    
                    print(f"    ✓ [{category}] {company} - {title[:20]}...")
                    
                except Exception as e:
                    continue
            
            print(f"  수집 완료: 총 {count}개")
            
        except Exception as e:
            print(f"  크롤링 오류: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return categorized_jobs
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
