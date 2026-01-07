#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 채용공고봇 - 순차 실행 모드 (대기업 -> 중견 -> 외국계 -> 강소)
"""

import os
import time
from datetime import datetime
from kakao_sender import KakaoSender
from work24_stealth import Work24StealthCrawler

def main():
    print("=" * 50)
    print("🏢 고용24 순차 발송 봇 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 카톡 설정 확인
    api_key = os.environ.get('KAKAO_REST_API_KEY')
    refresh_token = os.environ.get('KAKAO_REFRESH_TOKEN')
    
    if not api_key or not refresh_token:
        print("❌ [오류] 카카오 API 키가 설정되지 않았습니다.")
        return

    sender = KakaoSender(rest_api_key=api_key, refresh_token=refresh_token)
    crawler = Work24StealthCrawler()
    
    # 순서대로 실행할 타겟 목록 (이름, 체크박스ID)
    # 1. 대기업 (01)
    # 2. 중견기업 (20) - *주의: 20번이 중견기업 ID
    # 3. 외국계 (05)
    # 4. 청년친화강소 (10)
    target_list = [
        ("대기업", "enterPriseGbnParam01"),
        ("중견기업", "enterPriseGbnParam20"),
        ("외국계기업", "enterPriseGbnParam05"),
        ("청년친화강소기업", "enterPriseGbnParam10")
    ]
    
    total_sent = 0

    try:
        # 루프 시작: 하나씩 처리하고 바로 발송
        for name, target_id in target_list:
            
            # 1. 크롤링 (해당 기업형태만)
            jobs = crawler.scrape_one_category(name, target_id, max_jobs=15)
            
            if not jobs:
                print(f"ℹ️ '{name}' 조건의 오늘 공고가 없습니다.\n")
                continue
            
            # 2. 메시지 만들기
            msg = format_message(name, jobs)
            
            # 3. 바로 발송
            print(f"📤 [{name}] 카톡 발송 시도 ({len(jobs)}건)...", flush=True)
            if sender.send_message(msg):
                print(f"   ✓ 전송 성공!")
                total_sent += 1
            else:
                print(f"   ❌ 전송 실패")
            
            # 다음 검색 전 잠시 대기 (도배 방지 및 로딩 안정화)
            time.sleep(2)
            
    except Exception as e:
        print(f"❌ 전체 프로세스 중 치명적 에러: {e}")
        
    finally:
        crawler.close()
        print("=" * 50)
        print(f"🏁 모든 작업 완료. 총 {total_sent}번 발송함.")

def format_message(category, items):
    """메시지 포맷팅"""
    icons = {
        "대기업": "🏆", 
        "중견기업": "💼", 
        "외국계기업": "🌏", 
        "청년친화강소기업": "⭐"
    }
    icon = icons.get(category, "📌")
    
    # 헤더
    msg = f"{icon} {category} 채용공고 ({datetime.now().strftime('%m/%d')})\n"
    msg += "=" * 25 + "\n\n"
    
    # 내용 (최대 5개 표시)
    msg += "\n\n".join(items[:5])
    
    # 더 있으면 표시
    if len(items) > 5:
        msg += f"\n\n...외 {len(items)-5}건 더 있음"
        
    return msg

if __name__ == "__main__":
    main()
