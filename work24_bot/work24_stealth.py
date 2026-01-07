#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 크롤러 - 실시간 로그 출력 강화 버전 (flush=True)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import json
from typing import Dict, List

class Work24StealthCrawler:
    
    def __init__(self):
        self.driver = None
    
    def setup_stealth_driver(self):
        options = Options()
        options.add_argument('--headless=new') 
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        self.driver.implicitly_wait(10)

    def collect_jobs(self, max_jobs: int = 15) -> Dict[str, List[str]]:
        if not self.driver:
            self.setup_stealth_driver()
        
        categorized_jobs = {"대기업": [], "중견기업": [], "외국계": [], "강소기업": []}
        
        try:
            print(">>> [접속] 고용24 메인 페이지 이동...", flush=True)
            url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do"
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 30)
            time.sleep(3)

            # [1] 상세 필터링
            targets = [
                "enterPriseGbnParam01", "enterPriseGbnParam05", "enterPriseGbnParam06", 
                "enterPriseGbnParam07", "enterPriseGbnParam10", 
                "b_siteClcdCJK", "b_siteClcdCSI", 
                "employGbnParam10"
            ]
            
            print(">>> [필터] 체크박스 설정 중...", flush=True)
            js_filter = f"""
            const moreBtn = document.getElementById('moreBtn');
            if (moreBtn) moreBtn.click();
            
            const targets = {json.dumps(targets)};
            targets.forEach(id => {{
                const checkbox = document.getElementById(id);
                if (checkbox && !checkbox.checked) {{
                    const label = document.querySelector(`label[for="${{id}}"]`);
                    if (label) label.click();
                }}
            }});
            setTimeout(() => {{ fn_Search('1'); }}, 1000);
            """
            self.driver.execute_script(js_filter)
            
            print(">>> [로딩] 검색 결과 대기 중 (15초)...", flush=True)
            time.sleep(15) 

            # [2] 공고 찾기
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table-list tbody tr")
            if len(rows) == 0:
                print("⚠️ [경고] 테이블 못 찾음. 전체 검색 시도.", flush=True)
                rows = self.driver.find_elements(By.TAG_NAME, "tr")

            print(f"👉 [DEBUG] 화면에서 발견된 총 행(Row) 수: {len(rows)}개", flush=True)
            
            if len(rows) == 0:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text[:500]
                print(f"❌ [오류] 공고 0개. 화면 요약:\n{body_text}", flush=True)
                return categorized_jobs

            # [3] 데이터 수집
            main_window = self.driver.current_window_handle
            
            now = datetime.now()
            today_formats = [
                now.strftime("%y.%m.%d"), now.strftime("%Y.%m.%d"), 
                now.strftime("%Y-%m-%d"), now.strftime("%m-%d")
            ]
            
            count = 0
            for i, row in enumerate(rows, 1):
                if count >= max_jobs: break
                
                try:
                    row_text = row.text.strip()
                    if not row_text: 
                        continue

                    # 날짜 확인
                    try:
                        reg_date = row.find_element(By.CLASS_NAME, "date").text.strip()
                    except:
                        reg_date = row_text

                    is_today = any(fmt in reg_date for fmt in today_formats)
                    if not is_today: 
                        # print(f"   🚫 [탈락 {i}] 날짜 아님", flush=True) # 로그가 너무 많으면 주석 처리
                        continue

                    # 카테고리 확인
                    category = None
                    if "대기업" in row_text: category = "대기업"
                    elif "중견" in row_text: category = "중견기업"
                    elif "외국계" in row_text: category = "외국계"
                    elif "강소" in row_text: category = "강소기업"
                    
                    if not category: 
                        continue

                    # [4] 상세 링크 추출 (여기가 시간이 걸리는 구간)
                    print(f"   ⏳ [처리중 {i}] {category} 상세 페이지 진입...", end='', flush=True)
                    
                    try:
                        title_el = row.find_element(By.CSS_SELECTOR, "a[data-emp-detail]")
                        title = title_el.text.strip()
                        detail_url = title_el.get_attribute("href")
                        
                        try:
                            company = row.find_element(By.CLASS_NAME, "cp_name").text.strip()
                        except:
                            company = "회사명"

                        self.driver.execute_script(f"window.open('{detail_url}');")
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        
                        wait_btn = WebDriverWait(self.driver, 5)
                        final_btn = wait_btn.until(EC.presence_of_element_located(
                            (By.XPATH, "//a[contains(@onclick, 'f_goMove')]")
                        ))
                        actual_link = final_btn.get_attribute("onclick").split("'")[1]

                    except Exception as e:
                        actual_link = detail_url if 'detail_url' in locals() else "링크없음"
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(main_window)
                    
                    job_info = f"🏢 {company}\n📌 {title}\n🔗 바로가기: {actual_link}"
                    categorized_jobs[category].append(job_info)
                    count += 1
                    print(f" 완료! ({company})", flush=True)

                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                    self.driver.switch_to.window(main_window)
                    
                    # 너무 빠르면 차단될 수 있으니 짧게 대기
                    time.sleep(0.5)

                except Exception as e:
                    print(f" 에러({e})", flush=True)
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)
                    continue
            
            print(f">>> [완료] 총 {count}개의 공고 수집됨", flush=True)
            
        except Exception as e:
            print(f">>> [오류] 크롤링 전체 실패: {e}", flush=True)
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return categorized_jobs
