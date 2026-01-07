#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 크롤러 - 카테고리별 순차 검색 & 원본 링크 추출 엔진
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import json

class Work24StealthCrawler:
    
    def __init__(self):
        self.driver = None
    
    def setup_driver(self):
        """드라이버 설정 (한 번만 실행)"""
        if self.driver: return
        
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

    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def scrape_one_category(self, category_name, target_id, max_jobs=10):
        """
        특정 기업형태(target_id) 하나만 체크하고 검색하여 결과를 반환
        """
        self.setup_driver()
        job_results = []
        
        try:
            print(f"\n>>> [시작] '{category_name}' 공고 검색 시작...", flush=True)
            
            # 1. 초기화 (새로고침 효과를 위해 URL 재접속)
            self.driver.get("https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do")
            wait = WebDriverWait(self.driver, 20)
            time.sleep(3) # 접속 대기

            # 2. 필터 설정 (공통 필터 + 타겟 기업형태 1개)
            # 공통: 잡코리아, 사람인, 정규직
            common_ids = ["b_siteClcdCJK", "b_siteClcdCSI", "employGbnParam10"]
            
            # JS로 클릭 (안전하게)
            js_script = f"""
            // 더보기 열기
            const moreBtn = document.getElementById('moreBtn');
            if (moreBtn) moreBtn.click();
            
            // 1. 공통 필터 체크
            const commons = {json.dumps(common_ids)};
            commons.forEach(id => {{
                const el = document.getElementById(id);
                if (el && !el.checked) {{
                    const lbl = document.querySelector(`label[for="${{id}}"]`);
                    if (lbl) lbl.click();
                }}
            }});

            // 2. 타겟 기업형태(대기업/중견 등) 하나만 체크
            const target = document.getElementById('{target_id}');
            if (target && !target.checked) {{
                const lbl = document.querySelector(`label[for="{target_id}"]`);
                if (lbl) lbl.click();
            }}

            // 3. 검색 실행
            setTimeout(() => {{ fn_Search('1'); }}, 500);
            """
            self.driver.execute_script(js_script)
            
            print(f">>> [로딩] '{category_name}' 검색 결과 대기 중 (10초)...", flush=True)
            time.sleep(10) # 충분한 대기

            # 3. 결과 수집
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table-list tbody tr")
            if len(rows) == 0:
                print("⚠️ 테이블 못 찾음. 전체 검색 시도.", flush=True)
                rows = self.driver.find_elements(By.TAG_NAME, "tr")

            print(f"👉 [DEBUG] 발견된 행(Row): {len(rows)}개", flush=True)
            
            # 날짜 포맷
            now = datetime.now()
            today_formats = [now.strftime(f) for f in ["%y.%m.%d", "%Y.%m.%d", "%Y-%m-%d", "%m-%d"]]
            
            main_window = self.driver.current_window_handle
            count = 0

            for i, row in enumerate(rows, 1):
                if count >= max_jobs: break
                
                try:
                    text = row.text.strip()
                    if not text: continue # 빈 줄 패스

                    # 날짜 확인
                    try:
                        reg_date = row.find_element(By.CLASS_NAME, "date").text.strip()
                    except:
                        reg_date = text
                    
                    if not any(f in reg_date for f in today_formats):
                        continue # 오늘 거 아니면 패스

                    # [중요] 카테고리가 섞여 나올 수 있으므로 더블 체크
                    # (예: 대기업 검색했는데 계열사 중소기업이 나올 수도 있음 -> 그래도 검색결과 존중)
                    
                    # 상세 정보 추출
                    print(f"   ⏳ [처리중] 상세 페이지 진입...", end='', flush=True)
                    
                    title_el = row.find_element(By.CSS_SELECTOR, "a[data-emp-detail]")
                    title = title_el.text.strip()
                    detail_url = title_el.get_attribute("href")
                    
                    try:
                        company = row.find_element(By.CLASS_NAME, "cp_name").text.strip()
                    except:
                        company = category_name

                    # 4. 원본 링크 추출 (새 창)
                    self.driver.execute_script(f"window.open('{detail_url}');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    try:
                        wait_btn = WebDriverWait(self.driver, 5)
                        final_btn = wait_btn.until(EC.presence_of_element_located(
                            (By.XPATH, "//a[contains(@onclick, 'f_goMove')]")
                        ))
                        actual_link = final_btn.get_attribute("onclick").split("'")[1]
                    except:
                        actual_link = detail_url

                    job_info = f"🏢 {company}\n📌 {title}\n🔗 바로가기: {actual_link}"
                    job_results.append(job_info)
                    count += 1
                    print(f" 완료! ({company})", flush=True)

                    # 탭 닫기
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                    self.driver.switch_to.window(main_window)
                    time.sleep(0.5)

                except Exception:
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)
                    continue
            
            print(f"✅ [완료] '{category_name}' 수집: {count}건", flush=True)
            
        except Exception as e:
            print(f"❌ [에러] '{category_name}' 처리 중 실패: {e}", flush=True)
        
        return job_results
