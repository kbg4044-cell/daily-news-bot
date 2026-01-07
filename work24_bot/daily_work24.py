#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 채용공고봇 - 메인 실행
"""

import os
import sys
import json
from datetime import datetime
from work24_crawler import Work24Crawler
from kakao_sender import KakaoSender

def main():
    print("=" * 50)
    print("🏢 고용24 채용공고봇 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1단계: 고용24 크롤링
    print("\n[1/3] 🔍 고용24 크롤링 중...")
    try:
        crawler = Work24Crawler(headless=True)
        jobs_data = crawler.collect_jobs(max_jobs=15)
        
        total_count = sum(len(jobs) for jobs in jobs_data.values())
        print(f"✓ 크롤링 완료: {total_count}개 채용공고")
        
        if total_count == 0:
            print("❌ 오늘 등록된 채용공고가 없습니다.")
            # 빈 메시지 발송
            send_empty_message()
            return
            
    except Exception as e:
        print(f"❌ 크롤링 실패: {e}")
        return
    
    # 2단계: 메시지 포맷팅
    print("\n[2/3] 📝 메시지 포맷팅 중...")
    message = format_work24_message(jobs_data)
    print(f"✓ 메시지 길이: {len(message)}자")
    
    # 3단계: 카카오톡 발송
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
    
    # 결과 저장
    save_result(jobs_data)
    
    print("\n" + "=" * 50)
    print("✅ 고용24 채용공고봇 완료!")
    print("=" * 50)

def format_work24_message(jobs_data):
    """고용24 채용공고 메시지 포맷"""
    
    header = f"🏢 오늘의 채용공고 ({datetime.now().strftime('%m월 %d일')})\n"
    header += "=" * 30 + "\n\n"
    
    # 카테고리별 이모지
    category_icons = {
        "대기업": "🏆",
        "중견기업": "💼",
        "외국계": "🌏",
        "강소기업": "⭐"
    }
    
    sections = []
    has_data = False
    
    for category, jobs in jobs_data.items():
        if not jobs:
            continue
        
        has_data = True
        icon = category_icons.get(category, "📌")
        
        section = f"{icon} {category}\n"
        section += "\n\n".join(jobs) + "\n"
        
        sections.append(section)
    
    if not has_data:
        return f"{header}오늘 등록된 타겟 채용 공고가 없습니다."
    
    full_message = header + "\n".join(sections)
    
    # 1000자 제한
    if len(full_message) > 1000:
        # 각 카테고리당 2개씩만
        sections = []
        for category, jobs in jobs_data.items():
            if not jobs:
                continue
            
            icon = category_icons.get(category, "📌")
            section = f"{icon} {category}\n"
            section += "\n\n".join(jobs[:2]) + "\n"
            sections.append(section)
        
        full_message = header + "\n".join(sections)
    
    return full_message[:1000]

def send_empty_message():
    """채용공고가 없을 때 메시지"""
    
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
    except Exception as e:
        print(f"빈 메시지 발송 실패: {e}")

def save_result(jobs_data):
    """결과 저장"""
    
    result_data = {
        "bot_type": "work24",
        "timestamp": datetime.now().isoformat(),
        "jobs": jobs_data,
        "total_count": sum(len(jobs) for jobs in jobs_data.values())
    }
    
    filename = "work24_result.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
