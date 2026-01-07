#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 크롤러 - Stealth 모드 (상세 탈락 로그 & 원본 링크 추출)
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
            print(">>> [접속] 고용24 메인 페이지 이동...")
            url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do"
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 20)
            time.sleep(3)

            # [1] 상세 필터링 (JS 강제 클릭)
            targets = [
                "enterPriseGbnParam01", "enterPriseGbnParam05", "enterPriseGbnParam06", 
                "enterPriseGbnParam07", "enterPriseGbnParam10", 
                "b_siteClcdCJK", "b_siteClcdCSI", 
                "employGbnParam10"
            ]
            
            print(">>> [필터] 체크박스 설정 중...")
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
            setTimeout(() => {{ fn_Search('1'); }}, 500);
            """
            self.driver.execute_script(js_filter)
            
            print(">>> [로딩] 검색 결과 대기 중 (약 7초)...")
            time.sleep(7) 

            # [2] 날짜 포맷 준비
            now = datetime.now()
            today_formats = [
                now.strftime("%y.%m.%d"), now.strftime("%Y.%m.%d"), 
                now.strftime("%Y-%m-%d"), now.strftime("%m-%d")
            ]
            
            # 검색 범위를 테이블 전체 행으로 설정
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table-list tbody tr")
            print(f"👉 [DEBUG] 화면에서 발견된 총 행(Row) 수: {len(rows)}개")
            
            main_window = self.driver.current_window_handle
            count = 0
            
            for i, row in enumerate(rows, 1):
                if count >= max_jobs: break
                
                try:
                    # 텍스트 전체 미리 가져오기 (디버깅용)
                    row_text = row.text.strip()
                    if not row_text:
                        print(f"   🚫 [탈락 {i}] 빈 줄(Hidden Row)입니다.")
                        continue

                    # 날짜 확인
                    try:
                        reg_date = row.find_element(By.CLASS_NAME, "date").text.strip()
                    except:
                        reg_date = "날짜못찾음"

                    is_today = any(fmt in reg_date for fmt in today_formats)
                    
                    # 회사명 미리 추출 시도 (로그용)
                    try:
                        company_log = row.find_element(By.CLASS_NAME, "cp_name").text.strip()
                    except:
                        company_log = "회사명모름"

                    if not is_today:
                        print(f"   🚫 [탈락 {i}] 날짜 불일치: {reg_date} (회사: {company_log})")
                        continue

                    # 카테고리 확인
                    labels = [l.text.strip() for l in row.find_elements(By.CLASS_NAME, "tbl_label")]
                    category = None
                    if "대기업" in labels: category = "대기업"
                    elif "중견" in labels: category = "중견기업"
                    elif "외국계" in labels: category = "외국계"
                    elif "강소" in labels: category = "강소기업"
                    
                    if not category:
                        print(f"   🚫 [탈락 {i}] 카테고리 없음: {labels} (회사: {company_log})")
                        continue

                    # [3] 수집 성공 -> 상세 페이지 진입 -> 원본 링크 추출
                    title_el = row.find_element(By.CSS_SELECTOR, "a[data-emp-detail]")
                    title = title_el.text.strip()
                    detail_url = title_el.get_attribute("href")

                    self.driver.execute_script(f"window.open('{detail_url}');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    try:
                        btn_wait = WebDriverWait(self.driver, 5)
                        final_btn = btn_wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//a[contains(@onclick, 'f_goMove')]")
                        ))
                        actual_link = final_btn.get_attribute("onclick").split("'")[1]
                    except:
                        actual_link = detail_url # 실패 시 기본 링크

                    job_info = f"🏢 {company_log}\n📌 {title}\n🔗 바로가기: {actual_link}"
                    categorized_jobs[category].append(job_info)
                    count += 1
                    print(f"   ✅ [수집 {i}] {category} - {company_log}")

                    self.driver.close()
                    self.driver.switch_to.window(main_window)
                    time.sleep(0.5)

                except Exception as e:
                    print(f"   ⚠️ [에러 {i}] 처리 중 오류: {e}")
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)
                    continue
            
            print(f">>> [완료] 총 {count}개의 공고를 수집했습니다.")
            
        except Exception as e:
            print(f">>> [오류] 크롤링 실패: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return categorized_jobs
