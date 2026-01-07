#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 크롤러 - Stealth 모드 (봇 감지 우회)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
from typing import Dict, List

class Work24StealthCrawler:
    """봇 감지 우회 크롤러"""
    
    def __init__(self):
        self.driver = None
    
    def setup_stealth_driver(self):
        """봇 감지 우회 설정"""
        
        options = Options()
        
        # Headless 설정
        options.add_argument('--headless=new')  # 새 headless 모드
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # 봇 감지 우회
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User Agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 창 크기
        options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=options)
        
        # WebDriver 속성 숨기기 (JavaScript 실행)
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })
        
        self.driver.implicitly_wait(10)
    
    def collect_jobs(self, max_jobs: int = 15) -> Dict[str, List[str]]:
        """채용공고 수집"""
        
        if not self.driver:
            self.setup_stealth_driver()
        
        categorized_jobs = {
            "대기업": [],
            "중견기업": [],
            "외국계": [],
            "강소기업": []
        }
        
        try:
            url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do"
            self.driver.get(url)
            
            # 페이지 로드 대기
            time.sleep(3)
            
            # JavaScript로 검색 조건 설정
            js_script = """
            // 대기업, 중견, 외국계, 강소 체크박스 클릭
            const labels = ['대기업', '중견기업', '외국계기업', '강소기업'];
            labels.forEach(label => {
                const checkbox = document.querySelector(`label:contains('${label}') input[type='checkbox']`);
                if (checkbox && !checkbox.checked) {
                    checkbox.click();
                }
            });
            
            // 검색 버튼 클릭
            const searchBtn = document.querySelector('button.btn-search, button[type="submit"]');
            if (searchBtn) {
                searchBtn.click();
            }
            """
            
            self.driver.execute_script(js_script)
            time.sleep(2)
            
            # 결과 수집 (이전과 동일)
            today = datetime.now().strftime("%y.%m.%d")
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr, ul.job-list li")
            
            count = 0
            for row in rows:
                if count >= max_jobs:
                    break
                
                try:
                    date_el = row.find_element(By.CSS_SELECTOR, ".date, .reg-date")
                    reg_date = date_el.text.strip()
                    
                    if today not in reg_date:
                        continue
                    
                    company = row.find_element(By.CSS_SELECTOR, ".cp_name, .company-name").text.strip()
                    title_el = row.find_element(By.CSS_SELECTOR, "a.title, a.job-title")
                    title = title_el.text.strip()
                    job_link = title_el.get_attribute("href")
                    
                    labels = [l.text.strip() for l in row.find_elements(By.CSS_SELECTOR, ".tbl_label, .badge")]
                    
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
                    
                    job_info = f"🏢 {company}\n📌 {title}\n🔗 {job_link}"
                    categorized_jobs[category].append(job_info)
                    count += 1
                    
                    print(f"    ✓ [{category}] {company} - {title[:20]}...")
                    
                except Exception:
                    continue
            
            print(f"  수집 완료: 총 {count}개")
            
        except Exception as e:
            print(f"  크롤링 오류: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return categorized_jobs
