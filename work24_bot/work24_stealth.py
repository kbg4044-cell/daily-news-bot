#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 크롤러 - Stealth 모드 (디버깅 강화 및 다중 날짜 포맷 지원)
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
        """Selenium Stealth 설정"""
        options = Options()
        options.add_argument('--headless=new')  # 유령 모드 (창 안 뜸)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # 봇 탐지 회피
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User Agent (일반 브라우저처럼 보이기)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=options)
        
        # navigator.webdriver 속성 숨기기
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        self.driver.implicitly_wait(10)

    def collect_jobs(self, max_jobs: int = 15) -> Dict[str, List[str]]:
        """상세 필터 적용, 날짜 디버깅, 원본 링크 추출"""
        if not self.driver:
            self.setup_stealth_driver()
        
        categorized_jobs = {"대기업": [], "중견기업": [], "외국계": [], "강소기업": []}
        
        try:
            print(">>> [진행] 고용24 사이트 접속 중...")
            url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do"
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 20)
            time.sleep(3) # 초기 로딩 대기

            # [1] 상세 필터링 적용 (JS 강제 클릭)
            targets = [
                "enterPriseGbnParam01", "enterPriseGbnParam05", "enterPriseGbnParam06", 
                "enterPriseGbnParam07", "enterPriseGbnParam10", # 기업규모
                "b_siteClcdCJK", "b_siteClcdCSI", # 잡코리아, 사람인
                "employGbnParam10" # 정규직
            ]
            
            print(">>> [진행] 필터 적용 중 (JavaScript)...")
            js_filter = f"""
            const moreBtn = document.getElementById('moreBtn');
            if (moreBtn) moreBtn.click();
            
            const targets = {json.dumps(targets)};
            targets.forEach(id => {{
                const checkbox = document.getElementById(id);
                // 체크가 안 되어 있다면 클릭
                if (checkbox && !checkbox.checked) {{
                    const label = document.querySelector(`label[for="${{id}}"]`);
                    if (label) label.click();
                }}
            }});
            
            // 잠시 후 검색 실행
            setTimeout(() => {{ fn_Search('1'); }}, 500);
            """
            self.driver.execute_script(js_filter)
            
            # 검색 후 결과가 로딩될 때까지 충분히 대기 (중요!)
            print(">>> [진행] 검색 결과 로딩 대기 (약 7초)...")
            time.sleep(7) 

            # [2] 날짜 형식 준비 (다양한 포맷 대응)
            now = datetime.now()
            today_formats = [
                now.strftime("%y.%m.%d"),  # 26.01.07 (가장 흔함)
                now.strftime("%Y.%m.%d"),  # 2026.01.07
                now.strftime("%Y-%m-%d"),  # 2026-01-07
                now.strftime("%m-%d")      # 01-07
            ]
            
            # 공고 리스트 가져오기
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table-list tbody tr")
            print(f"👉 [DEBUG] 화면에서 발견된 총 공고 줄 수: {len(rows)}개")
            
            main_window = self.driver.current_window_handle
            count = 0
            
            for row in rows:
                if count >= max_jobs: break
                
                try:
                    # 1. 날짜 확인
                    # 구조가 바뀔 수 있으므로 여러 클래스 시도
                    try:
                        reg_date = row.find_element(By.CLASS_NAME, "date").text.strip()
                    except:
                        # date 클래스가 없으면 전체 텍스트에서 찾기 시도
                        reg_date = row.text
                    
                    # 디버그 로그: 실제 날짜가 어떻게 찍히는지 확인
                    # print(f"   [DEBUG] 공고 날짜: '{reg_date}' vs 찾는 날짜들: {today_formats}")

                    # 오늘 날짜 포맷 중 하나라도 포함되어 있으면 OK
                    is_today = any(fmt in reg_date for fmt in today_formats)
                    
                    if not is_today:
                        continue

                    # 2. 기업 규모 확인
                    labels = [l.text.strip() for l in row.find_elements(By.CLASS_NAME, "tbl_label")]
                    category = None
                    if "대기업" in labels: category = "대기업"
                    elif "중견" in labels: category = "중견기업"
                    elif "외국계" in labels: category = "외국계"
                    elif "강소" in labels: category = "강소기업"
                    
                    if not category: continue

                    # 3. 기본 정보 수집
                    company = row.find_element(By.CLASS_NAME, "cp_name").text.strip()
                    title_el = row.find_element(By.CSS_SELECTOR, "a[data-emp-detail]")
                    title = title_el.text.strip()
                    detail_url = title_el.get_attribute("href")

                    # 4. 상세 페이지 진입 -> 원본 링크 추출
                    self.driver.execute_script(f"window.open('{detail_url}');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    # '바로가기' 버튼 대기
                    try:
                        btn_wait = WebDriverWait(self.driver, 5)
                        final_btn = btn_wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//a[contains(@onclick, 'f_goMove')]")
                        ))
                        onclick_val = final_btn.get_attribute("onclick")
                        actual_link = onclick_val.split("'")[1]
                    except:
                        # 바로가기 버튼 못 찾으면 그냥 고용24 링크 사용
                        actual_link = detail_url

                    job_info = f"🏢 {company}\n📌 {title}\n🔗 {actual_link}"
                    categorized_jobs[category].append(job_info)
                    count += 1
                    print(f"   ✓ [수집성공] {category} - {company}")

                    # 탭 닫고 복귀
                    self.driver.close()
                    self.driver.switch_to.window(main_window)
                    time.sleep(0.5)

                except Exception as e:
                    # 에러 발생 시 복구
                    print(f"   ⚠️ 항목 스킵 에러: {e}")
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)
                    continue
            
            print(f">>> [완료] 총 {count}개의 타겟 공고 수집 완료")
            
        except Exception as e:
            print(f">>> [오류] 크롤링 중 치명적 문제: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return categorized_jobs
