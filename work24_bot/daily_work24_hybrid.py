#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 채용공고봇 - Selenium 우선 실행 버전
"""

import os
from datetime import datetime
from kakao_sender import KakaoSender

def main():
    print("=" * 50)
    print("🏢 고용24 채용공고봇 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    jobs_data = None
    
    # 1차 시도: Selenium Stealth (가장 확실한 필터링 및 원본 링크 추출)
    print("\n[1/3] 🔍 고용24 크롤링 중 (Selenium Stealth)...")
    try:
        from work24_stealth import Work24StealthCrawler
        
        crawler = Work24StealthCrawler()
        jobs_data = crawler.collect_jobs(max_jobs=15)
        
        total_count = sum(len(jobs) for jobs in jobs_data.values())
        print(f"✓ 크롤링 완료: {total_count}개 채용공고")
        
    except Exception as e:
        print(f"⚠️ Selenium 실패: {e}")
        # 실패 시에만 대안으로 requests 시도 (선택 사항)
        return

    # 데이터 확인 및 발송
    total_count = sum(len(jobs) for jobs in jobs_data.values())
    
    if total_count == 0:
        print("❌ 오늘 등록된 채용공고가 없습니다.")
        send_empty_message()
        return
    
    # 메시지 포맷팅
    print("\n[2/3] 📝 메시지 포맷팅 중...")
    message = format_work24_message(jobs_data)
    
    # 카카오톡 발송
    print("\n[3/3] 📤 카카오톡 발송 중...")
    try:
        sender = KakaoSender(
            rest_api_key=os.environ['KAKAO_REST_API_KEY'],
            refresh_token=os.environ['KAKAO_REFRESH_TOKEN']
        )
        
        result = sender.send_message(message)
        if result: print("✓ 발송 성공!")
        else: print("❌ 발송 실패")
            
    except Exception as e:
        print(f"❌ 발송 오류: {e}")

def format_work24_message(jobs_data):
    """메시지 포맷"""
    header = f"🏢 오늘의 채용공고 ({datetime.now().strftime('%m월 %d일')})\n"
    header += "=" * 20 + "\n\n"
    
    category_icons = {"대기업": "🏆", "중견기업": "💼", "외국계": "🌏", "강소기업": "⭐"}
    sections = []
    
    for category, jobs in jobs_data.items():
        if not jobs: continue
        icon = category_icons.get(category, "📌")
        section = f"{icon} {category}\n"
        section += "\n\n".join(jobs[:3]) + "\n"  # 카테고리당 3개 제한
        sections.append(section)
    
    full_message = header + "\n".join(sections)
    return full_message[:1000]

def send_empty_message():
    """공고 없음 메시지 발송"""
    message = f"🏢 오늘의 채용공고 ({datetime.now().strftime('%m월 %d일')})\n"
    message += "=" * 20 + "\n\n"
    message += "오늘 등록된 타겟 채용 공고가 없습니다. 😊"
    
    try:
        sender = KakaoSender(os.environ['KAKAO_REST_API_KEY'], os.environ['KAKAO_REFRESH_TOKEN'])
        sender.send_message(message)
    except: pass

if __name__ == "__main__":
    main()
