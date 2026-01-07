#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 크롤러 - 디버깅 모드 (스크린샷 & 광범위 검색)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import json
import os

class Work24StealthCrawler:
    
    def __init__(self):
        self.driver = None
    
    def setup_stealth_driver(self):
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def collect_jobs(self, max_jobs: int = 15):
        if not self.driver:
            self.setup_stealth_driver()
        
        categorized_jobs = {"대기업": [], "중견기업": [], "외국계": [], "강소기업": []}
        
        try:
            print(">>> [접속] 고용24 메인 페이지 이동...")
            self.driver.get("https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do")
            wait = WebDriverWait(self.driver, 20)
            time.sleep(5) # 충분한 대기

            # [DEBUG] 페이지 로딩 상태 확인
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "검색결과가 없습니다" in body_text:
                print("⚠️ [경고] 초기 페이지부터 '검색결과 없음'이 뜹니다.")

            # 필터 적용
            print(">>> [필터] 체크박스 설정 중...")
            targets = [
                "enterPriseGbnParam01", "enterPriseGbnParam05", "enterPriseGbnParam06", 
                "enterPriseGbnParam07", "enterPriseGbnParam10", 
                "b_siteClcdCJK", "b_siteClcdCSI", 
                "employGbnParam10"
            ]
            
            # JS로 체크박스 강제 클릭 후 검색
            js_script = f"""
            const targets = {json.dumps(targets)};
            targets.forEach(id => {{
                const el = document.getElementById(id);
                if (el && !el.checked) {{
                    el.click(); // 체크박스 직접 클릭 (이벤트 트리거용)
                }}
            }});
            setTimeout(() => {{ fn_Search('1'); }}, 1000);
            """
            self.driver.execute_script(js_script)
            
            print(">>> [로딩] 검색 결과 기다리는 중 (10초)...")
            time.sleep(10)

            # [수정] 검색 범위를 넓힘 (특정 클래스 의존 제거)
            rows = self.driver.find_elements(By.XPATH, "//tbody/tr")
            print(f"👉 [DEBUG] 발견된 테이블 줄(Row) 수: {len(rows)}개")

            # [DEBUG] 공고가 0개면 스크린샷 저장
            if len(rows) == 0:
                print("❌ [오류] 공고를 찾지 못했습니다. 스크린샷을 저장합니다.")
                self.driver.save_screenshot("debug_error.png")
                
                # 화면에 있는 텍스트 일부 출력 (원인 분석용)
                print(f"📄 [화면 텍스트 요약]: {self.driver.find_element(By.TAG_NAME, 'body').text[:300]}")
                return categorized_jobs

            # ... (이하 날짜 필터링 및 수집 로직은 동일)
            # 간결함을 위해 수집 루프는 유지하되, 핵심 디버깅 부분만 강화했습니다.
            
            today_formats = [datetime.now().strftime(fmt) for fmt in ["%y.%m.%d", "%Y.%m.%d", "%Y-%m-%d", "%m-%d"]]
            
            main_window = self.driver.current_window_handle
            count = 0
            
            for row in rows:
                if count >= max_jobs: break
                try:
                    text = row.text
                    # 날짜 확인
                    is_today = any(f in text for f in today_formats)
                    if not is_today: continue
                    
                    # 카테고리 확인
                    category = None
                    if "대기업" in text: category = "대기업"
                    elif "중견" in text: category = "중견기업"
                    elif "외국계" in text: category = "외국계"
                    elif "강소" in text: category = "강소기업"
                    
                    if not category: continue

                    # 링크 추출 로직 (안전하게)
                    try:
                        title_el = row.find_element(By.CSS_SELECTOR, "a[href*='empDetail']")
                        company = row.find_element(By.CLASS_NAME, "cp_name").text.strip()
                        title = title_el.text.strip()
                        link = title_el.get_attribute("href")
                        
                        job_info = f"🏢 {company}\n📌 {title}\n🔗 {link}"
                        categorized_jobs[category].append(job_info)
                        count += 1
                        print(f"   ✓ [수집] {company}")
                    except:
                        continue
                        
                except: continue

        except Exception as e:
            print(f"❌ [에러] {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
        
        return categorized_jobs
