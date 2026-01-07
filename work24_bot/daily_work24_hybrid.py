#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 채용공고봇 - 카톡 분할 발송 버전
"""

import os
import time
from datetime import datetime
from kakao_sender import KakaoSender

def main():
    print("=" * 50)
    print("🏢 고용24 채용공고봇 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    jobs_data = None
    
    # [1] Selenium Stealth 크롤링
    print("\n[단계 1] 크롤러 실행 중...")
    try:
        from work24_stealth import Work24StealthCrawler
        crawler = Work24StealthCrawler()
        jobs_data = crawler.collect_jobs(max_jobs=20) # 넉넉하게 20개 검색
        
        total_count = sum(len(jobs) for jobs in jobs_data.values())
        print(f"✓ 크롤링 결과: 총 {total_count}개 유효 공고 발견")
        
    except Exception as e:
        print(f"❌ 크롤링 실패: {e}")
        return

    if total_count == 0:
        print("\n[결과] 오늘 조건에 맞는 공고가 없습니다.")
        return
    
    # [2] 카톡 발송 준비
    print("\n[단계 2] 카카오톡 분할 발송 시작...")
    try:
        api_key = os.environ.get('KAKAO_REST_API_KEY')
        refresh_token = os.environ.get('KAKAO_REFRESH_TOKEN')
        
        if not api_key or not refresh_token:
            print("❌ 오류: API 키가 없습니다.")
            return

        sender = KakaoSender(rest_api_key=api_key, refresh_token=refresh_token)
        
        # [3] 카테고리별 분리 전송 로직
        # 순서대로 보내기 위해 리스트 정의
        target_categories = ["대기업", "중견기업", "외국계", "강소기업"]
        
        sent_count = 0
        for category in target_categories:
            items = jobs_data.get(category, [])
            
            if items:
                # 해당 카테고리 전용 메시지 생성
                message = format_category_message(category, items)
                
                # 전송
                print(f"📤 [{category}] 발송 시도 ({len(items)}건)...")
                if sender.send_message(message):
                    print(f"   ✓ 전송 성공")
                    sent_count += 1
                else:
                    print(f"   ❌ 전송 실패")
                
                # 카톡 도배 방지 및 순서 보장을 위해 1초 대기
                time.sleep(1)
        
        print(f"\n✓ 총 {sent_count}번의 메시지를 보냈습니다.")
            
    except Exception as e:
        print(f"❌ 발송 중 에러: {e}")

    print("\n" + "=" * 50)

def format_category_message(category, items):
    """단일 카테고리용 메시지 포맷"""
    icons = {"대기업": "🏆", "중견기업": "💼", "외국계": "🌏", "강소기업": "⭐"}
    icon = icons.get(category, "📌")
    
    # 헤더
    msg = f"{icon} {category} 채용공고 ({datetime.now().strftime('%m/%d')})\n"
    msg += "=" * 25 + "\n\n"
    
    # 내용 (최대 5개까지만 보여줌, 너무 길면 잘림)
    msg += "\n\n".join(items[:5])
    
    # 5개 넘으면 "외 N건" 표시
    if len(items) > 5:
        msg += f"\n\n...외 {len(items)-5}건 더 있음"
        
    return msg

if __name__ == "__main__":
    main()
