#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 크롤러 - Stealth 모드 (상세 필터링 및 원본 링크 추출 버전)
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
    """봇 감지 우회 및 상세 크롤링 엔진"""
    
    def __init__(self):
        self.driver = None
    
    def setup_stealth_driver(self):
        """Selenium Stealth 설정 (GitHub Actions 호환)"""
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
        
        # WebDriver 속성 변조 방지
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        self.driver.implicitly_wait(10)

    def collect_jobs(self, max_jobs: int = 15) -> Dict[str, List[str]]:
        """상세 필터를 적용하여 채용공고 수집 및 원본 링크 추출"""
        if not self.driver:
            self.setup_stealth_driver()
        
        categorized_jobs = {"대기업": [], "중견기업": [], "외국계": [], "강소기업": []}
        
        try:
            url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do"
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 15)
            time.sleep(3)

            # [1] 상세 필터링 적용 (JavaScript 실행)
            targets = [
                "enterPriseGbnParam01", "enterPriseGbnParam05", "enterPriseGbnParam06", 
                "enterPriseGbnParam07", "enterPriseGbnParam10", # 기업규모 5종
                "b_siteClcdCJK", "b_siteClcdCSI", # 정보제공처 (잡코리아, 사람인)
                "employGbnParam10" # 고용형태 (정규직)
            ]
            
            # targets 리스트를 JS 배열 형태로 변환하여 전달
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
            time.sleep(5) # 검색 결과 로딩 대기

            # [2] 오늘 날짜 공고 필터링 및 리스트 순회
            today = datetime.now().strftime("%y.%m.%d")
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table-list tbody tr")
            main_window = self.driver.current_window_handle
            
            count = 0
            for row in rows:
                if count >= max_jobs:
                    break
                
                try:
                    # 오늘 등록된 공고인지 체크
                    reg_date = row.find_element(By.CLASS_NAME, "date").text.strip()
                    if today not in reg_date:
                        continue

                    # 기업 규모 확인 (라벨 텍스트)
                    labels = [l.text.strip() for l in row.find_elements(By.CLASS_NAME, "tbl_label")]
                    
                    category = None
                    if "대기업" in labels: category = "대기업"
                    elif "중견" in labels: category = "중견기업"
                    elif "외국계" in labels: category = "외국계"
                    elif "강소" in labels: category = "강소기업"
                    
                    if not category:
                        continue

                    # 기본 정보 추출
                    company = row.find_element(By.CLASS_NAME, "cp_name").text.strip()
                    title_el = row.find_element(By.CSS_SELECTOR, "a[data-emp-detail]")
                    title = title_el.text.strip()
                    detail_url = title_el.get_attribute("href")

                    # [3] 상세 페이지 이동 -> 원본 사이트 링크 추출
                    self.driver.execute_script(f"window.open('{detail_url}');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    # '바로가기' 버튼의 onclick 속성에서 실제 URL 파싱
                    btn_wait = WebDriverWait(self.driver, 7)
                    final_btn = btn_wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//a[contains(@onclick, 'f_goMove')]")
                    ))
                    
                    onclick_val = final_btn.get_attribute("onclick")
                    # f_goMove('URL') 형태에서 URL만 추출
                    actual_link = onclick_val.split("'")[1]

                    job_info = f"🏢 {company}\n📌 {title}\n🔗 바로가기: {actual_link}"
                    categorized_jobs[category].append(job_info)
                    count += 1

                    # 현재 상세 창 닫고 메인 리스트로 복귀
                    self.driver.close()
                    self.driver.switch_to.window(main_window)
                    time.sleep(1) # 차단 방지용 지연

                except Exception as e:
                    # 에러 발생 시 현재 상세 페이지 창이 열려있다면 닫고 복귀
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)
                    continue
            
            print(f"  [성공] 총 {count}개의 타겟 공고 수집 완료")
            
        except Exception as e:
            print(f"  [오류] 크롤링 중 치명적 에러: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return categorized_jobs
