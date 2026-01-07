#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 채용공고봇 - 하이브리드 방식
1차: requests (빠름)
2차: Selenium (실패 시)
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
    
    # 1차 시도: requests (빠르고 안정적)
    print("\n[1/3] 🔍 고용24 크롤링 중 (requests)...")
    try:
        from work24_api_crawler import Work24APICrawler
        
        crawler = Work24APICrawler()
        jobs_data = crawler.collect_jobs(max_jobs=15)
        
        total_count = sum(len(jobs) for jobs in jobs_data.values())
        print(f"✓ 크롤링 완료: {total_count}개 채용공고")
        
    except Exception as e:
        print(f"⚠️ requests 실패: {e}")
        print("  → Selenium으로 재시도...")
        
        # 2차 시도: Selenium (느리지만 확실함)
        try:
            from work24_stealth import Work24StealthCrawler
            
            crawler = Work24StealthCrawler()
            jobs_data = crawler.collect_jobs(max_jobs=15)
            
            total_count = sum(len(jobs) for jobs in jobs_data.values())
            print(f"✓ Selenium 크롤링 완료: {total_count}개")
            
        except Exception as e2:
            print(f"❌ Selenium도 실패: {e2}")
            send_error_message()
            return
    
    # 데이터 확인
    total_count = sum(len(jobs) for jobs in jobs_data.values())
    
    if total_count == 0:
        print("❌ 오늘 등록된 채용공고가 없습니다.")
        send_empty_message()
        return
    
    # 메시지 포맷팅
    print("\n[2/3] 📝 메시지 포맷팅 중...")
    message = format_work24_message(jobs_data)
    print(f"✓ 메시지 길이: {len(message)}자")
    
    # 카카오톡 발송
    print("\n[3/3] 📤 카카오톡 발송 중...")
    try:
        sender = KakaoSender(
            rest_api_key=os.environ['KAKAO_REST_API_KEY'],
            refresh_token=os.environ['KAKAO_REFRESH_TOKEN']
        )
        
        result = sender.send_message(message)
        
        if result:
            print("✓ 발송 성공!")
        else:
            print("❌ 발송 실패")
            
    except Exception as e:
        print(f"❌ 발송 오류: {e}")
        return
    
    print("\n" + "=" * 50)
    print("✅ 고용24 채용공고봇 완료!")
    print("=" * 50)

def format_work24_message(jobs_data):
    """메시지 포맷"""
    
    header = f"🏢 오늘의 채용공고 ({datetime.now().strftime('%m월 %d일')})\n"
    header += "=" * 30 + "\n\n"
    
    category_icons = {
        "대기업": "🏆",
        "중견기업": "💼",
        "외국계": "🌏",
        "강소기업": "⭐"
    }
    
    sections = []
    
    for category, jobs in jobs_data.items():
        if not jobs:
            continue
        
        icon = category_icons.get(category, "📌")
        section = f"{icon} {category}\n"
        section += "\n\n".join(jobs[:3]) + "\n"  # 카테고리당 3개까지
        sections.append(section)
    
    full_message = header + "\n".join(sections)
    
    return full_message[:1000]

def send_empty_message():
    """빈 메시지 발송"""
    
    message = f"🏢 오늘의 채용공고 ({datetime.now().strftime('%m월 %d일')})\n"
    message += "=" * 30 + "\n\n"
    message += "오늘 등록된 타겟 채용 공고가 없습니다.\n"
    message += "내일 다시 확인해드릴게요! 😊"
    
    try:
        sender = KakaoSender(
            rest_api_key=os.environ['KAKAO_REST_API_KEY'],
            refresh_token=os.environ['KAKAO_REFRESH_TOKEN']
        )
        sender.send_message(message)
    except:
        pass

def send_error_message():
    """에러 메시지 발송"""
    
    message = f"🏢 고용24 채용공고봇 ({datetime.now().strftime('%m월 %d일')})\n"
    message += "=" * 30 + "\n\n"
    message += "⚠️ 크롤링 중 오류가 발생했습니다.\n"
    message += "고용24 사이트 점검 또는 일시적 문제일 수 있습니다.\n"
    message += "내일 다시 시도합니다."
    
    try:
        sender = KakaoSender(
            rest_api_key=os.environ['KAKAO_REST_API_KEY'],
            refresh_token=os.environ['KAKAO_REFRESH_TOKEN']
        )
        sender.send_message(message)
    except:
        pass

if __name__ == "__main__":
    main()
